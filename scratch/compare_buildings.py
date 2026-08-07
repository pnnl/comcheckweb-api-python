"""Compare building JSON exports against their Python (ComBuilding) round-trip.

The JSON -> ComBuilding -> JSON round-trip introduces a set of *known* /
expected differences (defaulted fields, dropped metadata like ``userProject``,
etc.). Those live in ``diff_ignore.json`` and are filtered out so that only
*new* discrepancies are surfaced when comparing additional buildings.

Usage
-----
Seed / update the ignore list from an existing diff file::

    python compare_buildings.py --update-ignore building_diff.json

Compare buildings (defaults to every ``*.json`` in ``buildings/`` if present,
otherwise ``building_json.json``)::

    python compare_buildings.py
    python compare_buildings.py path/to/one_building.json another.json

Get an actionable list of schema fixes for buildings that fail to validate::

    python compare_buildings.py --report

Two independent ignore lists (plain text, ``#`` for notes):
  - ``diff_ignore.txt``   -- round-trip diff paths (used by the default mode)
  - ``schema_ignore.txt`` -- validation failures to skip in ``--report``
"""

import argparse
import glob
import json
import os
import re
import sys
from collections import defaultdict
from typing import Any, Dict, List, Set, Tuple

from jsondiff import diff

from tools.generate_core_types import main as generate_core_types

IGNORE_FILE = "diff_ignore.txt"
# Separate ignore list for the --report (schema validation) mode. These are
# validation failures you've decided not to act on, kept apart from the
# round-trip diff ignore list since the two mean different things.
SCHEMA_IGNORE_FILE = "schema_ignore.txt"
BUILDINGS_GLOB = "buildings/*.json"
DEFAULT_BUILDING = "building_json.json"

# jsondiff (symmetric, marshalled) operator keys.
_INSERT_DELETE = ("$insert", "$delete")


def normalize_path(parts: Tuple[str, ...]) -> str:
    """Join a path, collapsing numeric array indices to ``[]``.

    Array positions vary between buildings, so an ignored discrepancy at
    ``hvac.hvacSystem.0.fanSystem`` should also match index ``1``, ``2``, ...
    """
    return ".".join("[]" if p.isdigit() else p for p in parts)


def walk_diff(d: Any, prefix: Tuple[str, ...] = ()) -> List[Tuple[str, str, Any]]:
    """Flatten a jsondiff (symmetric, marshalled) result into leaf findings.

    Returns a list of ``(normalized_path, op, value)`` tuples where ``op`` is
    one of ``insert``, ``delete``, ``replace`` or ``change``.
    """
    findings: List[Tuple[str, str, Any]] = []

    if isinstance(d, dict):
        for key, value in d.items():
            if key in _INSERT_DELETE:
                op = key.lstrip("$")  # "insert" / "delete"
                if isinstance(value, dict):
                    # Object keys added/removed.
                    for subkey, subval in value.items():
                        path = prefix + (str(subkey),)
                        findings.append((normalize_path(path), op, subval))
                elif isinstance(value, list):
                    # Array elements added/removed.
                    path = prefix + ("[]",)
                    for item in value:
                        findings.append((normalize_path(path), op, item))
                else:
                    findings.append((normalize_path(prefix), op, value))
            elif key == "$replace":
                findings.append((normalize_path(prefix), "replace", value))
            elif isinstance(key, str) and key.startswith("$"):
                # Any other operator ($update, etc.) -> recurse without
                # extending the path.
                findings.extend(walk_diff(value, prefix))
            else:
                findings.extend(walk_diff(value, prefix + (str(key),)))
    else:
        findings.append((normalize_path(prefix), "change", d))

    return findings


def load_ignore(ignore_file: str = IGNORE_FILE) -> Set[str]:
    """Load the set of normalized paths to ignore from ``ignore_file``.

    The ignore file is plain text: one path per line. Blank lines and anything
    after a ``#`` are treated as comments, so you can annotate entries inline
    (e.g. ``userProject  # dropped on purpose, not part of ComBuilding``).
    """
    if not os.path.exists(ignore_file):
        return set()
    paths: Set[str] = set()
    with open(ignore_file) as f:
        for line in f:
            entry = line.split("#", 1)[0].strip()
            if entry:
                paths.add(entry)
    return paths


