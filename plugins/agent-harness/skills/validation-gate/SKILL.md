---
description: Define and run validation before PR handoff or task completion.
---

# Validation Gate

Validation should prove the changed behavior, not just produce a green command.

## Selection

Choose validation in this order:

1. Ticket-provided validation or test plan.
2. Targeted test that exercises the changed code path.
3. Typecheck/lint/build for touched package.
4. Full repository gate when shared behavior or release-critical code changed.

## Evidence Format

Record:

- Command or manual path.
- Result.
- Relevant output summary.
- Timestamp if the run is long-lived or external.

## Required Behavior

- Run validation before push or PR handoff.
- If validation fails, fix and rerun unless the failure is unrelated and clearly documented.
- If validation cannot run, record why and what human action would unblock it.
- Never treat unrun validation as passed.

## Optional Repository Gate File

Projects can add `.agent-harness/required-checks.txt` with one shell command per line. Harness hooks
and agents should treat those commands as required before completing `[harness]` tasks.
