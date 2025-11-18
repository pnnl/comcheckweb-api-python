"""Generic data manager with JSON schema validation."""

import copy
import json
from pathlib import Path
from typing import Any, Dict, Generic, TypeVar

from jsonschema import ValidationError, validate

T = TypeVar("T")


class DataManager(Generic[T]):
    """Generic data manager for storing and validating typed data items.

    This class provides CRUD operations on a collection of items with:
    - JSON schema validation against a schema reference
    - Unique identifier enforcement
    - Type-safe operations

    Args:
        initial_data: Initial list of items to populate the manager.
        identifier: The key name used to uniquely identify items.
        schema_reference: The JSON schema definition name (e.g., "Window", "Door").
        schema_path: Path to the JSON schema file (defaults to comCheck.schema.json).
    """

    def __init__(
        self,
        initial_data: list[T] | None = None,
        identifier: str = "id",
        schema_reference: str | None = None,
        schema_path: str | Path = "../schemas/comCheck.schema.json",
    ):
        """Initialize the data manager."""
        self._data: list[T] = []
        self._identifier = identifier
        self._schema_reference = schema_reference
        self._schema: dict[str, Any] | None = None

        # Load schema if provided
        if schema_path:
            schema_path = Path(schema_path)
            if schema_path.exists():
                with open(schema_path, "r", encoding="utf-8") as f:
                    self._schema = json.load(f)

        # Add initial data
        if initial_data:
            for item in initial_data:
                self.add_new(item)

    def _validate_item(self, item: T) -> None:
        """Validate an item against the JSON schema reference.

        Args:
            item: The item to validate.

        Raises:
            ValidationError: If validation fails.
        """
        if not self._schema or not self._schema_reference:
            return

        # Build a validation schema that references the definition
        validation_schema = {
            **self._schema,
            "$ref": f"#/definitions/{self._schema_reference}",
        }

        # Convert typed object to dict if needed
        item_dict = item if isinstance(item, dict) else item.__dict__

        try:
            validate(instance=item_dict, schema=validation_schema)
        except ValidationError as e:
            raise ValidationError(f"Validation failed: {e.message}") from e

    def _get_identifier_value(self, item: T) -> Any:
        """Extract the identifier value from an item.

        Args:
            item: The item to extract the identifier from.

        Returns:
            The identifier value.
        """
        if isinstance(item, dict):
            return item.get(self._identifier)
        return getattr(item, self._identifier, None)

    def add_new(self, item: T) -> list[T]:
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
        # Validate against schema if configured
        if self._schema_reference:
            self._validate_item(item)

        # Check if the identifier exists and has a valid value
        identifier_value = self._get_identifier_value(item)
        if identifier_value is None:
            raise ValueError(f"Item must have a valid '{self._identifier}' attribute")

        # Check for duplicates
        if any(
            self._get_identifier_value(existing) == identifier_value
            for existing in self._data
        ):
            raise ValueError(
                f"Item with {self._identifier} '{identifier_value}' already exists"
            )

        self._data.append(item)
        return self._data

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

    def modify_one(self, id_value: Any, updates: T) -> T:
        """Modify an existing item by its identifier.

        If the identifier changes, ensures no duplicates exist in the data array.

        Args:
            id_value: The current identifier value.
            updates: Partial updates to apply to the item.

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

        # If identifier is changing, validate its uniqueness
        new_identifier: T = updates[self._identifier]  # type: ignore[index]
        if new_identifier and new_identifier != id_value:
            if any(
                self._get_identifier_value(existing) == new_identifier
                for existing in self._data
            ):
                raise ValueError(
                    f"Item with {self._identifier} '{new_identifier}' already exists"
                )

        # Apply updates
        updated_item: T = {**self._data[item_index], **updates}  # type: ignore
        return copy.deepcopy(updated_item)
