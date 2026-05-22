"""Per-client MCP config-file logic.

Each supported AI client (Claude Code, Claude Desktop, Cursor, Windsurf,
Zed) stores its MCP server registry in a slightly different file in a
slightly different shape. This module isolates those details so the
orchestration in ``setup.py`` can stay agnostic.

Pure functions over paths and dicts — easy to unit-test without
mocking ``input()``.
"""

from __future__ import annotations

import json
import platform
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MCPClient:
    """Describes how one AI client stores its MCP config."""

    name: str
    config_path: Path
    config_section: str  # JSON key under which servers are registered


def _claude_desktop_path() -> Path:
    home = Path.home()
    system = platform.system()
    if system == "Darwin":
        return (
            home
            / "Library"
            / "Application Support"
            / "Claude"
            / "claude_desktop_config.json"
        )
    if system == "Windows":
        return home / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
    return home / ".config" / "Claude" / "claude_desktop_config.json"


def all_clients() -> list[MCPClient]:
    """Return every supported client with its config-file path."""
    home = Path.home()
    return [
        MCPClient(
            name="Claude Code",
            config_path=home / ".claude.json",
            config_section="mcpServers",
        ),
        MCPClient(
            name="Claude Desktop",
            config_path=_claude_desktop_path(),
            config_section="mcpServers",
        ),
        MCPClient(
            name="Cursor",
            config_path=home / ".cursor" / "mcp.json",
            config_section="mcpServers",
        ),
        MCPClient(
            name="Windsurf",
            config_path=home / ".codeium" / "windsurf" / "mcp_config.json",
            config_section="mcpServers",
        ),
        MCPClient(
            name="Zed",
            config_path=home / ".config" / "zed" / "settings.json",
            config_section="context_servers",
        ),
    ]


def detect_installed() -> list[MCPClient]:
    """Filter to clients whose config file already exists."""
    return [c for c in all_clients() if c.config_path.exists()]


def read_config(client: MCPClient) -> dict:
    """Load existing config, or return empty dict if file is missing."""
    if not client.config_path.exists():
        return {}
    try:
        return json.loads(client.config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"{client.config_path} is not valid JSON: {e}") from e


def write_config(client: MCPClient, config: dict) -> None:
    """Write config back, creating parent directories if needed."""
    client.config_path.parent.mkdir(parents=True, exist_ok=True)
    client.config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")


def add_server(client: MCPClient, name: str, command: str) -> dict:
    """Return a new config dict with ``name`` registered."""
    config = read_config(client)
    section = config.setdefault(client.config_section, {})
    section[name] = {"command": command}
    return config


def remove_server(client: MCPClient, name: str) -> dict:
    """Return a new config dict with ``name`` removed (no-op if absent)."""
    config = read_config(client)
    section = config.get(client.config_section, {})
    section.pop(name, None)
    return config


def has_server(client: MCPClient, name: str) -> bool:
    """Return True if ``name`` is registered with this client."""
    config = read_config(client)
    return name in config.get(client.config_section, {})
