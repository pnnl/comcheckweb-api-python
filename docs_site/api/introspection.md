# Introspection & Validation

Runtime helpers for discovering what the SDK exposes and validating
project data — useful from notebooks, IDE plugins, and AI agents
alike. All return typed Pydantic models; call `.model_dump()` for
JSON-shaped output.

```python
import comcheck_api as cc

# What operation functions does the SDK ship?
for op in cc.list_operations():
    print(op.group, op.signature)

# What does the ComBuilding model look like?
schema = cc.lookup_type("ComBuilding")
if schema:
    for field in schema.fields:
        print(field.name, field.type, field.required)

# Does this dict satisfy the SDK schema?
result = cc.validate_project(project_dict)
if not result.ok:
    for err in result.errors:
        print(err.loc, err.msg)
```

- `list_operations` covers the project operation modules, grouped as
  `building_area`, `envelope`, `interior_lighting`, `exterior_lighting`,
  `mechanical`, `credits`, and `renewable`. `COMcheckClient` methods (API
  calls) are not included — see [COMcheckClient](client.md).
- `lookup_type` accepts any model or enum name from `comcheck_api.types`,
  including the `InteriorSpace` and `ExteriorArea` aliases. The match is
  case-insensitive; it returns `None` if nothing matches.
- `validate_project` checks the schema only (field types, required fields,
  enum values). Rules the project operations enforce, such as unique
  descriptions or a `fanSystemKey` that points to an existing fan system, are
  not checked.

## Introspection

::: comcheck_api.introspection

## Validation

::: comcheck_api.validation
