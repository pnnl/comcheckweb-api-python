"""Read-only lookup tools: introspection over the installed SDK + Skill content."""

from __future__ import annotations

import inspect
import math
import re
from typing import Any, get_args, get_origin

import pydantic

from comcheck_api import (
    project_building_area_operations,
    project_envelope_operations,
)
from comcheck_api.ai import content

# --------------------------------------------------------------------------
# list_operations — discover public functions in the operation modules.
# --------------------------------------------------------------------------


_OP_MODULES = {
    "building_area": project_building_area_operations,
    "envelope": project_envelope_operations,
}


def list_operations() -> list[dict[str, Any]]:
    """List public functions in the project operation modules.

    Discovered live via ``inspect`` so the list always matches the
    installed SDK version. Each entry has:

    - ``module`` — full module path
    - ``name`` — function name
    - ``signature`` — string-rendered signature
    - ``summary`` — first line of the docstring (or empty)
    """
    out: list[dict[str, Any]] = []
    for group, mod in _OP_MODULES.items():
        for name, fn in inspect.getmembers(mod, inspect.isfunction):
            if name.startswith("_"):
                continue
            if fn.__module__ != mod.__name__:
                continue  # skip re-exports
            doc = inspect.getdoc(fn) or ""
            summary = doc.split("\n", 1)[0]
            out.append(
                {
                    "group": group,
                    "module": fn.__module__,
                    "name": name,
                    "signature": f"{name}{inspect.signature(fn)}",
                    "summary": summary,
                }
            )
    return out


# --------------------------------------------------------------------------
# lookup_type — reflect a Pydantic model from comcheck_api.types.
# --------------------------------------------------------------------------


def lookup_type(name: str) -> dict[str, Any]:
    """Return field-level schema for a Pydantic model in ``comcheck_api.types``.

    Returns ``{"name": ..., "fields": [...], "doc": ...}``. If the name
    doesn't match a Pydantic model in the types module, returns
    ``{"error": ...}``.
    """
    from comcheck_api import types as cc_types

    obj = getattr(cc_types, name, None)
    if obj is None:
        # Try case-insensitive match.
        lower = name.lower()
        for cand in dir(cc_types):
            if cand.lower() == lower:
                obj = getattr(cc_types, cand)
                name = cand
                break

    if obj is None:
        return {"error": f"No type named {name!r} in comcheck_api.types"}

    if isinstance(obj, type) and issubclass(obj, pydantic.BaseModel):
        return _describe_model(name, obj)

    # StrEnum-style options classes commonly live alongside models.
    if isinstance(obj, type):
        members = []
        for member in getattr(obj, "__members__", {}).values():
            members.append({"name": member.name, "value": str(member.value)})
        if members:
            return {
                "name": name,
                "kind": "enum",
                "doc": inspect.getdoc(obj) or "",
                "members": members,
            }

    return {"error": f"{name!r} is not a Pydantic model or enum"}


def _describe_model(name: str, model: type[pydantic.BaseModel]) -> dict[str, Any]:
    fields: list[dict[str, Any]] = []
    for fname, finfo in model.model_fields.items():
        fields.append(
            {
                "name": fname,
                "type": _render_type(finfo.annotation),
                "required": finfo.is_required(),
                "default": _render_default(finfo),
                "description": finfo.description or "",
            }
        )
    return {
        "name": name,
        "kind": "model",
        "doc": inspect.getdoc(model) or "",
        "fields": fields,
    }


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
        # Pydantic models / enums won't JSON-serialize cleanly.
        if isinstance(default, pydantic.BaseModel):
            return default.model_dump(mode="json")
        return default
    except Exception:  # noqa: BLE001
        return repr(default)


# --------------------------------------------------------------------------
# search_docs — BM25-style ranking over Skill content.
# --------------------------------------------------------------------------


_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]+")


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text)]


def _chunk(text: str, source: str, max_chars: int = 800) -> list[dict[str, str]]:
    """Split text into chunks of up to max_chars on paragraph boundaries."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[dict[str, str]] = []
    buf = ""
    for p in paragraphs:
        if len(buf) + len(p) + 2 > max_chars and buf:
            chunks.append({"source": source, "text": buf})
            buf = p
        else:
            buf = f"{buf}\n\n{p}" if buf else p
    if buf:
        chunks.append({"source": source, "text": buf})
    return chunks


def _build_corpus() -> list[dict[str, str]]:
    chunks: list[dict[str, str]] = []
    chunks.extend(_chunk(content.read_skill_body(), "SKILL.md"))
    for ref_name in content.list_references():
        chunks.extend(_chunk(content.read_reference(ref_name), f"reference/{ref_name}"))
    for ex_name in content.list_examples():
        chunks.extend(_chunk(content.read_example(ex_name), f"examples/{ex_name}"))
    return chunks


def search_docs(query: str, k: int = 5) -> list[dict[str, str]]:
    """Search Skill content for ``query`` using BM25 ranking.

    Returns at most ``k`` ranked chunks of the form
    ``{"source": "<file>", "snippet": "...", "score": <float>}``.
    """
    corpus = _build_corpus()
    if not corpus:
        return []

    q_tokens = _tokenize(query)
    if not q_tokens:
        return []

    docs_tokens = [_tokenize(c["text"]) for c in corpus]
    n = len(corpus)
    avgdl = sum(len(d) for d in docs_tokens) / max(1, n)

    df: dict[str, int] = {}
    for d in docs_tokens:
        for term in set(d):
            df[term] = df.get(term, 0) + 1

    k1 = 1.5
    b = 0.75

    scored: list[tuple[float, int]] = []
    for i, d in enumerate(docs_tokens):
        score = 0.0
        dl = len(d) or 1
        tf: dict[str, int] = {}
        for term in d:
            tf[term] = tf.get(term, 0) + 1
        for term in q_tokens:
            if term not in tf:
                continue
            idf = math.log(1 + (n - df[term] + 0.5) / (df[term] + 0.5))
            freq = tf[term]
            score += idf * (freq * (k1 + 1)) / (freq + k1 * (1 - b + b * dl / avgdl))
        if score > 0:
            scored.append((score, i))

    scored.sort(reverse=True)
    out: list[dict[str, str]] = []
    for score, idx in scored[:k]:
        chunk = corpus[idx]
        out.append(
            {
                "source": chunk["source"],
                "score": round(score, 3),
                "snippet": chunk["text"][:600],
            }
        )
    return out
