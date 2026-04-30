# Harness Workflow

This is the public workflow contract for Agent Harness v0.1.

## Issue To PR

1. Read the issue and repository state.
2. Create or update the `## Agent Harness Workpad` with `scripts/workpad.py`.
3. Prove the current behavior or locate the exact code path.
4. Create a focused branch.
5. Implement the narrow fix.
6. Run validation.
7. Open or update the PR.
8. Sweep feedback and checks with `scripts/pr_feedback_sweep.py`.
9. Handoff with PR URL, validation, and risks.

## Feedback Loop

Before handoff, all actionable PR feedback must be one of:

- fixed in code,
- answered with a justified pushback,
- converted into a follow-up issue when non-blocking and out of scope.

## Landing

Landing is a separate command because merge behavior is repository policy. The lander agent checks
feedback, checks, mergeability, and validation before merging.

## Deterministic Helpers

```sh
plugins/agent-harness/scripts/workpad.py <issue>
plugins/agent-harness/scripts/pr_feedback_sweep.py <pr>
plugins/agent-harness/scripts/doctor.sh
```

These helpers are intentionally small and inspectable. They turn the highest-risk GitHub reads and
writes into repeatable commands while leaving implementation judgment to Claude Code.
