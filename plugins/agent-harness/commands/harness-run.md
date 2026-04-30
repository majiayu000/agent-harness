---
description: Run the Agent Harness GitHub issue-to-PR workflow.
argument-hint: "<github-issue-url-or-number>"
---

# Harness Run

Run the Agent Harness delivery flow for `$ARGUMENTS`.

Start by creating or refreshing the persistent GitHub issue workpad:

```sh
"${CLAUDE_PLUGIN_ROOT}/scripts/workpad.py" "$ARGUMENTS" --status "Harness run started"
```

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
