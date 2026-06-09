"""AI-facing surface for the comcheck_api package.

Ships the canonical Skill folder under ``comcheck_api/ai/skill/``
(SKILL.md + reference docs + examples + scripts). Use
:func:`skill_root` to get the on-disk path to the bundled folder —
useful for installing it into ``<project>/.claude/skills/`` or
``~/.claude/skills/``.

Introspection and validation helpers live on the SDK itself
(``comcheck_api.list_operations``, ``comcheck_api.lookup_type``,
``comcheck_api.validate_project``).
"""

from __future__ import annotations

from importlib.resources import as_file, files
from pathlib import Path


def skill_root() -> Path:
    """Return the on-disk path to the bundled Skill folder.

    Uses ``importlib.resources`` so the path resolves correctly
    whether the package is installed normally or zip-imported.
    """
    with as_file(files("comcheck_api.ai.skill")) as p:
        return Path(p)


__all__ = ["skill_root"]
