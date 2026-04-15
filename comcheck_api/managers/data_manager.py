"""Generic data manager with JSON schema validation."""

import copy
import json
from pathlib import Path
from typing import (
    Any,
    Generic,
    List,
    Type,
    TypeVar,
)
from collections import namedtuple

from pydantic import BaseModel
from comcheck_api.utilities.id_registry import (
    register_existing_id,
    generate_id_with_prefix,
)

T = TypeVar("T")
S = TypeVar("S")


class DataManager(Generic[T]):
    """Generic data manager for storing and validating typed data items.

    This class provides CRUD operations on a collection of items with:
    - JSON schema validation against a schema reference
    - Unique identifier enforcement
    - Type-safe operations

    Args:
        initial_data: Initial list of items to populate the manager.
        schema_path: Path to the JSON schema file (defaults to comCheck.schema.json).
    """

    model_type: Type[BaseModel] | None = None

    def __init__(
        self,
        initial_data: list[T] | None = [],
        model_type: Type[BaseModel] | None = None,
        schema_path: str | Path = "../schemas/comCheck.schema.json",
    ):
        """Initialize the data manager.

        Args:
            initial_data: Items to pre-populate the manager with.
            model_type: Pydantic model class for the managed items.
                Falls back to the class-level ``model_type`` attribute.
            schema_path: Path to a JSON schema file for validation.
        """
        self._data: list[T] = []
        self._schema: dict[str, Any] | None = None

        self._initialize_metadata(model_type)
        self._initialize_schema(schema_path)
        self._initialize_data(initial_data)

    def _initialize_metadata(self, model_type: BaseModel | None = None) -> None:
        """Resolve and store the model type and its ID field information.

        Args:
            model_type: Explicit model class; falls back to the class-level ``model_type``.

        Raises:
            ValueError: If no model type is available or no ID info is found for it.
        """
        self.model_type = model_type or self.__class__.model_type
        if self.model_type is None:
            raise ValueError(
                f"{self.__class__.__name__} requires a model_type "
                "either as a class variable or via initialization."
            )

        id_info = get_model_info(self.model_type)
        if id_info:
            self._identifier = id_info.identifier
            self._id_prefix = id_info.id_prefix
        else:
            raise ValueError(
                f"No ID info found for model class {self.model_type.__name__}"
            )

    def _initialize_schema(self, schema_path: str | Path) -> None:
        """Load the JSON schema from disk if the file exists.

        Args:
            schema_path: Path to the JSON schema file.
        """
        if schema_path:
            schema_path = Path(schema_path)
            if schema_path.exists():
                with open(schema_path, "r", encoding="utf-8") as f:
                    self._schema = json.load(f)

    def _initialize_data(self, initial_data: list[T] = []) -> None:
        """Populate the manager with an initial list of items.

        Args:
            initial_data: Items to add via ``add_new`` on startup.
        """
        for item in initial_data:
            self.add_new(item)

    def _validate_item(self, item: T) -> T:
        """Validate an item against the JSON schema reference.

        Args:
            item: The item to validate.

        Returns:
            A model instance.

        Raises:
            ValidationError: If validation fails.
        """
        if isinstance(item, self.model_type):
            model_instance = item
        else:
            model_instance = self.model_type.model_validate(item)

        return model_instance

    def _get_identifier_value(self, item: T) -> Any:
        """Extract the identifier value from an item.

        Args:
            item: The item to extract the identifier from.

        Returns:
            The identifier value.
        """
        return getattr(item, self._identifier, None)

    def add_new(self, item: T | dict[str, Any]) -> list[T]:
        """Add a new item to the data array.

        Args:
            item: The item to add.

        Returns:
            The updated data array.

        Raises:
            ValueError: If the identifier is missing or if an item with the
                same identifier already exists.
            ValidationError: If schema validation fails.
        """
        model_instance = self._validate_item(item)

        if item:
            self.generate_identifier(model_instance)

            self._data.append(copy.deepcopy(model_instance))

        return self.get_all()

    def generate_identifier(self, item: T) -> None:
        """Ensure the item has a valid and unique identifier.

        If the identifier is missing, invalid, duplicated, or does not match
        the expected prefix, a new unique one is generated via the ID registry.

        Args:
            item: The item whose identifier should be validated or assigned.

        Raises:
            Exception: If the item is already present in the managed list.
        """
        if any(existing is item for existing in self._data):
            raise Exception("Item already exists in managed list")

        if self._id_prefix is None:
            return

        current = getattr(item, self._identifier, None)

        needs_new_identifier = (
            not current
            or not isinstance(current, str)
            or current
            in {getattr(existing, self._identifier, None) for existing in self._data}
            or (not current.startswith(self._id_prefix))
        )

        if not needs_new_identifier:
            register_existing_id(current)
            return

        new_id = generate_id_with_prefix(self._id_prefix)

        item.__dict__[self._identifier] = new_id

    def add_subcomponent(
        self,
        parent: T,
        subcomponent: S,
    ) -> T:
        """
        Add a new subcomponent to a parent item.

        Args:
            parent: The parent item (e.g., BgWall)
            subcomponent: The subcomponent to add (e.g., Door)

        Returns:
            Updated parent with the new subcomponent added.
        """
        subcomponent_type = type(subcomponent)

        subcomponent_name = subcomponent.json_key()

        current_subcomponents: List[S] = getattr(parent, subcomponent_name, [])

        subcomponent_manager = DataManager[subcomponent_type](
            initial_data=current_subcomponents, model_type=subcomponent_type
        )

        parent.__dict__[subcomponent_name] = subcomponent_manager.add_new(subcomponent)
        updated = self.modify_one(self._get_identifier_value(parent), parent)
        return updated

    def get_all(self) -> list[T]:
        """Get all items.

        Returns:
            A deep copy of the data array.
        """
        return copy.deepcopy(self._data)

    def get_by_identifier(self, id_value: Any) -> T | None:
        """Find an item by its identifier.

        Args:
            id_value: The value of the identifier to search for.

        Returns:
            The found item, or None if not found.
        """
        for item in self._data:
            if self._get_identifier_value(item) == id_value:
                return copy.deepcopy(item)
        return None

    def delete_one(self, id_value: Any) -> bool:
        """Delete an item by its identifier.

        Args:
            id_value: The value of the identifier to delete.

        Returns:
            True if an item was deleted, False otherwise.
        """
        initial_length = len(self._data)
        self._data = [
            item for item in self._data if self._get_identifier_value(item) != id_value
        ]
        return len(self._data) != initial_length

    def modify_one(self, id_value: Any, updates: T | dict[str, Any]) -> T:
        """Modify an existing item by its identifier.

        If the identifier changes, ensures no duplicates exist in the data array.

        Args:
            id_value: The current identifier value.
            updates: Partial updates (dict) or full model object to apply to the item.

        Returns:
            The updated item.

        Raises:
            ValueError: If the item is not found or if the updated identifier
                already exists.
        """
        item_index = None
        for i, item in enumerate(self._data):
            if self._get_identifier_value(item) == id_value:
                item_index = i
                break

        if item_index is None:
            raise ValueError(f"Item with {self._identifier} '{id_value}' not found")

        # Convert updates to dict if it's a model object
        updates_dict = (
            updates.model_dump(mode="json", exclude_unset=True)
            if isinstance(updates, BaseModel)
            else updates
        )

        # If identifier is changing, validate its uniqueness
        new_identifier = updates_dict.get(self._identifier)
        if new_identifier and new_identifier != id_value:
            if any(
                self._get_identifier_value(existing) == new_identifier
                for existing in self._data
            ):
                raise ValueError(
                    f"Item with {self._identifier} '{new_identifier}' already exists"
                )

        original = self._data[item_index]

        # Validate that all keys in updates_dict are valid fields
        model_fields = type(original).model_fields
        invalid_fields = set(updates_dict.keys()) - set(model_fields.keys())
        if invalid_fields:
            raise ValueError(f"Invalid fields in updates: {invalid_fields}")

        # Validate partial updates by attempting to construct with merged data
        # This will raise Pydantic ValidationError if types don't align
        # Get only the model fields to avoid serializing dynamically added methods
        original_dict = original.model_dump(
            mode="python", by_alias=False, exclude_unset=True
        )
        merged = {**original_dict, **updates_dict}
        try:
            updated_item = type(original).model_validate(merged)
        except Exception as e:
            raise ValueError(
                f"Validation failed for updates to {self._identifier} '{id_value}': {str(e)}"
            ) from e

        self._data[item_index] = copy.deepcopy(updated_item)  # Protect internal state
        return copy.deepcopy(
            updated_item
        )  # Protect returned object from external mutation


