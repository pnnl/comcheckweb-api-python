"""Build pipeline for AI-facing artifacts.

Reads the canonical Skill content under ``comcheck_api/ai/skill/`` and
emits the derived ``CLAUDE.md`` files used by Claude Code:

* ``CLAUDE.md`` (repo root)            — auto-loads in Claude Code sessions
* ``comcheck_api/ai/CLAUDE.md``        — in-wheel copy

Run with: ``python scripts/build_ai_assets.py``
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO_ROOT / "comcheck_api" / "ai" / "skill"


def strip_frontmatter(text: str) -> str:
    """Remove a leading YAML frontmatter block, if present."""
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    if end == -1:
        return text
    return text[end + 4 :].lstrip("\n")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"  wrote {path.relative_to(REPO_ROOT)}")


def build_claude_md() -> str:
    """Return the body of SKILL.md without frontmatter."""
    return strip_frontmatter(read(SKILL_DIR / "SKILL.md"))


def main() -> int:
    if not SKILL_DIR.exists():
        print(f"ERROR: Skill folder missing at {SKILL_DIR}", file=sys.stderr)
        return 1

    print("Building AI assets from", SKILL_DIR.relative_to(REPO_ROOT))

    claude_md = build_claude_md()

    write(REPO_ROOT / "CLAUDE.md", claude_md)
    write(REPO_ROOT / "comcheck_api" / "ai" / "CLAUDE.md", claude_md)

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
