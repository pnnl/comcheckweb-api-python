"""In-memory registry for unique component identifiers.

The registry tracks every ID that has been issued or imported so that
:func:`generate_id_with_prefix` never produces duplicates within a session.
Call :func:`reset_registry` between test runs or independent sessions.
"""

_used_ids: set[str] = set()
_prefix_counters: dict[str, int] = {}


def register_existing_id(id: str):
    """Register a pre-existing ID so it is not re-issued by the generator.

    Args:
        id: The existing ID string to reserve.
    """
    if id in _used_ids:
        # ID already registered, skip silently
        return
    _used_ids.add(id)

    prefix, number = _parse_prefix_number(id)
    if prefix:
        current_max = _prefix_counters.get(prefix, 0)
        if number and number > current_max:
            _prefix_counters[prefix] = number


def generate_id_with_prefix(prefix: str) -> str:
    """Generate a unique ID of the form ``"<prefix> <n>"`` for the given prefix.

    Args:
        prefix: The prefix string (e.g. ``"Door:Door"``).

    Returns:
        A new unique ID string that has not been previously issued.
    """
    counter = _prefix_counters.get(prefix, 0) + 1

    while True:
        candidate = f"{prefix} {counter}"
        if candidate not in _used_ids:
            _used_ids.add(candidate)
            _prefix_counters[prefix] = counter
            return candidate
        counter += 1


def release_id(id: str):
    """Release a previously registered ID so it may be reused.

    Args:
        id: The ID string to release.
    """
    _used_ids.discard(id)
    # Note: Not adjusting _prefix_counters for simplicity


def reset_registry():
    """Clear all registered IDs and prefix counters, resetting the registry to empty."""
    _used_ids.clear()
    _prefix_counters.clear()


def _parse_prefix_number(id: str):
    """Parse a prefix and optional trailing number from a composite ID.

    Args:
        id: An ID string such as ``"Door:Door 5"``.

    Returns:
        A ``(prefix, number)`` tuple where *number* is ``None`` when the ID
        has no trailing integer.
    """
    parts = id.rsplit(" ", 1)
    if len(parts) == 2 and parts[1].isdigit():
        return parts[0], int(parts[1])
    return id, None