def save_ignore(paths: Set[str]) -> None:
    """Append new paths to the ignore file, preserving existing notes/comments.

    Existing lines (including comments) are kept verbatim; only paths not
    already present are appended, so hand-written notes are never clobbered.
    """
    existing = load_ignore()
    new = sorted(p for p in paths if p not in existing)
    if not new:
        return
    header_needed = not os.path.exists(IGNORE_FILE)
    with open(IGNORE_FILE, "a") as f:
        if header_needed:
            f.write("# Diff paths to ignore (one per line). "
                    "Use '#' for inline notes.\n")
        for p in new:
            f.write(f"{p}\n")


def is_ignored(path: str, ignore: Set[str]) -> bool:
    """A path is ignored if it matches an ignore entry.

    An entry matches when it (a) equals the path, (b) is a prefix of it (so an
    ignored subtree covers its descendants), or (c) is a ``*.suffix`` wildcard
    that matches the trailing segment(s) at any depth -- e.g. ``*.listPosition``
    ignores ``listPosition`` wherever it appears.
    """
    for ig in ignore:
        if ig.startswith("*."):
            suffix = ig[1:]  # ".listPosition"
            if path == ig[2:] or path.endswith(suffix):
                return True
        elif path == ig or path.startswith(ig + "."):
            return True
    return False


def diff_building(building_json: Dict[str, Any]) -> Any:
    """Round-trip a building through ComBuilding and diff it against the raw JSON."""
    # Imported lazily: core_types is (re)generated by generate_core_types().
    from comcheck_api.types.core_types import ComBuilding

    building_python = ComBuilding(**building_json).model_dump(mode="json")
    return diff(building_python, building_json, marshal=True, syntax="symmetric")


def update_ignore(diff_files: List[str]) -> None:
    """Extend the ignore list with every leaf path found in ``diff_files``."""
    ignore = load_ignore()
    added: Set[str] = set()
    for path in diff_files:
        with open(path) as f:
            d = json.load(f)
        for norm_path, _op, _value in walk_diff(d):
            if norm_path and norm_path not in ignore:
                added.add(norm_path)
    ignore |= added
    save_ignore(ignore)
    print(f"Ignore list now has {len(ignore)} paths ({len(added)} added).")
    for path in sorted(added):
        print(f"  + {path}")


def compare(building_files: List[str]) -> int:
    """Compare each building JSON against its round-trip; report un-ignored diffs.

    Returns the total number of flagged (non-ignored) discrepancies.
    """
    generate_core_types()
    from pydantic import ValidationError

    ignore = load_ignore()
    schema_ignore = load_ignore(SCHEMA_IGNORE_FILE)
    # Definition names leak into Pydantic union-error paths; strip them.
    global _DEF_NAMES
    _DEF_NAMES = set(_load_schema().get("definitions", {}))
    total_flagged = 0

    errored = 0
    for path in building_files:
        with open(path) as f:
            building_json = json.load(f)

        try:
            raw_diff = diff_building(building_json)
        except ValidationError as exc:
            errored += 1
            total_flagged += 1
            print(f"\n=== {path} ===")
            # List the validation errors, noting any suppressed via the
            # schema ignore list rather than hiding them silently.
            shown, ignored = [], 0
            for err in exc.errors():
                _kind, epath, detail, _value = classify_error(err)
                if is_ignored(epath, schema_ignore):
                    ignored += 1
                else:
                    shown.append((epath, detail))
            print(f"  ! failed to validate as ComBuilding: "
                  f"{len(shown)} error(s), {ignored} ignored")
            for epath, detail in shown:
                print(f"    - {epath}: {detail}")
            continue
        except Exception as exc:  # non-validation failure
            errored += 1
            total_flagged += 1
            print(f"\n=== {path} ===")
            print(f"  ! failed to round-trip through ComBuilding: "
                  f"{type(exc).__name__}")
            first_line = str(exc).splitlines()[0] if str(exc) else ""
            if first_line:
                print(f"    {first_line}")
            continue

        findings = walk_diff(raw_diff)
        flagged = [f for f in findings if not is_ignored(f[0], ignore)]

        ignored_count = len(findings) - len(flagged)
        total_flagged += len(flagged)

        print(f"\n=== {path} ===")
        print(f"  {len(flagged)} flagged, {ignored_count} ignored")
        for norm_path, op, value in flagged:
            print(f"  [{op}] {norm_path} = {json.dumps(value, default=str)}")

    print(f"\nTotal flagged across {len(building_files)} building(s): "
          f"{total_flagged} ({errored} failed to round-trip)")
    return total_flagged


