# Notes: comCheck.schema.json & Pydantic Generation Changes

Takeaways from the most recent round of changes to `comcheck_api/schemas/comCheck.schema.json`
and the Pydantic model generation.

## 1. Use `--use-missing-sentinel` for optional fields

Passing `--use-missing-sentinel` to the generator lets fields be marked with a `MISSING`
identifier instead of defaulting to a JSON value. When the model is exported back to JSON,
`MISSING` fields are omitted entirely.

**Why it matters:** we were hitting problems where fields that weren't present in the original
export would default to values we didn't want. The sentinel avoids inventing data — absent stays
absent on round-trip.

## 2. Avoid adding redundant `NONE` to enumerations

Adding `NONE` to enums caused a lot of churn, and in many cases an option that already means "none"
existed. Example: `SlabInsulationPositionOptions` already has `NO_INSULATION` **and** `NONE`.

**Action:** before adding `NONE`, check whether the enum already has an equivalent member and reuse it
rather than introducing a duplicate.

## 3. Allow `null` as a valid type for many fields

A lot of values arrive as `null` and should *not* be coerced to a default. To handle this correctly
we had to explicitly allow `null` as a type for many fields in the JSON schema.

## 4. Exemption types and activity types are likely incomplete

I added a number of exemption types and activity types, but I'm not confident the coverage is complete.

**Action:** cross-reference the enumeration directly in the backend code to confirm all valid
exemption/activity types are represented.

## 5. Put `null` inside the enumeration instead of `anyOf: [enum, null]`

Rather than repeating `anyOf: [enumeration, null]` across many fields, I added `null` directly to the
enumeration itself. This avoids repetition and is simpler to write.

**Note:** when the enum carries the type, you can also drop the `type` keyword on the field — the type
is inferred from the enumeration.

## 6. Reconsider `minimum` constraints

`minimum` flags caused failures — e.g. a building with `preAltPropUval` less than 0 failed schema
validation and couldn't be loaded into the `ComBuilding` object.

**Open question:** do we actually need `minimum` in the schema? It isn't necessarily enforced by the
backend, and its main effect right now is blocking otherwise-valid projects from loading. Consider
removing these unless the constraint is genuinely required.

## 7. Drop non-informative descriptions; prefer `title`

Many `description` fields just restate the field name and add nothing.

**Action:** remove descriptions that don't add information. If the text is just a formatted version of
the field name, use the `title` keyword instead of `description`.
