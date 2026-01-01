import copy
from typing import (
    Any,
    TypeVar,
    get_type_hints,
)

from pydantic.main import _model_construction

from pydantic import BaseModel

from comcheck_api.utilities.data_manager import DataManager

T = TypeVar("T")
S = TypeVar("S")

class CustomBaseModelMeta(_model_construction.ModelMetaclass):
    def __new__(mcls, name, bases, namespace):
        cls = super().__new__(mcls, name, bases, namespace)

        # Get all type hints for this class
        hints = get_type_hints(cls)

        # Identify fields whose type is a subclass of CustomBaseModel
        for field_name, field_type in hints.items():
            if isinstance(field_type, type) and issubclass(field_type, BaseModel):
                # Define an add_<field_name> method dynamically
                def make_adder(fn, ft):
                    def adder(self, instance, fn=fn, ft=ft):
                        setattr(self, fn, instance)
                        print(f"Added {fn}: {instance}")
                    adder.__name__ = f"add_{fn}"
                    return adder

                setattr(cls, f"add_{field_name}", make_adder(field_name, field_type))

        return cls
    

class CustomBaseModel(BaseModel, metaclass=CustomBaseModelMeta):
    """Base model providing structured, type-safe manipulation of nested
    data components.

    This class adds support for:
    - Adding typed subcomponents (including dict -> model coercion)
    - Enforcing naming conventions for subcomponent attributes
    - Safe traversal of nested attributes using dot-paths
    - Automatic derivation of JSON keys for model types

    It is intended to be extended by models that contain lists of
    subcomponents and need controlled, validated CRUD-like operations
    on those nested items.
    """
    _identifier: str = "id"

    def add_subcomponent(
        self,
        subcomponent: S,
        subcomponent_name: str | None = None,
    ) -> T:
        """
        Add a new subcomponent to internal data.

        Args:
            subcomponent: The subcomponent to add (e.g., Door)
            subcomponent name: Name of the subcomponent attribute (e.g., "door")

        Returns:
            Item with the new subcomponent added.
        """

        subcomponent_type, subcomponent_name = self._get_normalized_subcomponent_info(subcomponent=subcomponent, subcomponent_name=subcomponent_name)

        current_subcomponents = self._get_subcomponent_list(subcomponent_name)
        subcomponent_manager = DataManager[subcomponent_type](initial_data=current_subcomponents, model_type=subcomponent_type)

        updated_list = subcomponent_manager.add_new(subcomponent)

        setattr(self, subcomponent_name, updated_list)
        return copy.deepcopy(self)
    
    
    def _get_normalized_subcomponent_info(self, subcomponent: S, subcomponent_name: str | None):
        """
        Returns:
            (subcomponent_type, resolved_subcomponent_name)
        """
        if isinstance(subcomponent, dict):
            if subcomponent_name is None:
                raise ValueError("subcomponent_name is required when subcomponent is a dict")

            # Convert "door" -> "Door"
            from comcheck_api.types import core_types
            class_name = subcomponent_name[0].upper() + subcomponent_name[1:]
            cls = getattr(core_types, class_name, None)
            if cls is None:
                raise ValueError(f"Unknown subcomponent type for name '{class_name}'")

            return cls, subcomponent_name

        elif isinstance(subcomponent, CustomBaseModel):
            subcomponent_name = subcomponent.json_key()
            return type(subcomponent), subcomponent_name

        else:
            raise TypeError(
                f"subcomponent must be a dict or CustomBaseModel instance, "
                f"got {type(subcomponent).__name__}"
            )
        
    def _get_subcomponent_list(self, subcomponent_name: str):
        if subcomponent_name not in self.__class__.model_fields:
            raise AttributeError(
                f"{self.__class__.__name__} has no subcomponent list '{subcomponent_name}'"
            )

        current_subcomponents = getattr(self, subcomponent_name)

        if not isinstance(current_subcomponents, list):
            raise TypeError(
                f"{self.__class__.__name__}.{subcomponent_name} "
                f"must be a list, got {type(current_subcomponents).__name__}"
            )

        return current_subcomponents

    def get_by_path(self, path: str, default: Any = None) -> Any | None:
        attrs = path.split(".")
        current = self
        for attr in attrs:
            if not hasattr(current, attr):
                return default
            current = getattr(current, attr)
        return current

    def set_by_path(self, path: str, value: Any) -> None:
        attrs = path.split(".")
        current = self
        for attr in attrs[:-1]:
            if not hasattr(current, attr):
                raise AttributeError(f"{current!r} has no attribute {attr!r}")
            current = getattr(current, attr)
        setattr(current, attrs[-1], value)

    @classmethod
    def json_key(cls) -> str:
        return cls.__name__[0].lower() + cls.__name__[1:]