"""Orchestration for ``comcheck-api setup-mcp``.

Detects installed AI clients, prompts, and writes the appropriate MCP
config entries. All JSON-mangling is delegated to ``clients.py``; this
module owns the user-facing flow only.

Note: the file is named ``setup.py`` because it implements the
``setup-mcp`` subcommand. Despite the name it has nothing to do with
the legacy Python ``setup.py`` packaging file — ``pyproject.toml`` is
the build config.
"""

from __future__ import annotations

import shutil
import sys

from comcheck_api.mcp import clients


def setup_mcp(
    server_name: str = "comcheck",
    *,
    dry_run: bool = False,
    force: bool = False,
    yes: bool = False,
    remove: bool = False,
) -> int:
    """Register (or unregister) ``comcheck-mcp`` with detected AI clients.

    Returns an exit code (0 on success, non-zero on failure).
    """
    if remove:
        return _remove(server_name, dry_run=dry_run, yes=yes)

    command = shutil.which("comcheck-mcp")
    if command is None:
        print("ERROR: 'comcheck-mcp' not found on PATH.")
        print("Install with: pip install comcheck_api[mcp]")
        return 1

    detected = clients.detect_installed()
    if not detected:
        print("No MCP-aware AI clients detected.")
        print("Install Claude Code, Claude Desktop, Cursor, Windsurf, or Zed first.")
        return 1

    print(f"Found {len(detected)} MCP-aware client(s):")
    for c in detected:
        print(f"  ✓ {c.name}  ({c.config_path})")
    print()

    failures = 0
    for client in detected:
        if not _confirm(f"Register {server_name} with {client.name}?", yes=yes):
            continue

        if clients.has_server(client, server_name) and not force:
            if not _confirm(
                f"  {server_name} is already registered. Overwrite?", yes=yes
            ):
                continue

        new_config = clients.add_server(client, server_name, command)

        if dry_run:
            print(f"  [dry-run] would write {client.config_path}")
            continue

        try:
            clients.write_config(client, new_config)
        except Exception as e:  # noqa: BLE001 — surface any IO/permission issue
            print(f"  ✗ failed: {e}")
            failures += 1
            continue

        print(f"  → wrote {client.config_path}")

    if failures:
        return 1
    print("\nDone. Restart your AI client(s) to activate the comcheck tools.")
    return 0


def _remove(server_name: str, *, dry_run: bool, yes: bool) -> int:
    detected = [
        c for c in clients.detect_installed() if clients.has_server(c, server_name)
    ]
    if not detected:
        print(f"No installed clients have '{server_name}' registered.")
        return 0

    for client in detected:
        if not _confirm(f"Remove {server_name} from {client.name}?", yes=yes):
            continue
        new_config = clients.remove_server(client, server_name)
        if dry_run:
            print(f"  [dry-run] would write {client.config_path}")
            continue
        clients.write_config(client, new_config)
        print(f"  → updated {client.config_path}")
    return 0


def _confirm(prompt: str, *, yes: bool) -> bool:
    if yes:
        print(f"{prompt} [Y/n] (auto-yes)")
        return True
    try:
        answer = input(f"{prompt} [Y/n] ").strip().lower()
    except EOFError:
        return False
    return answer in ("", "y", "yes")


if __name__ == "__main__":  # pragma: no cover — direct invocation helper
    sys.exit(setup_mcp())
