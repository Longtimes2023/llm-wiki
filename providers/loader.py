"""Provider resolution: 3-tier priority. Called at ingest time, not module load.

Priority (lowest → highest):
  1. ANTHROPIC_* in main .env (bootstrap fallback)
  2. providers/.active sentinel (sticky default, set via /provider command)
  3. Override arg passed by caller (CLI flag --provider, or @provider in Telegram msg)
"""
from pathlib import Path
from typing import Optional
import os

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parent.parent
PROVIDERS_DIR = ROOT / "providers"
SENTINEL = PROVIDERS_DIR / ".active"


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
    if not base["auth_token"]:
        raise RuntimeError(
            f"No ANTHROPIC_AUTH_TOKEN in profile {base['name']!r}. "
            f"Check providers/{base['name']}.env or main .env"
        )
    return base