# --- Schema-fix report ------------------------------------------------------

# datamodel-codegen tags union branches in error locations, e.g.
# "fanEfficiencyExceptionType.str-enum[FanEfficiencyExceptionTypeOptions]" or
# "cavityRValue.float". These aren't real data keys, so we strip them when
# building a clean dotted path, but we mine them for the enum/type name.
_BRANCH_TAG = re.compile(r"^(str-enum|int-enum|enum)\[(?P<name>[^\]]+)\]$")
# Pydantic union-branch tags that are not real data keys: plain type names,
# ``list[Fan]`` / ``dict[...]`` shapes, etc.
_TYPE_BRANCH = {"str", "int", "float", "bool", "constrained-str", "list", "dict"}
_SHAPE_TAG = re.compile(r"^(list|dict|tuple)\[.*\]$")


# Populated by report() from the schema's definition names; these leak into
# Pydantic union-error locations (e.g. the "HVAC" in "hvac.HVAC.fanSystem").
_DEF_NAMES: Set[str] = set()


def _is_branch_tag(s: str) -> bool:
    return (
        s == "missing-sentinel"
        or _BRANCH_TAG.match(s) is not None
        or _SHAPE_TAG.match(s) is not None
        or s in _TYPE_BRANCH
        or s in _DEF_NAMES
    )


def _clean_loc(loc: Tuple[Any, ...]) -> str:
    """Turn a Pydantic error location into a normalized dotted path.

    Array indices collapse to ``[]`` and pydantic union-branch tags
    (``str-enum[...]``, ``list[Fan]``, ``.float``, ``missing-sentinel``) are
    dropped so the path reads as real data keys.
    """
    parts: List[str] = []
    for p in loc:
        if isinstance(p, int):
            parts.append("[]")
            continue
        s = str(p)
        if _is_branch_tag(s):
            continue
        parts.append(s)
    return ".".join(parts)


SCHEMA_FILE = os.path.join("comcheck_api", "schemas", "comCheck.schema.json")


def _load_schema() -> Dict[str, Any]:
    with open(SCHEMA_FILE) as f:
        return json.load(f)


