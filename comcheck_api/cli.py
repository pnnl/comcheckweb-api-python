"""``comcheck-api`` console-script entry point.

Subcommands:

* ``install-skill`` — install the bundled Skill so an AI coding agent
  picks it up. The Skill follows the open agent-skills standard
  (``SKILL.md`` + ``reference/`` + ``scripts/``), so the same folder
  works for both Claude Code and OpenAI Codex; only the install
  location differs:

  - Claude Code → ``.claude/skills/comcheck-api/`` (or
    ``~/.claude/skills/`` with ``--global``).
  - OpenAI Codex → ``.agents/skills/comcheck-api/`` (or
    ``~/.agents/skills/`` with ``--global``). Codex scans
    ``.agents/skills`` from the working directory up to the repo root.

  By default both are installed. Pass ``--claude`` to install only the
  Claude Code Skill, or ``--codex`` to install only the Codex Skill.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from comcheck_api import ai

# (agent label, skills dir) for each supported target.
_TARGETS = {
    "claude": ("Claude", ".claude"),
    "codex": ("Codex", ".agents"),
}


def _install_one(
    src: Path, base_dir: Path, agent_dir: str, force: bool, dry_run: bool
) -> tuple[bool, Path]:
    """Install the Skill for one agent. Returns (installed, target)."""
    target_root = base_dir / agent_dir / "skills" / "comcheck-api"

    if dry_run:
        print(f"[dry-run] would copy {src} → {target_root}")
        return True, target_root

    if target_root.exists() and not force:
        print(f"{target_root} already exists. Re-run with --force to overwrite.")
        return False, target_root

    if target_root.exists():
        shutil.rmtree(target_root)
    target_root.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, target_root)
    print(f"Installed Skill into {target_root}")
    return True, target_root


def _cmd_install_skill(args: argparse.Namespace) -> int:
    if args.global_install:
        base_dir = Path.home()
    else:
        base_dir = Path(args.path).resolve()
        if not base_dir.is_dir():
            print(f"ERROR: {base_dir} is not a directory.")
            return 1

    # No agent flag → install both. Otherwise install only the
    # selected agents.
    if args.claude or args.codex:
        agents = [k for k in _TARGETS if getattr(args, k)]
    else:
        agents = list(_TARGETS)

    src = ai.skill_root()
    any_installed = False
    for key in agents:
        label, agent_dir = _TARGETS[key]
        installed, _ = _install_one(src, base_dir, agent_dir, args.force, args.dry_run)
        if installed and not args.dry_run:
            print(f"Restart {label} to pick up the new Skill.")
        any_installed = any_installed or installed

    return 0 if any_installed else 1


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--dry-run", action="store_true", help="Show actions without applying"
    )
    common.add_argument(
        "--force", action="store_true", help="Overwrite existing files/configs"
    )

    parser = argparse.ArgumentParser(prog="comcheck-api")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_skill = sub.add_parser(
        "install-skill",
        parents=[common],
        help="Install the Skill for Claude Code and/or Codex (both by default)",
    )
    p_skill.add_argument(
        "path", nargs="?", default=".", help="Project directory (default: cwd)"
    )
    p_skill.add_argument(
        "--global",
        dest="global_install",
        action="store_true",
        help="Install into the user-global skills dir (~/.claude/skills/ "
        "and/or ~/.agents/skills/) instead of project-level",
    )
    p_skill.add_argument(
        "--claude",
        action="store_true",
        help="Install only the Claude Code Skill (.claude/skills/)",
    )
    p_skill.add_argument(
        "--codex",
        action="store_true",
        help="Install only the Codex Skill (.agents/skills/)",
    )
    p_skill.set_defaults(func=_cmd_install_skill)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
