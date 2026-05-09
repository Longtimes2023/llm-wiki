"""One-shot: strip stray block-list lines that follow an inline `sources: [...]`.

Quartz's YAML parser rejects the hybrid pattern produced when the wiki-skill
template (block list) and schema (inline list) disagreed:

    sources: [a, b]
      - a.md
      - b.md

We keep the inline line (matches schema) and drop the stray `  - …` lines
that immediately follow it inside the frontmatter block.
"""
import re
import pathlib

ROOT = pathlib.Path("ai-wiki")
HYBRID = re.compile(r"^sources:\s*\[")
STRAY = re.compile(r"^\s+-\s.*\.md\s*$")

for p in ROOT.rglob("*.md"):
    lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
    if not lines or lines[0].rstrip() != "---":
        continue

    out, i, in_fm, changed = [], 0, False, False
    while i < len(lines):
        line = lines[i]
        if i == 0:
            in_fm = True
            out.append(line)
            i += 1
            continue
        if in_fm and line.rstrip() == "---":
            in_fm = False
        out.append(line)
        if in_fm and HYBRID.match(line):
            j = i + 1
            while j < len(lines) and STRAY.match(lines[j]):
                changed = True
                j += 1
            i = j
            continue
        i += 1

    if changed:
        p.write_text("".join(out), encoding="utf-8")
        print("fixed", p)
