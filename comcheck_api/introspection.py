"""Introspection helpers over the installed SDK.

Discoverable from the package root:

    >>> from comcheck_api import list_operations, lookup_type
    >>> ops = list_operations()
    >>> schema = lookup_type("ComBuilding")

``list_operations`` enumerates the public functions in the project
operation modules. ``lookup_type`` reflects a Pydantic model or enum
from :mod:`comcheck_api.types`. Both return Pydantic models with
typed fields so IDEs and type checkers can see the shape.
"""

from __future__ import annotations

import inspect
from typing import Any, Literal, get_args, get_origin

import pydantic
from pydantic import BaseModel, ConfigDict

from comcheck_api import (
    project_building_area_operations,
    project_envelope_operations,
)

_OP_MODULES = {
    "building_area": project_building_area_operations,
    "envelope": project_envelope_operations,
}


class OperationInfo(BaseModel):
    """One public function in a project-operation module."""

    group: str
    module: str
    name: str
    signature: str
    summary: str


class FieldSchema(BaseModel):
    """One field of a Pydantic model."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    type: str
    required: bool
    default: Any | None
    description: str


class EnumMember(BaseModel):
    name: str
    value: str


class TypeSchema(BaseModel):
    """Reflected schema of a Pydantic model or StrEnum."""

    name: str
    kind: Literal["model", "enum"]
    doc: str
    fields: list[FieldSchema] = []
    members: list[EnumMember] = []


def list_operations() -> list[OperationInfo]:
    """Discover public functions in the project operation modules.

    Discovered live via :mod:`inspect` so the list always matches the
    installed SDK version.
    """
    out: list[OperationInfo] = []
    for group, mod in _OP_MODULES.items():
        for name, fn in inspect.getmembers(mod, inspect.isfunction):
            if name.startswith("_"):
                continue
            if fn.__module__ != mod.__name__:
                continue  # skip re-exports
            doc = inspect.getdoc(fn) or ""
            summary = doc.split("\n", 1)[0]
            out.append(
                OperationInfo(
                    group=group,
                    module=fn.__module__,
                    name=name,
                    signature=f"{name}{inspect.signature(fn)}",
                    summary=summary,
                )
            )
    return out


def lookup_type(name: str) -> TypeSchema | None:
    """Reflect a Pydantic model or enum from :mod:`comcheck_api.types`.

    Returns ``None`` if no matching type is found. Lookup is
    case-insensitive as a fallback.
    """
    from comcheck_api import types as cc_types

    obj = getattr(cc_types, name, None)
    if obj is None:
        lower = name.lower()
        for cand in dir(cc_types):
            if cand.lower() == lower:
                obj = getattr(cc_types, cand)
                name = cand
                break

    if obj is None:
        return None

    if isinstance(obj, type) and issubclass(obj, pydantic.BaseModel):
        return _describe_model(name, obj)

    if isinstance(obj, type):
        members = [
            EnumMember(name=member.name, value=str(member.value))
            for member in getattr(obj, "__members__", {}).values()
        ]
        if members:
            return TypeSchema(
                name=name,
                kind="enum",
                doc=inspect.getdoc(obj) or "",
                members=members,
            )

    return None


def _describe_model(name: str, model: type[pydantic.BaseModel]) -> TypeSchema:
    fields = [
        FieldSchema(
            name=fname,
            type=_render_type(finfo.annotation),
            required=finfo.is_required(),
            default=_render_default(finfo),
            description=finfo.description or "",
        )
        for fname, finfo in model.model_fields.items()
    ]
    return TypeSchema(
        name=name,
        kind="model",
        doc=inspect.getdoc(model) or "",
        fields=fields,
    )


def _render_type(annotation: Any) -> str:
    if annotation is None or annotation is type(None):
        return "None"
    origin = get_origin(annotation)
    if origin is None:
        return getattr(annotation, "__name__", str(annotation))
    args = ", ".join(_render_type(a) for a in get_args(annotation))
    origin_name = getattr(origin, "__name__", str(origin))
    return f"{origin_name}[{args}]"


def _render_default(finfo: pydantic.fields.FieldInfo) -> Any:
    if finfo.is_required():
        return None
    default = finfo.default
    if default is pydantic.fields.PydanticUndefined:
        return None
    try:
        if isinstance(default, pydantic.BaseModel):
            return default.model_dump(mode="json")
        return default
    except Exception:  # noqa: BLE001
        return repr(default)


__all__ = [
    "OperationInfo",
    "FieldSchema",
    "EnumMember",
    "TypeSchema",
    "list_operations",
    "lookup_type",
]
