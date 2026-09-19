# Ticket 005: Adopt wellmanifest/new-project 0.20.35

- **ID**: ticket-005
- **Owner**: tom@sapletta.com
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-09-19

## Goal and scope

Adopt `wellmanifest/new-project` governance pack version `0.20.35` (source revision `cfaa0bf0ea6b0e7349fed0bb62b5ce15792d687d`).
- Upgrade `.governance/` governance files using `create_adoption_lock.py --upgrade`.
- Pin container image base digest in `Dockerfile` and `Dockerfile.e2e`.
- Update `pyproject.toml` with `wellman>=0.20.35` dependency and `[tool.wellmanifest]` table.
- Adhere to `wellmanifest/worktrees` standard v5 for worktree isolation.
- Verify deterministic governance check and real-time standards check via `wellman check`.

## Acceptance criteria

- [ ] AC-01: Standard adoption lock is synchronized to `0.20.35` at `cfaa0bf0ea6b0e7349fed0bb62b5ce15792d687d`.
- [ ] AC-02: `pyproject.toml` contains `wellman>=0.20.35` in dev and governance dependency groups, and `[tool.wellmanifest]`.
- [ ] AC-03: `bash project/governance-check.sh` passes without errors.
- [ ] AC-04: `wellman check` verifies standard conformance.
