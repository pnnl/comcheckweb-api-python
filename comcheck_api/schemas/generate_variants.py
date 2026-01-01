from typing import Annotated, Any, Union, get_args, get_origin
import typing
import yaml
import inspect
from pathlib import Path
from comcheck_api.schemas.custom_base_model import CustomBaseModel
from pydantic import BaseModel
from comcheck_api.types import core_types

VARIANTS_PATH = Path("comcheck_api/schemas/model_variants.yml")
OUTPUT_PATH = Path("comcheck_api/types/core_types_variants.py")

def iter_custom_models(module):
    for _, obj in inspect.getmembers(module, inspect.isclass):
        if obj.__module__ == module.__name__ and issubclass(obj, CustomBaseModel):
            yield obj

BASE_MODELS = {
    cls.__name__: cls
    for cls in iter_custom_models(core_types)
}

used_typing: set[str] = set()


def generate():
    config = yaml.safe_load(VARIANTS_PATH.read_text())

    global used_typing, used_model_types
    used_typing = set()
    used_model_types = set()

    body_lines: list[str] = []


    for base_name, variants in config.items():
        for variant_id, spec in variants.items():
            base_model = BASE_MODELS.get(base_name)
            if not base_model:
                raise ValueError(f"Base model {base_name} not found in core_types.")

            variant_name = f"{base_name}{variant_id.capitalize()}"
            
            mixin_name = f"{variant_name}Mixin"
            body_lines.append(f"class {mixin_name}:")
            if not spec.get("required") and not spec.get("defaults"):
                body_lines.append("\tpass")
            else:
                # defaults
                for field_name, default in (spec.get("defaults") or {}).items():
                    field_info = base_model.model_fields[field_name]
                    type_expr = format_annotation(field_info.annotation)
                    default_repr = repr(default)
                    body_lines.append(f"\t{field_name}: {type_expr} = Field(")
                    body_lines.append(f"\t\t{default_repr},")
                    if field_info.description:
                        body_lines.append(f"\t\tdescription={field_info.description!r},")
                    body_lines.append("\t)")

                for field_name in spec.get("required") or []:
                    field_info = base_model.model_fields[field_name]
                    type_expr = format_annotation(field_info.annotation)
                    body_lines.append(f"\t{field_name}: {type_expr} = Field(")
                    body_lines.append("\t\t...,")
                    if field_info.description:
                        body_lines.append(f"\t\tdescription={field_info.description!r},")
                    body_lines.append("\t)")

                body_lines.append("")
                body_lines.append(f"class {variant_name}({mixin_name}, {base_name}):")
                body_lines.append("\tpass")
                body_lines.append("")

        header_lines: list[str] = []

        if used_typing:
            typing_imports = ", ".join(sorted(used_typing))
            header_lines.append(f"from typing import {typing_imports}")

        header_lines.append("from pydantic import Field")

        if used_model_types:
            names = ", ".join(sorted(used_model_types))
            header_lines.append(f"from .core_types import {names}")
        else:
            header_lines.append("from .core_types import *")

        header_lines.append("")  # blank line

    OUTPUT_PATH.write_text("\n".join(header_lines + body_lines))


def format_annotation(ann: Any) -> str:
    origin = get_origin(ann)

    # Handle Annotated[T, ...] by collapsing it to T
    if origin is Annotated:
        # Annotated[T, *meta]
        args = get_args(ann)
        inner = args[0]
        return format_annotation(inner)

    if origin is not None:
        args = get_args(ann)

        # Optional[T] is Union[T, NoneType]
        if origin is Union:
            if len(args) == 2 and type(None) in args:
                used_typing.add("Optional")
                other = next(a for a in args if a is not type(None))
                return f"Optional[{format_annotation(other)}]"
            used_typing.add("Union")
            inner = ", ".join(format_annotation(a) for a in args)
            return f"Union[{inner}]"

        origin_name = origin.__name__  # e.g. list, dict, etc.
        # Normalize to capitalized typing names if you want (List, Dict)
        origin_name = {"list": "List", "dict": "Dict"}.get(origin_name, origin_name)
        used_typing.add(origin_name)
        if args:
            inner = ", ".join(format_annotation(a) for a in args)
            return f"{origin_name}[{inner}]"
        return origin_name

    # Builtins
    if getattr(ann, "__module__", "") == "builtins":
        return ann.__name__

    # ForwardRef
    if isinstance(ann, typing.ForwardRef):
        return ann.__forward_arg__

    # Regular class / enum / model
    if hasattr(ann, "__name__"):
        return ann.__name__

    # Fallback
    r = repr(ann)
    if r.startswith("typing."):
        r = r.replace("typing.", "")
    return r

if __name__ == "__main__":
    generate()