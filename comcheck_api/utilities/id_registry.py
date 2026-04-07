_used_ids: set[str] = set()
_prefix_counters: dict[str, int] = {}


def register_existing_id(id: str):
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
    counter = _prefix_counters.get(prefix, 0) + 1

    while True:
        candidate = f"{prefix} {counter}"
        if candidate not in _used_ids:
            _used_ids.add(candidate)
            _prefix_counters[prefix] = counter
            return candidate
        counter += 1


def release_id(id: str):
    _used_ids.discard(id)
    # Note: Not adjusting _prefix_counters for simplicity


def reset_registry():
    _used_ids.clear()
    _prefix_counters.clear()


def _parse_prefix_number(id: str):
    """
    Parse prefix and trailing number from an ID like "Door 5"
    Returns (prefix:str, number:int|None)
    """
    parts = id.rsplit(" ", 1)
    if len(parts) == 2 and parts[1].isdigit():
        return parts[0], int(parts[1])
    return id, None
