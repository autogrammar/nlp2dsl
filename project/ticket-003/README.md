# Ticket 003: fix-mcp-uv-source-paths

- **ID**: ticket-003
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-09-13

## Goal and scope

Fix stale `tool.uv.sources` path for `env2llm` (`../../semcod/env2llm` -> `../env2llm`) so `uv` installs resolve after the repository moved from `semcod/env2llm` to `autogrammar/env2llm`. Detected while restoring the `nlp2dsl` MCP server toolchain.

## Acceptance criteria

- [x] AC-01: `uv pip install -e .` resolves `env2llm` from `autogrammar/env2llm`.
- [x] AC-02: No other `../../` sibling paths remain stale in `pyproject.toml`.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-devin.md](ai-devin.md)