def _deref(node: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    """Follow a ``$ref`` (if present) and return (target_node, definition_name)."""
    ref = node.get("$ref")
    if not ref:
        return node, ""
    name = ref.split("/")[-1]
    return schema.get("definitions", {}).get(name, {}), name


def resolve_schema_target(
    dotted_path: str, schema: Dict[str, Any]
) -> Tuple[str, str]:
    """Walk the schema along a cleaned data path.

    Returns ``(location, enum_def_name)`` where ``location`` is a string like
    ``definitions/AgWall -> properties/wallType`` pinpointing the node to edit,
    and ``enum_def_name`` is the ``*Options`` definition backing the field if
    it is an enum reference ("" for inline enums / non-enums). Returns
    ``("", "")`` when the path can't be resolved against the schema.
    """
    node = schema.get("definitions", {}).get("ComBuilding", {})
    def_name = "ComBuilding"      # the enclosing definition
    prop_seg = ""                 # the final property key within that definition
    enum_def = ""

    for seg in dotted_path.split("."):
        if seg == "[]":
            items = node.get("items") or node.get("item") or {}
            node, ref_name = _deref(items, schema)
            if ref_name:
                def_name, prop_seg = ref_name, ""
            continue
        props = node.get("properties", {})
        if seg not in props:
            return ("", "")  # path diverges (unknown / extra field)
        raw = props[seg]
        # Capture the enum def name from a $ref before dereferencing.
        ref = raw.get("$ref", "")
        target, ref_name = _deref(raw, schema)
        if ref_name and target.get("enum") is not None:
            enum_def = ref_name
        elif ref_name:
            # Non-enum sub-object: descend into it as the new enclosing def.
            def_name, prop_seg = ref_name, ""
            node = target
            continue
        node = target
        prop_seg = seg

    loc = f"definitions/{def_name}"
    if prop_seg:
        loc += f" -> properties/{prop_seg}"
    return (loc, enum_def)


def classify_error(err: Dict[str, Any]) -> Tuple[str, str, str, Any]:
    """Map one Pydantic error to (fix_kind, path, detail, offending_value).

    ``fix_kind`` is one of:
      - ``enum-missing-value``  : add the value to the enum ``*Options`` def
      - ``needs-null``          : field arrives as null but schema forbids it
      - ``constraint-too-strict`` : a min/max/etc. constraint rejects real data
      - ``other``               : anything not auto-classified
    """
    etype = err["type"]
    path = _clean_loc(err["loc"])
    value = err.get("input")

    # Which enum definition is implicated (from the branch tag), if any.
    enum_name = ""
    for p in err["loc"]:
        m = _BRANCH_TAG.match(str(p))
        if m:
            enum_name = m.group("name")
            break

    if etype == "enum":
        if value is None:
            return ("needs-null", path, "enum should allow null", value)
        target = enum_name or "<enum def>"
        return ("enum-missing-value", path,
                f"add {value!r} to enum '{target}'", value)

    if etype in ("string_type", "int_type", "float_type", "bool_type",
                 "int_parsing", "float_parsing") and value is None:
        return ("needs-null", path, "field arrives as null", value)

    if etype == "missing_sentinel_error":
        # Secondary branch of a union; the real story is told by the sibling
        # enum/type error. Mark as such so we can dedupe it away.
        return ("secondary", path, "union branch (see sibling error)", value)

    if etype in ("greater_than", "greater_than_equal", "less_than",
                 "less_than_equal", "multiple_of"):
        ctx = err.get("ctx", {})
        return ("constraint-too-strict", path,
                f"{etype} {ctx} rejects value {value!r}", value)

    return ("other", path, f"{etype}: {err.get('msg', '')}", value)


def report(building_files: List[str]) -> int:
    """Collect round-trip validation failures and print actionable schema fixes.

    Returns the number of distinct issues found.
    """
    generate_core_types()
    from comcheck_api.types.core_types import ComBuilding
    from pydantic import ValidationError

    # Pydantic injects the model class name as a path segment in union errors
    # (e.g. "hvac.HVAC.fanSystem..."). Those definition names aren't data keys,
    # so strip them before cleaning paths.
    global _DEF_NAMES
    _DEF_NAMES = set(_load_schema().get("definitions", {}))

    # Validation failures you've decided not to act on, kept in a file separate
    # from the round-trip diff ignore list.
    schema_ignore = load_ignore(SCHEMA_IGNORE_FILE)

    # fix_kind -> (path, detail) -> {values seen, files affected}
    issues: Dict[str, Dict[Tuple[str, str], Dict[str, set]]] = defaultdict(
        lambda: defaultdict(lambda: {"values": set(), "files": set()})
    )
    failed_files: Set[str] = set()
    ignored_count = 0

    for path in building_files:
        with open(path) as f:
            building_json = json.load(f)
        try:
            ComBuilding(**building_json)
        except ValidationError as exc:
            fname = os.path.basename(path)
            for err in exc.errors():
                kind, epath, detail, value = classify_error(err)
                if is_ignored(epath, schema_ignore):
                    ignored_count += 1
                    continue
                failed_files.add(path)
                bucket = issues[kind][(epath, detail)]
                if value is not None:
                    bucket["values"].add(repr(value)[:60])
                bucket["files"].add(fname)

    # Drop "secondary" union-branch noise where a real sibling error exists for
    # the same path (keeps the report focused on the actual fix).
    real_paths = {
        epath
        for kind in ("enum-missing-value", "needs-null", "constraint-too-strict")
        for (epath, _detail) in issues.get(kind, {})
    }
    for (epath, detail) in list(issues.get("secondary", {})):
        if epath in real_paths:
            del issues["secondary"][(epath, detail)]

    # --- render ---
    schema = _load_schema()
    print(f"\n{'=' * 70}")
    print(f"SCHEMA FIX REPORT  ({len(failed_files)}/{len(building_files)} "
          f"buildings failed to validate)")
    print(f"file: {SCHEMA_FILE}  (regenerate types after editing)")
    if ignored_count:
        print(f"({ignored_count} error(s) suppressed via {SCHEMA_IGNORE_FILE})")
    print(f"{'=' * 70}")

    order = [
        ("enum-missing-value", "1. MISSING ENUM VALUES  (add to the *Options enum)"),
        ("needs-null", "2. FIELDS THAT MUST ALLOW null  (use [\"<type>\", \"null\"])"),
        ("constraint-too-strict", "3. CONSTRAINTS TOO STRICT  (relax min/max)"),
        ("other", "4. OTHER  (needs manual review)"),
        ("secondary", "5. UNRESOLVED union-branch errors  (no sibling fix found)"),
    ]

    total_issues = 0
    for kind, header in order:
        entries = issues.get(kind, {})
        if not entries:
            continue
        print(f"\n{header}")
        print("-" * 70)
        for (epath, detail) in sorted(entries):
            info = entries[(epath, detail)]
            total_issues += 1
            vals = ", ".join(sorted(info["values"])[:6]) if info["values"] else ""
            nfiles = len(info["files"])
            loc, enum_def = resolve_schema_target(epath, schema)
            # Prefer the resolved enum definition name over the branch-tag guess.
            if kind == "enum-missing-value" and enum_def:
                detail = detail.replace("'<enum def>'", f"'{enum_def}'")
            print(f"  • {epath}")
            print(f"      fix: {detail}")
            if loc:
                where = loc
                if kind == "enum-missing-value" and enum_def:
                    where += f"  ->  definitions/{enum_def}/enum"
                print(f"      where: {where}")
            else:
                print("      where: <unresolved - field not found in schema; "
                      "may be an extra/renamed key>")
            if vals:
                print(f"      values seen: {vals}")
            print(f"      seen in {nfiles} file(s)")

    print(f"\n{'=' * 70}")
    print(f"{total_issues} distinct issue(s) to fix across "
          f"{len(failed_files)} failing building(s).")
    print(f"{'=' * 70}")
    return total_issues


def resolve_building_files(args_files: List[str]) -> List[str]:
    if args_files:
        return args_files
    globbed = sorted(glob.glob(BUILDINGS_GLOB))
    if globbed:
        return globbed
    return [DEFAULT_BUILDING]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--update-ignore",
        nargs="+",
        metavar="DIFF_JSON",
        help="Add every path in the given diff file(s) to the ignore list.",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Instead of diffing, classify round-trip validation failures "
        "into actionable schema fixes (missing enum values, nullable fields, "
        "over-strict constraints).",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Building JSON export files to compare "
        f"(default: {BUILDINGS_GLOB} or {DEFAULT_BUILDING}).",
    )
    args = parser.parse_args()

    if args.update_ignore:
        update_ignore(args.update_ignore)
        return

    if args.report:
        issues = report(resolve_building_files(args.files))
        sys.exit(1 if issues else 0)

    flagged = compare(resolve_building_files(args.files))
    sys.exit(1 if flagged else 0)


if __name__ == "__main__":
    main()
