# VALIDATE

## Purpose

VALIDATE in nlp2dsl checks a **workflow** (file or inline object), optionally
against policy. This is **validate-workflow**, not path/artifact validation.

It does **not** adopt
`https://wellmanifest.dev/schemas/dsl-commands/validate` (shared
**validate-path**: `verb` + `path`, used by doql/testql/vql). Same command
name, different contract — keep them separate.

## Syntax

See `packages/dsl2nlp2dsl/src/dsl2nlp2dsl/schema/commands/validate.schema.json` for the canonical JSON Schema contract.

## Inputs

- `verb`: `VALIDATE`
- `workflow_file` (optional): path to a workflow document
- `workflow` (optional): inline workflow object
- `check_policy` (optional, default false): whether to evaluate policy checks

## Outputs

Defined by the command schema.

## Errors

See `docs/ERROR/` for error codes.

## Examples

See `examples/` directory.
