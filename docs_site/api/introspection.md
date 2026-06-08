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

## Introspection

::: comcheck_api.introspection

## Validation

::: comcheck_api.validation
