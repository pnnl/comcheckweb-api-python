"""Build pipeline for AI-facing artifacts.

Reads the canonical Skill content under ``comcheck_api/ai/skill/`` and
emits derived files used by various AI surfaces:

* ``docs_site/llms.txt``               — TOC for web-grounded AI clients
* ``docs_site/llms-full.txt``          — concatenated full docs
* ``CLAUDE.md`` (repo root)            — auto-loads in Claude Code sessions
* ``comcheck_api/ai/CLAUDE.md``        — in-wheel copy
* ``.cursor/rules/comcheck.mdc``       — auto-loads in Cursor sessions

Run with: ``python scripts/build_ai_assets.py``
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO_ROOT / "comcheck_api" / "ai" / "skill"
DOCS_SITE = REPO_ROOT / "docs_site"
EXAMPLES_DIR = REPO_ROOT / "examples"

CURSOR_FRONTMATTER = (
    "---\n"
    "description: Conventions for the comcheck_api Python client\n"
    'globs: ["**/*.py"]\n'
    "alwaysApply: true\n"
    "---\n\n"
)


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


def build_llms_txt() -> str:
    """Return a short TOC pointing at the docs_site Markdown files."""
    parts = [
        "# COMcheck Web API – Python Client",
        "",
        "> Type-safe Python client for the PNNL COMcheck Web API. Build COMcheck",
        "> project JSON, run compliance simulations, and parse results.",
        "",
        "Targets Python 3.12+. Core entry point: `COMcheckClient`. Project",
        "construction uses functional operation modules",
        "(`project_building_area_operations`, `project_envelope_operations`).",
        "All inputs/outputs are Pydantic models.",
        "",
        "## Docs",
        "",
    ]

    if DOCS_SITE.exists():
        for md in sorted(DOCS_SITE.rglob("*.md")):
            if md.name in {"llms.txt", "llms-full.txt"}:
                continue
            rel = md.relative_to(DOCS_SITE)
            parts.append(f"- [{rel}]({rel})")

    parts.append("")
    parts.append("## Examples")
    parts.append("")
    if EXAMPLES_DIR.exists():
        for py in sorted(EXAMPLES_DIR.rglob("*.py")):
            rel = py.relative_to(REPO_ROOT)
            parts.append(f"- [{rel}]({rel})")
    parts.append("")
    return "\n".join(parts)


def build_llms_full_txt() -> str:
    """Concatenate Skill + docs_site + examples into one big Markdown file."""
    parts: list[str] = []

    # 1. Skill cheat sheet at the top.
    parts.append("# COMcheck API — Compact Reference\n\n")
    parts.append("## Skill body\n\n")
    parts.append(strip_frontmatter(read(SKILL_DIR / "SKILL.md")))
    parts.append("\n\n")

    ref_dir = SKILL_DIR / "reference"
    if ref_dir.exists():
        for md in sorted(ref_dir.glob("*.md")):
            parts.append(f"\n\n---\n\n## reference/{md.name}\n\n")
            parts.append(read(md))

    # 2. Public docs_site (if present).
    if DOCS_SITE.exists():
        for md in sorted(DOCS_SITE.rglob("*.md")):
            if md.name in {"llms.txt", "llms-full.txt"}:
                continue
            rel = md.relative_to(DOCS_SITE)
            parts.append(f"\n\n---\n\n## docs_site/{rel}\n\n")
            parts.append(read(md))

    # 3. Bundled Skill examples.
    ex_dir = SKILL_DIR / "examples"
    if ex_dir.exists():
        for py in sorted(ex_dir.glob("*.py")):
            parts.append(f"\n\n---\n\n## skill/examples/{py.name}\n\n```python\n")
            parts.append(read(py))
            parts.append("\n```\n")

    return "".join(parts)


def main() -> int:
    if not SKILL_DIR.exists():
        print(f"ERROR: Skill folder missing at {SKILL_DIR}", file=sys.stderr)
        return 1

    print("Building AI assets from", SKILL_DIR.relative_to(REPO_ROOT))

    claude_md = build_claude_md()

    write(REPO_ROOT / "CLAUDE.md", claude_md)
    write(REPO_ROOT / "comcheck_api" / "ai" / "CLAUDE.md", claude_md)
    write(
        REPO_ROOT / ".cursor" / "rules" / "comcheck.mdc", CURSOR_FRONTMATTER + claude_md
    )

    write(DOCS_SITE / "llms.txt", build_llms_txt())
    write(DOCS_SITE / "llms-full.txt", build_llms_full_txt())

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
