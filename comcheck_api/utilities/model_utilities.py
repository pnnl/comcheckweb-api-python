from typing import Any, Iterable, List
from pydantic import BaseModel

def find_objects_by_ids(
    root: Any,
    ids: List[str],
    id_field: str = "id",
) -> List[Any]:
    """
    Recursively search through a nested structure (Pydantic models, dicts,
    lists/tuples/sets) and return all objects whose `id_field` value is in `ids`.

    Args:
        root: Object to search. 
        ids: Iterable of ID values to match against.
        id_field: Name of the ID field to look for (default: "id").

    Returns:
        List of objects (dicts or Pydantic models) that have `id_field` in `ids`.
    """
    target_ids = set(ids)
    results = []
    _find_objects_by_ids_recursive(root, target_ids, id_field, results)
    return results


def _find_objects_by_ids_recursive(
    obj: Any,
    target_ids: set,
    id_field: str,
    results: List[Any],
) -> None:
    original = obj
    if isinstance(obj, BaseModel):
        obj = obj.__dict__

    if isinstance(obj, dict):
        if id_field in obj and obj[id_field] in target_ids:
            results.append(original)
        for value in obj.values():
            _find_objects_by_ids_recursive(value, target_ids, id_field, results)
    elif isinstance(obj, (list, set)):
        for item in obj:
            _find_objects_by_ids_recursive(item, target_ids, id_field, results)
    else:
        return