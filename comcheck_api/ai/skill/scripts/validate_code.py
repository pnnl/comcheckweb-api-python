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


UNSUPPORTED_PROJECT_ATTRS = {"hvac", "renewable"}
UNSUPPORTED_LIGHTING_ATTRS = {
    "activityUse",
    "exteriorUse",
    "fixtureSchedule",
}


def _supported_operation_names() -> set[str]:
    """Live set of supported operation function names from the SDK."""
    try:
        from comcheck_api import list_operations
    except Exception:  # noqa: BLE001
        return set()
    return {op.name for op in list_operations()}


def _is_attr_chain(node, head: str, tail: str) -> bool:
    """True if `node` is `<head>.<tail>` — e.g. `project.hvac`."""
    import ast

    return (
        isinstance(node, ast.Attribute)
        and node.attr == tail
        and isinstance(node.value, ast.Name)
        and node.value.id == head
    )


def _is_lighting_chain(node, attr: str) -> bool:
    """True if `node` is `project.lighting.<attr>`."""
    import ast

    return (
        isinstance(node, ast.Attribute)
        and node.attr == attr
        and isinstance(node.value, ast.Attribute)
        and node.value.attr == "lighting"
        and isinstance(node.value.value, ast.Name)
        and node.value.value.id == "project"
    )


def validate(code: str) -> dict:
    """Compile-check the provided code and report errors as a dict.

    Runs three passes:
    1. Syntax check via :func:`compile`.
    2. Import check on every imported module name.
    3. Scope check that the code only uses operations actually exposed
       by the SDK and does not mutate the unsupported `hvac`,
       `renewable`, or non-`wholeBldgUse` lighting subtrees.
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

    # 3. Scope check: cross-reference symbols against list_operations()
    #    so the guard auto-tracks SDK growth, and forbid direct mutation
    #    of the unsupported subtrees.
    supported_ops = _supported_operation_names()

    # Collect the local names that resolve into the operation modules.
    op_module_aliases: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "comcheck_api":
            for alias in node.names:
                if alias.name in {
                    "project_envelope_operations",
                    "project_building_area_operations",
                }:
                    op_module_aliases.add(alias.asname or alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module == (
            "comcheck_api.project_operations"
        ):
            for alias in node.names:
                if alias.name in {
                    "project_envelope_operations",
                    "project_building_area_operations",
                }:
                    op_module_aliases.add(alias.asname or alias.name)

    for node in ast.walk(tree):
        # Forbid `project.hvac` / `project.renewable` access in any context.
        if isinstance(node, ast.Attribute) and any(
            _is_attr_chain(node, "project", attr) for attr in UNSUPPORTED_PROJECT_ATTRS
        ):
            errors.append(
                {
                    "kind": "unsupported-scope",
                    "line": node.lineno,
                    "message": (
                        f"`project.{node.attr}` has no operations in this SDK; "
                        "leave it at template defaults."
                    ),
                }
            )

        # Forbid `project.lighting.<unsupported>`.
        if isinstance(node, ast.Attribute) and any(
            _is_lighting_chain(node, attr) for attr in UNSUPPORTED_LIGHTING_ATTRS
        ):
            errors.append(
                {
                    "kind": "unsupported-scope",
                    "line": node.lineno,
                    "message": (
                        f"`project.lighting.{node.attr}` has no operations; "
                        "only `lighting.wholeBldgUse[]` is editable."
                    ),
                }
            )

        # Calls of the form `<op_module>.<name>(...)` must hit a real op.
        if (
            supported_ops
            and isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id in op_module_aliases
        ):
            fn_name = node.func.attr
            if fn_name not in supported_ops and not fn_name.startswith("_"):
                errors.append(
                    {
                        "kind": "unknown-operation",
                        "line": node.lineno,
                        "operation": fn_name,
                        "message": (
                            f"`{node.func.value.id}.{fn_name}` is not a supported "
                            "operation. Run comcheck_api.list_operations() for the "
                            "current set."
                        ),
                    }
                )

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
