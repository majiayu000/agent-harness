---
description: Run Agent Harness from one short entrypoint.
argument-hint: "[doctor|workpad|review|land] <github-url-or-number>"
---

# Harness

Run Agent Harness for `$ARGUMENTS`.

Route by the first argument:

- No arguments or `doctor`: run `"${CLAUDE_PLUGIN_ROOT}/scripts/doctor.sh"` and report `Ready`,
  `Needs setup`, or `Blocked`.
- `workpad <issue>`: run `"${CLAUDE_PLUGIN_ROOT}/scripts/workpad.py" "<issue>"`, then report the
  workpad comment URL or exact blocker.
- `review <pr>`: run `"${CLAUDE_PLUGIN_ROOT}/scripts/pr_feedback_sweep.py" "<pr>"`, use the
  `agent-harness:reviewer` agent, and follow `pr-feedback-sweep`, `validation-gate`, and `handoff`.
- `land <pr>`: run
  `"${CLAUDE_PLUGIN_ROOT}/scripts/pr_feedback_sweep.py" "<pr>" --fail-on-blocking --fail-on-pending`,
  use the `agent-harness:lander` agent, and follow `land-pr`.
- Any GitHub PR URL: treat it as `review <pr>` unless the user explicitly asks to land.
- Anything else: treat the first non-flag argument as a GitHub issue and run the issue-to-PR flow.

For the issue-to-PR flow:

1. Create or refresh the persistent workpad:

   ```sh
   "${CLAUDE_PLUGIN_ROOT}/scripts/workpad.py" "$ARGUMENTS" --status "Harness run started"
   ```

2. Use the `agent-harness:manager` agent as the coordinator.
3. Follow `github-issue-flow`, `workpad`, `validation-gate`, `pr-feedback-sweep`, and `handoff`.

Required outcome:

- If the issue can be completed, produce or update a pull request with validation evidence.
- If feedback or checks are blocking, fix them or record the exact blocker.
- If credentials or repository permissions are missing, stop and report the missing prerequisite.
