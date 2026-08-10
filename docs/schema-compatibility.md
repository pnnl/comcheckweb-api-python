# Schema Compatibility

The `comcheck_api` library bridges between the Python Pydantic models in `core_types.py` (generated from `comCheck.schema.json`) and the live COMcheck backend API. Because the server may return data that predates or diverges from the current schema, `CustomBaseModel` contains several sanitization layers that run automatically on every parse and serialize cycle.

This document describes each known compatibility issue, why it occurs, and how it is handled.

---

## Background: `MISSING` Sentinel

Many fields in the generated models use `MISSING` (from `pydantic.experimental.missing_sentinel`) as a default instead of `None`. A field with `= MISSING` means:

- **On parse:** the server did not include this field — the model holds `MISSING` rather than failing validation.
- **On serialize:** `model_dump(mode='json')` omits the key entirely — the server does not receive it.

This is the intentional "sparse update" pattern: only fields the server actually sent are round-tripped back. Issues arise when the server *requires* a field on write but omits it on read, or when `MISSING` leaks into the JSON payload.

---

## Issue 1 — `deepcopy` fails on models with `MISSING` fields

**Symptom:** `TypeError: Cannot pickle 'Sentinel' object` when calling `copy.deepcopy()` or `model.model_copy(deep=True)`.

**Root cause:** `MISSING` is a `typing_extensions.Sentinel` that is not picklable. Pydantic's `__deepcopy__` internally uses pickle for nested objects.

**Fix:** `CustomBaseModel.__deepcopy__` copies fields one-by-one, passing `MISSING` through unchanged rather than attempting to deep-copy it.

---

## Issue 2 — Boolean flags serialized as integers

**Symptom:** `HTTP 400: 'instance.isHistoricBuilding' is not of a type(s) boolean`

**Root cause:** The generated schema models boolean flags as `IntEnum` with values `{0, 1}` (e.g. `IsHistoricBuilding`, `CirculationPump`, `HeatTraceTapeInstalled`, `CombinedSystem`, `PoolSystem`). `model_dump(mode='json')` serializes them as integers; the server's JSON Schema validator requires `true`/`false`.

**Affected fields:** `isHistoricBuilding`, `allElectric`, `isRenewable`, `hasBattery`, `hasCharger`, `hasHeatPump`

**Fix:** `CustomBaseModel.model_dump` runs both a `mode='python'` and `mode='json'` dump, then walks them in parallel. Wherever the Python value is an `IntEnum` instance, the corresponding JSON integer is replaced with `bool(value)`.

---

## Issue 3 — Unknown enum values crash on parse

**Symptom:** `ValidationError: Input should be 'ACTIVITY_INVALID_USE', 'ACTIVITY_AUTO_REPAIR', ... [type=enum]` for a value like `'ACTIVITY_COMMON_OFFICE'`.

**Root cause:** Projects created under older schema versions may reference enum values that have since been renamed or removed (e.g. `ACTIVITY_COMMON_OFFICE` → `ACTIVITY_COMMON_OFFICE_OPEN`). The server stores these values verbatim and returns them unchanged.

**Fix — two-validator approach:**

Pydantic runs validators in order: `wrap` → `before` → field validation → `after`. This ordering is used to preserve the original value while still satisfying Pydantic's type checker:

1. **`_preserve_invalid_enum_strings` (`mode='wrap'`)** runs first. It inspects the raw input dict and stashes any string values that are not valid members of their declared `StrEnum` type.
2. **`_sanitize_server_data` (`mode='before'`)** runs next (inside the `handler` call). It replaces the unknown string with the first valid enum member so Pydantic can construct the model without raising a `ValidationError`.
3. After `handler()` returns the constructed model object, `_preserve_invalid_enum_strings` writes the original (unknown) string back onto the field using `object.__setattr__`, bypassing field validation entirely.

The result: the model field holds exactly what the server sent. `model_dump(mode='json')` serializes it as-is, so the value round-trips back to the server unchanged. A `WARNING` is still logged so the drift is visible.

```python
# Server returns an old enum value
project = client.get_project("project-id")
area = project.lighting.wholeBldgUse[0].activityUse[0]

print(area.activityType)  # 'ACTIVITY_COMMON_OFFICE'  ← original value preserved
print(type(area.activityType))  # <class 'str'>  ← not an enum member
```

> **Schema action needed:** When the backend migrates old records to use current enum values, this fallback will no longer be triggered.

---

## Issue 4 — Pydantic serializer `UserWarning` spam

**Symptom:** Dozens of `PydanticSerializationUnexpectedValue: Expected 'MISSING' sentinel` warnings on every `model_dump` call.

**Root cause:** Pydantic's built-in serializer emits a warning for each `SomeEnum | MISSING` union variant it tries during serialization.

**Fix:** `CustomBaseModel.model_dump` wraps both internal dump calls in `warnings.catch_warnings()` suppressing `UserWarning` from pydantic only. No behavior change.

---

## Issue 5 — Server sends negative sentinels for unset numeric fields

