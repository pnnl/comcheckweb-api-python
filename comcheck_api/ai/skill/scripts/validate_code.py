"""Validate generated Python that uses comcheck_api against a mocked client.

Usage:
    python -m comcheck_api.ai.skill.scripts.validate_code <path-to-script>
    cat script.py | python -m comcheck_api.ai.skill.scripts.validate_code -

Runs the user's code in a subprocess with the network layer mocked.
Prints structured errors to stdout and exits non-zero if validation
fails.

This script is invoked by the Skill so Claude can run it via shell
tools to self-check generated code.

Security: the calling layer is responsible for sandboxing — running
this script from an untrusted source still executes arbitrary Python.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def _read_input(arg: str) -> str:
    if arg == "-":
        return sys.stdin.read()
    return Path(arg).read_text()


def validate(code: str) -> dict:
    """Compile-check the provided code and report errors as a dict.

    This is intentionally limited to syntax + import checks for now.
    Runtime validation (executing the code against a mocked SDK client)
    is added in a follow-up phase, where the sandbox is hardened.
    """
    errors: list[dict] = []

    # 1. Syntax check via compile().
    try:
        compile(code, "<generated>", "exec")
    except SyntaxError as e:
        errors.append(
            {
                "kind": "syntax",
                "line": e.lineno,
                "col": e.offset,
                "message": e.msg,
            }
        )
        return {"ok": False, "errors": errors}

    # 2. Import check: parse import statements and try importing each
    #    module name without executing the user's code.
    import ast

    tree = ast.parse(code)
    for node in ast.walk(tree):
        modules: list[str] = []
        if isinstance(node, ast.Import):
            modules = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules = [node.module]
        for mod in modules:
            try:
                __import__(mod)
            except ImportError as e:
                errors.append({"kind": "import", "module": mod, "message": str(e)})

    return {"ok": not errors, "errors": errors}


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_code.py <path|->", file=sys.stderr)
        return 2
    code = _read_input(sys.argv[1])
    result = validate(code)
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
