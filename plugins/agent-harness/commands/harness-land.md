---
description: Land a validated PR after checks and review feedback are clean.
argument-hint: "<github-pr-url-or-number>"
---

# Harness Land

Run the Agent Harness landing loop for `$ARGUMENTS`.

Use the `agent-harness:lander` agent and follow the `land-pr` skill.

Required outcome:

- Confirm the PR exists and is open.
- Confirm there are no unresolved actionable review comments.
- Confirm required checks are green on the latest head.
- Merge only when the user has clearly authorized landing and repository policy allows it.
