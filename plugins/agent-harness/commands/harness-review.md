---
description: Sweep PR comments, review threads, and checks, then decide required changes.
argument-hint: "<github-pr-url-or-number>"
---

# Harness Review

Run the Agent Harness PR feedback sweep for `$ARGUMENTS`.

Use the `agent-harness:reviewer` agent first for a read-only review. Then, if actionable feedback or
failing checks require code changes, use `agent-harness:executor` for the focused fix.

Follow the `pr-feedback-sweep`, `validation-gate`, and `handoff` skills.

Required outcome:

- Every actionable comment is either fixed or answered with a justified pushback.
- Checks are green or the exact blocking failure is recorded.
- The PR description and workpad reflect the current state.