**Symptom:** `HTTP 400: 'instance.envelope.roof[1].continuousRValue' must be greater than or equal to 0`

**Root cause:** The server uses `-1` (and similar negative values like `-4.545`) as a "not set" sentinel on fields like `continuousRValue`, `propUValue`, `cavityRValue`. The server enforces `>= 0` on write but does not enforce it on read.

**Fix:** `CustomBaseModel._sanitize_server_data` replaces any incoming negative number with the field's declared `default` value, when that default is `>= 0`. A warning is logged.

**Schema fix applied:** Added `"minimum": 0.0` to the following fields in `comCheck.schema.json` where it was missing:

| Definition | Fields updated |
|---|---|
| `AboveGradeWall` (all 3 definitions) | `cavityRValue`, `continuousRValue`, `propUValue`, `grossArea` |
| `BelowGradeWall` | `cavityRValue`, `continuousRValue` |
| `Window` | `cavityRValue`, `continuousRValue` |
| `Door` | `cavityRValue`, `continuousRValue` |
| `Skylight` | `cavityRValue`, `continuousRValue` |
| `Roof` (second definition) | `cavityRValue`, `continuousRValue`, `propUValue` |

---

## Issue 6 — `MISSING` fields included in outbound JSON payload

**Symptom:** `HTTP 400: 'instance.lighting.wholeBldgUse[0].allowedWattage' is not of a type(s) number`

**Root cause:** `MISSING` fields — those the server never sent — were being included in `model_dump(mode='json')` output as unexpected non-typed values (not `null`, not a number). The server's JSON Schema validator rejected them.

**Fix:** The `model_dump` post-processing step (which already diffs Python vs JSON output for Issue 2) now also drops any key whose Python-side value is `MISSING`. The field is simply omitted from the outbound payload.

---

## Issue 7 — `allowanceType` absent on GET, required on PUT

**Symptom:** `ValidationError: Field required [type=missing]` on parse, then `HTTP 400: requires property "allowanceType"` on PUT.

**Root cause:** The server omits `allowanceType` for older envelope records (sends `null` or omits the key entirely), but its write validator requires the field to be present with a valid string value. The field type is `EnvelopeAssemblyAllowanceTypeOptions | MISSING`.

**Affected components:** `AgWall`, `BgWall`, `Window`, `Door`, `Skylight`, `Roof`

**Fix — inbound (parse):** `_sanitize_server_data` maps an incoming `null` for a non-nullable enum field to the first non-null enum member. For `EnvelopeAssemblyAllowanceTypeOptions`, this is `ENV_ALLOWANCE_NONE`.

**Fix — schema:** Removed `allowanceType` from the `required` arrays of all six component definitions in `comCheck.schema.json`. The field remains defined in `properties` — it is optional on read, required on write (enforced by the server).

> **Note:** This is a server-side inconsistency. The long-term fix is for the server to always populate `allowanceType` when returning records, and for the schema to reflect that it is always present. Once the server is updated, the `required` entries can be restored.

---

## Issue 8 — `null` values dropped for non-optional enum fields

**Symptom:** Fields like `adjacentSpaceType`, `exemptionType` (typed as `SomeEnum`, not `SomeEnum | None`) arrive as `null` from the server, causing the Pydantic model to lose them.

**Root cause:** The server sends `null` for fields it considers "not set" even when the generated schema does not allow `null`. The `_sanitize_server_data` validator was dropping these fields (reverting to `MISSING`), which then caused serialization failures or missing required fields on write.

**Fix:** When the field has an enum with a `None`-valued member (`NoneType_None = None`), the incoming `null` is mapped to that enum member rather than dropped. When no such member exists, the field is dropped and a warning is logged.

---

## Summary of `comCheck.schema.json` changes

All changes align the schema with the server's actual write-time validation behavior:

| Change | Location | Reason |
|---|---|---|
| Added `"minimum": 0.0` | `cavityRValue`, `continuousRValue` in all envelope definitions | Server rejects negative values on write |
| Added `"minimum": 0.0` | `propUValue` in Roof (alt definition), AgWall (alt definitions) | Server rejects negative values on write |
| Added `"minimum": 0.0` | `grossArea` in first AgWall definition | Consistent with all other `grossArea` definitions |
| Removed `allowanceType` from `required` | AgWall, BgWall, Window, Door, Skylight, Roof | Server omits this field on read for older records |

---

## Logging

All sanitization actions emit `WARNING`-level log messages via `comcheck_api.types.custom_base_model`. To see them:

```python
import logging
logging.basicConfig(level=logging.WARNING)
```

Example output:
```
WARNING  comcheck_api.types.custom_base_model:custom_base_model.py:142
  Replacing unknown enum value 'ACTIVITY_COMMON_OFFICE' with fallback 'ACTIVITY_INVALID_USE'
  for field ActivityUse.activityType

WARNING  comcheck_api.types.custom_base_model:custom_base_model.py:160
  Replacing server sentinel -1 with default 0.0 for field Roof.continuousRValue
```
