"""``comcheck-api`` console-script entry point.

Subcommands:

* ``install-skill`` — copy the bundled Skill folder into a project's
  ``.claude/skills/comcheck-api/`` directory (or ``~/.claude/skills/``
  when ``--global`` is passed).
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from comcheck_api import ai


def _cmd_install_skill(args: argparse.Namespace) -> int:
    if args.global_install:
        target_root = Path.home() / ".claude" / "skills" / "comcheck-api"
    else:
        project_dir = Path(args.path).resolve()
        if not project_dir.is_dir():
            print(f"ERROR: {project_dir} is not a directory.")
            return 1
        target_root = project_dir / ".claude" / "skills" / "comcheck-api"

    if target_root.exists() and not args.force:
        print(f"{target_root} already exists. Re-run with --force to overwrite.")
        return 1

    src = ai.skill_root()
    if args.dry_run:
        print(f"[dry-run] would copy {src} → {target_root}")
        return 0

    if target_root.exists():
        shutil.rmtree(target_root)
    target_root.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, target_root)
    print(f"Installed Skill into {target_root}")
    print("Restart Claude to pick up the new Skill.")
    return 0


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
        help="Install the Skill into <project>/.claude/skills/ (or ~/.claude/skills/ with --global)",
    )
    p_skill.add_argument(
        "path", nargs="?", default=".", help="Project directory (default: cwd)"
    )
    p_skill.add_argument(
        "--global",
        dest="global_install",
        action="store_true",
        help="Install into ~/.claude/skills/ instead of project-level",
    )
    p_skill.set_defaults(func=_cmd_install_skill)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
