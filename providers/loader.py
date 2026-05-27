"""Provider resolution: 3-tier priority. Called at ingest time, not module load.

Priority (lowest → highest):
  1. ANTHROPIC_* in main .env (bootstrap fallback)
  2. providers/.active sentinel (sticky default, set via /provider command)
  3. Override arg passed by caller (CLI flag --provider, or @provider in Telegram msg)

Chat (Q&A) uses an independent sentinel `.active_chat` resolved by
get_active_chat(), so the cheap chat model can be switched without touching
the heavy ingest model. resolve() is shared — caller picks which active to feed in.
"""
from pathlib import Path
from typing import Optional
import os

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parent.parent
PROVIDERS_DIR = ROOT / "providers"
SENTINEL = PROVIDERS_DIR / ".active"
SENTINEL_CHAT = PROVIDERS_DIR / ".active_chat"
SENTINEL_FALLBACK = PROVIDERS_DIR / ".fallback_chain"


def list_providers() -> list[str]:
    if not PROVIDERS_DIR.exists():
        return []
    return sorted(
        p.stem for p in PROVIDERS_DIR.glob("*.env")
        if not p.name.endswith(".env.example") and p.name != ".active"
    )


def get_active() -> Optional[str]:
    if SENTINEL.exists():
        name = SENTINEL.read_text(encoding="utf-8").strip()
        if name:
            return name
    return os.getenv("ACTIVE_PROVIDER", "").strip() or None


def set_active(name: str) -> None:
    available = list_providers()
    if name not in available:
        raise ValueError(
            f"Unknown provider: {name!r}. Available: {available or '(none)'}"
        )
    PROVIDERS_DIR.mkdir(exist_ok=True)
    SENTINEL.write_text(name + "\n", encoding="utf-8")


def get_active_chat() -> Optional[str]:
    """Sticky chat (Q&A) provider. Falls back to CHAT_PROVIDER env var,
    then None — caller should treat None as "use ingest provider"."""
    if SENTINEL_CHAT.exists():
        name = SENTINEL_CHAT.read_text(encoding="utf-8").strip()
        if name:
            return name
    return os.getenv("CHAT_PROVIDER", "").strip() or None


def set_active_chat(name: str) -> None:
    available = list_providers()
    if name not in available:
        raise ValueError(
            f"Unknown provider: {name!r}. Available: {available or '(none)'}"
        )
    PROVIDERS_DIR.mkdir(exist_ok=True)
    SENTINEL_CHAT.write_text(name + "\n", encoding="utf-8")


def get_fallback_chain() -> list[str]:
    """Comma-separated provider names in providers/.fallback_chain.
    Used by raw-watcher.sh: attempt 1 uses .active, attempts 2..N walk this chain.
    Returns [] if sentinel missing or empty — caller treats as "no fallback"."""
    if not SENTINEL_FALLBACK.exists():
        return []
    raw = SENTINEL_FALLBACK.read_text(encoding="utf-8").strip()
    if not raw:
        return []
    return [p.strip() for p in raw.split(",") if p.strip()]


def set_fallback_chain(names: list[str]) -> None:
    """Validate every name exists in providers/*.env, then write the chain."""
    available = list_providers()
    bad = [n for n in names if n not in available]
    if bad:
        raise ValueError(
            f"Unknown provider(s) in chain: {bad}. Available: {available or '(none)'}"
        )
    PROVIDERS_DIR.mkdir(exist_ok=True)
    SENTINEL_FALLBACK.write_text(",".join(names) + "\n", encoding="utf-8")


def resolve(override: Optional[str] = None) -> dict:
    """Returns dict with name, model, base_url, auth_token, input_price_per_m, output_price_per_m.

    Raises FileNotFoundError if a named provider profile is missing.
    Raises RuntimeError if the resolved profile has no auth token.
    """
    name = (override or get_active() or "").strip() or None
    base = {
        "name": name or "default",
        "model": os.getenv("MODEL", "claude-sonnet-4-20250514"),
        "base_url": os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com"),
        "auth_token": os.getenv("ANTHROPIC_AUTH_TOKEN", ""),
        "input_price_per_m": 0.0,
        "output_price_per_m": 0.0,
    }
    base["extra_env"] = {}
    if name:
        profile = PROVIDERS_DIR / f"{name}.env"
        if not profile.exists():
            raise FileNotFoundError(
                f"Provider profile not found: {profile}. "
                f"Available: {list_providers() or '(none)'}"
            )
        vals = dotenv_values(profile)
        base.update({
            "name": name,
            "model": vals.get("MODEL") or base["model"],
            "base_url": vals.get("ANTHROPIC_BASE_URL") or base["base_url"],
            "auth_token": vals.get("ANTHROPIC_AUTH_TOKEN") or base["auth_token"],
            "input_price_per_m": float(vals.get("INPUT_PRICE_PER_M") or 0),
            "output_price_per_m": float(vals.get("OUTPUT_PRICE_PER_M") or 0),
        })
        # Forward Claude SDK model-mapping vars (lets relays like Mimo route
        # `claude-sonnet-4-6` requests to their own underlying model server-side
        # while passing client-side model whitelist validation).
        base["extra_env"] = {
            k: vals[k]
            for k in (
                "ANTHROPIC_DEFAULT_HAIKU_MODEL",
                "ANTHROPIC_DEFAULT_SONNET_MODEL",
                "ANTHROPIC_DEFAULT_OPUS_MODEL",
            )
            if vals.get(k)
        }
    if not base["auth_token"]:
        raise RuntimeError(
            f"No ANTHROPIC_AUTH_TOKEN in profile {base['name']!r}. "
            f"Check providers/{base['name']}.env or main .env"
        )
    return base
