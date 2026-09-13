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

Projects can add `.agent-harness/required-checks.txt` with one command per line
(argv form: program plus arguments, no shell syntax).

### Trust boundary (SEC-07)

- That file is **repository-controlled and untrusted**. A compromised repo can plant
  hostile lines; the TaskCompleted hook must not treat it as operator intent.
- The hook enforces required checks **only** when `AGENT_HARNESS_ENFORCE=1` is set
  explicitly by the operator. Subject tags such as `[harness]` alone never trigger
  enforcement.
- Checks are resolved from the **git toplevel** (not process CWD).
- Lines are executed as **argv arrays** against an allowlisted set of tools or
  repo-relative executables. Freeform shell via `sh -lc` is not used.
- Prefer intentional local validation (`scripts/validate.sh`, package test commands)
  over relying on the lifecycle hook for security-sensitive gates.
