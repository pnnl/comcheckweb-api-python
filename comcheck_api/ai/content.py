"""Runtime loader for Skill content bundled in the wheel.

Consumers (an external LangGraph agent, the ``comcheck-api init``
command, etc.) call these helpers to read SKILL.md, reference docs,
and examples without hard-coding paths. Uses ``importlib.resources``
so the files are located correctly whether the package is installed
normally or zip-imported.
"""

from __future__ import annotations

from importlib.resources import as_file, files
from pathlib import Path

_SKILL_PACKAGE = "comcheck_api.ai.skill"


def skill_root() -> Path:
    """Return the on-disk path to the bundled Skill folder.

    Useful for callers that want to copy the whole folder somewhere
    (e.g., ``~/.claude/skills/comcheck-api/``).
    """
    with as_file(files(_SKILL_PACKAGE)) as p:
        return Path(p)


def read_skill_body() -> str:
    """Return the full text of SKILL.md (frontmatter + body)."""
    return (files(_SKILL_PACKAGE) / "SKILL.md").read_text(encoding="utf-8")


def read_skill_body_only() -> str:
    """Return SKILL.md with the YAML frontmatter stripped.

    Useful when feeding the Skill body into a LangGraph system prompt
    or any other surface that shouldn't include Skill-specific
    frontmatter.
    """
    text = read_skill_body()
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4 :].lstrip("\n")
    return text


def read_reference(name: str) -> str:
    """Return the contents of ``reference/<name>``.

    ``name`` may be ``"types.md"`` or just ``"types"`` — the ``.md``
    suffix is added if missing.
    """
    if not name.endswith(".md"):
        name = f"{name}.md"
    return (files(_SKILL_PACKAGE) / "reference" / name).read_text(encoding="utf-8")


def read_example(name: str) -> str:
    """Return the contents of ``examples/<name>``.

    ``name`` may be ``"small_office.py"`` or just ``"small_office"``.
    """
    if not name.endswith(".py"):
        name = f"{name}.py"
    return (files(_SKILL_PACKAGE) / "examples" / name).read_text(encoding="utf-8")


def list_references() -> list[str]:
    """Return the names of all reference Markdown files."""
    ref_dir = files(_SKILL_PACKAGE) / "reference"
    return sorted(p.name for p in ref_dir.iterdir() if p.name.endswith(".md"))


def list_examples() -> list[str]:
    """Return the names of all example Python files."""
    ex_dir = files(_SKILL_PACKAGE) / "examples"
    return sorted(p.name for p in ex_dir.iterdir() if p.name.endswith(".py"))
