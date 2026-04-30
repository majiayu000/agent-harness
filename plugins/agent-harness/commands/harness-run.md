---
description: Run the Agent Harness GitHub issue-to-PR workflow.
argument-hint: "<github-issue-url-or-number>"
---

# Harness Run

Run the Agent Harness delivery flow for `$ARGUMENTS`.

Use the `agent-harness:manager` agent as the coordinator. The coordinator must load and follow:

- `github-issue-flow`
- `workpad`
- `validation-gate`
- `pr-feedback-sweep`
- `handoff`

Required outcome:

- If the issue can be completed, produce or update a pull request with validation evidence.
- If blocked, leave a precise blocker note in the workpad and stop without inventing completion.
- Do not ask for next steps unless required credentials or permissions are missing.
