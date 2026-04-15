import logging
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

logger = logging.getLogger(__name__)

T = TypeVar("T")
S = TypeVar("S")


class CustomBaseModel(BaseModel):
    """Base model providing structured, type-safe manipulation of nested data components.

    Extends Pydantic's :class:`~pydantic.BaseModel` with convenience methods
    for appending, updating, and removing items in list-valued sub-component
    fields (e.g. windows on a wall, skylights on a roof).  Subclasses
    automatically gain ``add_<field>`` helper methods for every field whose
    type is itself a :class:`~pydantic.BaseModel`.
    """

    _identifier: str = "id"

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        """Automatically generate `add_<field>` methods for BaseModel-typed fields on subclasses."""
        super().__pydantic_init_subclass__(**kwargs)
        try:
            from typing import get_type_hints

            hints = get_type_hints(cls)
        except Exception:
            return

        for field_name, field_type in hints.items():
            try:
                if isinstance(field_type, type) and issubclass(field_type, BaseModel):

                    def make_adder(fn, ft):
                        """Create an adder method that sets a single BaseModel-typed field."""

                        def adder(self, instance, fn=fn, ft=ft):
                            """Set the field `fn` to `instance` on this model."""
                            setattr(self, fn, instance)
                            logger.debug("Added %s: %s", fn, instance)

                        adder.__name__ = f"add_{fn}"
                        return adder

                    setattr(
                        cls, f"add_{field_name}", make_adder(field_name, field_type)
                    )
            except TypeError:
                continue

    def append_subcomponent(
        self,
        subcomponent: S | dict,
        subcomponent_name: Optional[str] = None,
    ) -> T:
        """
        Append a subcomponent to the corresponding subcomponent list.

        Args:
            subcomponent: The subcomponent instance to add.
            subcomponent_name: Name of the subcomponent attribute (e.g., ``"door"``).

        Returns:
            Item with the new subcomponent added.
        """

        subcomponent_type, subcomponent_name = self._get_normalized_subcomponent_info(
            subcomponent=subcomponent, subcomponent_name=subcomponent_name
        )

        current_subcomponents = self._get_subcomponent_list(subcomponent_name)
        subcomponent_manager = DataManager[subcomponent_type](
            initial_data=current_subcomponents, model_type=subcomponent_type
        )

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

        subcomponent_type, subcomponent_name = self._get_normalized_subcomponent_info(
            subcomponent=subcomponent_updates, subcomponent_name=subcomponent_name
        )

        current_subcomponents = self._get_subcomponent_list(subcomponent_name)
        subcomponent_manager = DataManager[subcomponent_type](
            initial_data=current_subcomponents, model_type=subcomponent_type
        )

        subcomponent_manager.modify_one(
            id_value=subcomponent_id, updates=subcomponent_updates
        )

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
            raise ValueError(
                "Must provide either subcomponent instance or subcomponent_id and subcomponent_name"
            )

        subcomponent_type, subcomponent_name = self._get_normalized_subcomponent_info(
            subcomponent=subcomponent,
            subcomponent_name=subcomponent_name,
        )

        current_subcomponents = self._get_subcomponent_list(subcomponent_name)
        subcomponent_manager = DataManager[subcomponent_type](
            initial_data=current_subcomponents, model_type=subcomponent_type
        )

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

    def _get_normalized_subcomponent_info(
        self, subcomponent: S, subcomponent_name: str | None
    ):
        """Resolve the concrete type and attribute name for a subcomponent.

        When *subcomponent_name* is provided the type is looked up from
        ``core_types`` by capitalising the name.  Otherwise the type and
        name are derived from the *subcomponent* instance itself.

        Args:
            subcomponent: A model instance or dict representing the subcomponent.
            subcomponent_name: Optional explicit attribute name (e.g. ``"door"``).

        Returns:
            A ``(subcomponent_type, resolved_subcomponent_name)`` tuple.

        Raises:
            ValueError: If the name cannot be resolved to a known type, or if
                *subcomponent* is a dict and no *subcomponent_name* is given.
            TypeError: If *subcomponent* is neither a dict nor a
                :class:`CustomBaseModel`.
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
                raise ValueError(
                    "subcomponent_name is required when subcomponent is a dict"
                )
            elif isinstance(subcomponent, CustomBaseModel):
                subcomponent_name = subcomponent.json_key()
                return type(subcomponent), subcomponent_name
            else:
                raise TypeError(
                    f"subcomponent must be a dict or CustomBaseModel instance, "
                    f"got {type(subcomponent).__name__}"
                )

    def _get_subcomponent_list(self, subcomponent_name: str):
        """Return the current list for a named subcomponent attribute.

        Args:
            subcomponent_name: Name of the list-valued field on this model.

        Returns:
            The current list value for the given attribute.

        Raises:
            AttributeError: If the field does not exist on this model.
            TypeError: If the field value is not a list.
        """
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
        """Traverse nested attributes/list indices using a dot-bracket path expression.

        Args:
            path: Dot-separated path string with optional bracket indexing,
                e.g. ``"envelope.roof[0].assemblyType"``.
            default: Value to return if any segment of the path is missing.

        Returns:
            The value at the given path, or ``default`` if not found.
        """
        current = self

        # Split on dots that are not inside brackets
        parts = re.split(r"\.(?![^\[]*\])", path)

        try:
            for part in parts:
                # Handle object
                attr_match = re.match(r"^([A-Za-z_]\w*)", part)
                if attr_match:
                    attr = attr_match.group(1)
                    if not hasattr(current, attr):
                        return default
                    current = getattr(current, attr)
                    remainder = part[len(attr) :]
                else:
                    remainder = part

                # Handle brackets for possible list
                for m in re.finditer(r"\[(.*?)\]", remainder):
                    idx_str = m.group(1).strip()
                    idx = int(idx_str)
                    current = current[idx]
        except Exception:
            return default

        return current

    def require_attribute(self, path: str) -> None:
        """Assert that a nested attribute exists and is truthy.

        Args:
            path: Dot-bracket path to the attribute (see ``get_by_path``).

        Raises:
            ValueError: If the attribute is falsy or not found.
        """
        if not self.get_by_path(path):
            raise ValueError(f"'{path}' is required in project")

    @classmethod
    def json_key(cls) -> str:
        """Return the camelCase JSON key derived from the class name.

        Returns:
            Class name with the first character lowercased (e.g. ``AgWall`` → ``agWall``).
        """
        return cls.__name__[0].lower() + cls.__name__[1:]
