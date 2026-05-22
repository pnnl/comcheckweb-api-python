"""``comcheck-api`` console-script entry point.

Subcommands:

* ``setup-mcp`` — register/unregister the local MCP server with
  detected AI clients.
* ``install-skill`` — copy the bundled Skill folder into
  ``~/.claude/skills/comcheck-api/``.
* ``init`` — drop a ``CLAUDE.md`` and ``.cursor/rules/comcheck.mdc``
  into the user's project directory.
* ``setup-ai`` — one-shot: runs all three with confirmation prompts.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from comcheck_api.ai import content


def _cmd_setup_mcp(args: argparse.Namespace) -> int:
    from comcheck_api.mcp.setup import setup_mcp

    return setup_mcp(
        dry_run=args.dry_run,
        force=args.force,
        yes=args.yes,
        remove=args.remove,
    )


def _cmd_install_skill(args: argparse.Namespace) -> int:
    target_root = Path.home() / ".claude" / "skills" / "comcheck-api"
    if target_root.exists() and not args.force:
        print(f"{target_root} already exists. Re-run with --force to overwrite.")
        return 1

    src = content.skill_root()
    if args.dry_run:
        print(f"[dry-run] would copy {src} → {target_root}")
        return 0

    if target_root.exists():
        shutil.rmtree(target_root)
    shutil.copytree(src, target_root)
    print(f"Installed Skill into {target_root}")
    print("Restart Claude to pick up the new Skill.")
    return 0


def _cmd_init(args: argparse.Namespace) -> int:
    project_dir = Path(args.path).resolve()
    if not project_dir.is_dir():
        print(f"ERROR: {project_dir} is not a directory.")
        return 1

    claude_md = project_dir / "CLAUDE.md"
    cursor_rule = project_dir / ".cursor" / "rules" / "comcheck.mdc"

    if claude_md.exists() and not args.force:
        print(f"{claude_md} exists. Re-run with --force to overwrite.")
        return 1
    if cursor_rule.exists() and not args.force:
        print(f"{cursor_rule} exists. Re-run with --force to overwrite.")
        return 1

    body = content.read_skill_body_only()
    cursor_frontmatter = (
        "---\n"
        "description: Conventions for the comcheck_api Python client\n"
        'globs: ["**/*.py"]\n'
        "alwaysApply: true\n"
        "---\n\n"
    )

    if args.dry_run:
        print(f"[dry-run] would write {claude_md}")
        print(f"[dry-run] would write {cursor_rule}")
        return 0

    claude_md.write_text(body, encoding="utf-8")
    print(f"Wrote {claude_md}")

    cursor_rule.parent.mkdir(parents=True, exist_ok=True)
    cursor_rule.write_text(cursor_frontmatter + body, encoding="utf-8")
    print(f"Wrote {cursor_rule}")
    return 0


def _cmd_setup_ai(args: argparse.Namespace) -> int:
    print("Running install-skill, setup-mcp, and init in sequence.\n")
    rc = _cmd_install_skill(args)
    if rc and not args.continue_on_error:
        return rc
    print()
    rc = _cmd_setup_mcp(args)
    if rc and not args.continue_on_error:
        return rc
    print()
    return _cmd_init(args)


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--dry-run", action="store_true", help="Show actions without applying"
    )
    common.add_argument(
        "--force", action="store_true", help="Overwrite existing files/configs"
    )
    common.add_argument(
        "--yes", "-y", action="store_true", help="Don't prompt; assume yes"
    )

    parser = argparse.ArgumentParser(prog="comcheck-api")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_mcp = sub.add_parser(
        "setup-mcp",
        parents=[common],
        help="Register comcheck-mcp with AI clients",
    )
    p_mcp.add_argument(
        "--remove", action="store_true", help="Unregister instead of register"
    )
    p_mcp.set_defaults(func=_cmd_setup_mcp)

    p_skill = sub.add_parser(
        "install-skill",
        parents=[common],
        help="Install the Skill into ~/.claude/skills/",
    )
    p_skill.set_defaults(func=_cmd_install_skill)

    p_init = sub.add_parser(
        "init",
        parents=[common],
        help="Drop CLAUDE.md and .cursor/rules/comcheck.mdc into the current project",
    )
    p_init.add_argument(
        "path", nargs="?", default=".", help="Project directory (default: cwd)"
    )
    p_init.set_defaults(func=_cmd_init)

    p_all = sub.add_parser(
        "setup-ai",
        parents=[common],
        help="Run install-skill, setup-mcp, and init in sequence",
    )
    p_all.add_argument(
        "path", nargs="?", default=".", help="Project directory (default: cwd)"
    )
    p_all.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue if a step fails",
    )
    p_all.add_argument(
        "--remove", action="store_true", help="Pass through to setup-mcp"
    )
    p_all.set_defaults(func=_cmd_setup_ai)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
