"""Validation tools: lint generated code, schema-validate project JSON."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path
from typing import Any

import pydantic

from comcheck_api.ai.skill.scripts import validate_code as _static
from comcheck_api.types.core_types import ComBuilding

# --------------------------------------------------------------------------
# validate_code — static syntax/import check + optional sandboxed run.
# --------------------------------------------------------------------------


_SANDBOX_PRELUDE = textwrap.dedent("""
    # Sandbox prelude: stub network access before user code runs.
    import sys
    import socket

    class _Blocked(socket.socket):
        def __init__(self, *a, **kw):
            raise RuntimeError("Network access blocked in sandbox")

    socket.socket = _Blocked  # type: ignore[misc,assignment]

    # Patch the comcheck SDK's HTTP layer with a no-op mock.
    try:
        import comcheck_api.api.api_services as _svc

        class _MockApiService:
            def __init__(self, *a, **kw): pass
            def get_project(self, *a, **kw): return {"data": {}}
            def get_project_list(self, *a, **kw): return {"data": []}
            def update_project(self, *a, **kw): return {"data": {}}
            def start_run_simulation(self, *a, **kw):
                from comcheck_api.types.api_types import RunSimulationResponse
                return RunSimulationResponse(data={"sessionId": "MOCK"})  # type: ignore[arg-type]
            def get_simulation_status(self, *a, **kw):
                from comcheck_api.types.api_types import SimulationStatusResponse
                return SimulationStatusResponse(
                    data={"sessionId": "MOCK", "status": "complete"}  # type: ignore[arg-type]
                )
            def get_simulation_result(self, *a, **kw):
                from comcheck_api.types.api_types import SimulationResultResponse
                return SimulationResultResponse(
                    data={
                        "sessionId": "MOCK",
                        "performanceRating": 0.0,
                        "energyCreditPerformanceRating": 0.0,
                        "proposedBpf": 0.0,
                        "baselineBpf": 0.0,
                    }  # type: ignore[arg-type]
                )
            def close(self): pass

        _svc.COMCheckApiService = _MockApiService
    except Exception:
        pass
    """)


def validate_code(
    code: str, *, run: bool = False, timeout: float = 5.0
) -> dict[str, Any]:
    """Compile-check + import-check the provided Python.

    Args:
        code: The Python source to validate.
        run: If True, also execute the code in a sandboxed subprocess
            (network blocked, COMcheck client mocked). Default False —
            static checks only.
        timeout: Subprocess timeout in seconds when ``run`` is True.

    Returns ``{"ok": bool, "errors": list[dict]}``. Each error dict has
    a ``kind`` ("syntax", "import", "runtime", or "timeout") and a
    ``message``; syntax errors include ``line`` and ``col``; runtime
    errors include ``traceback``.
    """
    # 1. Static checks first — fast and don't require subprocess.
    static = _static.validate(code)
    if not static["ok"]:
        return static
    if not run:
        return static

    # 2. Sandboxed runtime check.
    with tempfile.TemporaryDirectory() as tmp:
        script_path = Path(tmp) / "user_code.py"
        script_path.write_text(_SANDBOX_PRELUDE + "\n\n" + code, encoding="utf-8")

        try:
            proc = subprocess.run(  # noqa: S603
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return {
                "ok": False,
                "errors": [
                    {
                        "kind": "timeout",
                        "message": f"Execution exceeded {timeout}s timeout",
                    }
                ],
            }

    if proc.returncode == 0:
        return {"ok": True, "errors": [], "stdout": proc.stdout}

    return {
        "ok": False,
        "errors": [
            {
                "kind": "runtime",
                "message": (proc.stderr.strip().splitlines() or [""])[-1],
                "traceback": proc.stderr,
            }
        ],
    }


# --------------------------------------------------------------------------
# dry_run_project — validate project JSON against the SDK's Pydantic models.
# --------------------------------------------------------------------------


def dry_run_project(project_json: dict[str, Any]) -> dict[str, Any]:
    """Validate ``project_json`` against the ``ComBuilding`` Pydantic model.

    Returns ``{"ok": True}`` if the data parses cleanly, otherwise
    ``{"ok": False, "errors": [{"loc": "...", "msg": "..."}, ...]}``.
    No network calls are made.
    """
    try:
        ComBuilding.model_validate(project_json)
    except pydantic.ValidationError as e:
        return {
            "ok": False,
            "errors": [
                {
                    "loc": ".".join(str(x) for x in err["loc"]),
                    "msg": err["msg"],
                    "type": err["type"],
                }
                for err in e.errors()
            ],
        }
    return {"ok": True, "errors": []}


# --------------------------------------------------------------------------
# Re-export json so MCP wrappers can serialize uniformly.
# --------------------------------------------------------------------------

__all__ = ["validate_code", "dry_run_project", "json"]