IdInfo = namedtuple("IdInfo", ["identifier", "id_prefix"])


def get_model_info(model_class: Type[BaseModel]) -> IdInfo | None:
    """Return the identifier field name and ID prefix for a known model class.

    Args:
        model_class: The Pydantic model class to look up.

    Returns:
        An ``IdInfo`` namedtuple with ``identifier`` and ``id_prefix`` fields,
        or ``None`` if the class is not registered.
    """
    from comcheck_api.types.core_types import (
        Door,
        Roof,
        Window,
        BgWall,
        AgWall,
        Floor,
        Skylight,
        ThermalBridge,
        WholeBldgUse,
    )

    MODEL_TO_ID_INFO = {
        Door: IdInfo(identifier="assemblyType", id_prefix="Door:Door"),
        Roof: IdInfo(identifier="assemblyType", id_prefix="Roof:Roof"),
        Window: IdInfo(identifier="assemblyType", id_prefix="Window:Window"),
        BgWall: IdInfo(identifier="assemblyType", id_prefix="Basement:Basement"),
        AgWall: IdInfo(identifier="assemblyType", id_prefix="AgWall:Ext Wall"),
        Floor: IdInfo(identifier="assemblyType", id_prefix="Floor:Floor"),
        Skylight: IdInfo(identifier="assemblyType", id_prefix="Skylight:Skylight"),
        ThermalBridge: IdInfo(identifier="id", id_prefix=None),
        WholeBldgUse: IdInfo(identifier="key", id_prefix=None),
    }
    return MODEL_TO_ID_INFO.get(model_class)
