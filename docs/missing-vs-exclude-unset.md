# `MISSING` vs `exclude_unset=True`

Both mechanisms control which fields are included when serializing a Pydantic model to JSON, but they operate at different layers and serve different purposes.

## `MISSING` sentinel

Many fields in `core_types.py` use `MISSING` (from `pydantic.experimental.missing_sentinel`) as their default:

```python
preAltPropUval: Annotated[float | None | MISSING, Field(ge=0.0)] = MISSING
```

This gives a field three distinct states:

| Value | Meaning |
|---|---|
| `1.5` | Server sent a real value |
| `None` | Server explicitly sent `null` |
| `MISSING` | Server omitted the key entirely |

On `model_dump(mode='json')`, Pydantic drops `MISSING` fields automatically — they are never included in the output and never sent back to the server.

## `exclude_unset=True`

`exclude_unset=True` is a Pydantic dump option that drops any field not explicitly assigned during construction. Pydantic tracks this via `__pydantic_fields_set__` — a set that records which fields the caller actually provided. It operates regardless of what default value a field holds.

## Where they diverge

**Fields with real defaults** — `MISSING` only protects fields that explicitly use it as their default. Fields with ordinary defaults (`0`, `""`, `False`, `None`) are still included unless `exclude_unset=True` is used:

```python
class Foo(BaseModel):
    name: str = "default"           # real default
    count: int | MISSING = MISSING  # sentinel default

f = Foo()  # neither field set by the caller

f.model_dump()                    # → {"name": "default"}   (count dropped, name included)
f.model_dump(exclude_unset=True)  # → {}                    (both dropped)
```

**Partial updates** — this is the critical case for `DataManager.update_item` and every outbound API call site. When building a model to describe only the fields you want to change, unset fields hold real defaults (`0`, `False`, etc.) — not `MISSING`. Only `exclude_unset=True` knows the caller never touched them:

```python
# Only want to change the roof type — everything else should be left alone
update = Roof(roofType=RoofTypeOptions.METAL_ROOF_WITH_THERMAL_BLOCKS)

update.model_dump(mode="json")                     # includes propUValue=0, grossArea=0, ...
update.model_dump(mode="json", exclude_unset=True) # → {"roofType": "METAL_ROOF_WITH_THERMAL_BLOCKS"}
```

## Summary

| | `MISSING` default | `exclude_unset=True` |
|---|---|---|
| Mechanism | sentinel value on the field | field-set tracking on the instance |
| Drops server-omitted fields | yes | yes (if server did not provide them) |
| Drops fields with real defaults | no | yes |
| Needed for partial updates | no | yes |

They complement each other. `MISSING` is for modeling fields the server may legitimately omit (keeping `None` and "absent" distinct). `exclude_unset=True` is for controlling the outbound payload based on what the caller explicitly set — which is why every API write call site in `comcheck_client.py`, `data_manager.py`, and `utilities/common.py` uses it.
