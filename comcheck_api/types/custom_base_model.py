import re
from typing import (
    Any,
    Optional,
    TypeVar,
    get_type_hints,
)

from pydantic.main import _model_construction

from pydantic import BaseModel

from comcheck_api.managers.data_manager import DataManager

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

    It is intended to be extended by models that contain lists of
    subcomponents and need controlled, validated CRUD-like operations
    on those nested items.
    """
    _identifier: str = "id"

    def append_subcomponent(
        self,
        subcomponent: S | dict,
        subcomponent_name: Optional[str] = None,
    ) -> T:
        """
        Append a subcomponent to the corresponding subcomponent list.

        Args:
            subcomponent: The subcomponent instance to add
            subcomponent name: Name of the subcomponent attribute (e.g., "door")

        Returns:
            Item with the new subcomponent added.
        """

        subcomponent_type, subcomponent_name = self._get_normalized_subcomponent_info(subcomponent=subcomponent, subcomponent_name=subcomponent_name)

        current_subcomponents = self._get_subcomponent_list(subcomponent_name)
        subcomponent_manager = DataManager[subcomponent_type](initial_data=current_subcomponents, model_type=subcomponent_type)

        updated_list = subcomponent_manager.add_new(subcomponent)

        setattr(self, subcomponent_name, updated_list)
        
        return self
    
    def update_subcomponent_list(
        self,
        *,
        subcomponent_updates: Optional[S | dict] = None,
        subcomponent_id: str = None,
        subcomponent_name: str = None,
    ) -> T:
        """
        Append a subcomponent to the corresponding subcomponent list.

        Args:
            subcomponent_updates: Partial updates (dict) or full model object to apply to the item.
            subcomponent_id: The unique identifier of the subcomponent to remove
            subcomponent_name: Name of the subcomponent attribute (e.g., "door")

        Returns:
            Item with the new subcomponent added.
        """

        subcomponent_type, subcomponent_name = self._get_normalized_subcomponent_info(subcomponent=subcomponent_updates, subcomponent_name=subcomponent_name)

        current_subcomponents = self._get_subcomponent_list(subcomponent_name)
        subcomponent_manager = DataManager[subcomponent_type](initial_data=current_subcomponents, model_type=subcomponent_type)

        subcomponent_manager.modify_one(id_value=subcomponent_id, updates=subcomponent_updates)

        setattr(self, subcomponent_name, subcomponent_manager.get_all())
        
        return self
    
    def remove_from_subcomponent_list(
        self,
        *,
        subcomponent: Optional[S | dict] = None,
        subcomponent_id: Optional[str] = None,
        subcomponent_name: Optional[str] = None,
    ) -> T:
        """
        Remove a subcomponent from a list-valued attribute by instance or ID.

        Args:
            subcomponent: The subcomponent instance to remove
            subcomponent_id: The unique identifier of the subcomponent to remove
            subcomponent_name: Name of the subcomponent attribute (e.g., "door")

        Returns:
            Item with the subcomponent removed.
        """
        if subcomponent is None and (subcomponent_name and subcomponent_id) is None:
            raise ValueError("Must provide either subcomponent instance or subcomponent_id and subcomponent_name")

        subcomponent_type, subcomponent_name = self._get_normalized_subcomponent_info(
            subcomponent=subcomponent,
            subcomponent_name=subcomponent_name,
        )

        current_subcomponents = self._get_subcomponent_list(subcomponent_name)
        subcomponent_manager = DataManager[subcomponent_type](initial_data=current_subcomponents, model_type=subcomponent_type)

        subcomponent_identifier = subcomponent_manager._identifier

        target_id = (
            getattr(subcomponent, subcomponent_identifier)
            if subcomponent is not None
            else subcomponent_id
        )

        was_deleted = subcomponent_manager.delete_one(target_id)

        if not was_deleted:
            raise ValueError(
                f"Subcomponent with id {target_id} not found in '{subcomponent_name}'"
            )

        setattr(self, subcomponent_name, subcomponent_manager.get_all())

        return self
    
    
    def _get_normalized_subcomponent_info(self, subcomponent: S, subcomponent_name: str | None):

        """
        Returns:
            (subcomponent_type, resolved_subcomponent_name)
        """
        if subcomponent_name:
            from comcheck_api.types import core_types
            class_name = subcomponent_name[0].upper() + subcomponent_name[1:]
            cls = getattr(core_types, class_name, None)
            if cls is None:
                raise ValueError(f"Unknown subcomponent type for name '{class_name}'")

            return cls, subcomponent_name
        else:
            if isinstance(subcomponent, dict):
                raise ValueError("subcomponent_name is required when subcomponent is a dict")
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

        current_subcomponents = getattr(self, subcomponent_name, [])

        if not isinstance(current_subcomponents, list):
            raise TypeError(
                f"{self.__class__.__name__}.{subcomponent_name} "
                f"must be a list, got {type(current_subcomponents).__name__}"
            )

        return current_subcomponents

    def get_by_path(self, path: str, default: Any = None) -> Any | None:
        current = self

        # Split on dots that are not inside brackets
        parts = re.split(r'\.(?![^\[]*\])', path)

        try:
            for part in parts:
                # Handle object
                attr_match = re.match(r'^([A-Za-z_]\w*)', part)
                if attr_match:
                    attr = attr_match.group(1)
                    if not hasattr(current, attr):
                        return default
                    current = getattr(current, attr)
                    remainder = part[len(attr):]
                else:
                    remainder = part

                # Handle brackets for possible list
                for m in re.finditer(r'\[(.*?)\]', remainder):
                    idx_str = m.group(1).strip()
                    idx = int(idx_str)
                    current = current[idx]
        except Exception:
            return default

        return current
    
    def require_attribute(self, path: str) -> None:
        if not self.get_by_path(path):
            raise ValueError(f"'{path}' is required in project")

    @classmethod
    def json_key(cls) -> str:
        return cls.__name__[0].lower() + cls.__name__[1:]