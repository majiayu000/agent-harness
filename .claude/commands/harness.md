---
description: Local /harness alias for Agent Harness.
argument-hint: "[doctor|workpad|review|land] <github-url-or-number>"
---

# Harness

Use the installed Agent Harness plugin for `$ARGUMENTS`.

Follow the same routing as `/agent-harness:harness $ARGUMENTS`:

- No arguments or `doctor`: check local readiness.
- `workpad <issue>`: create or refresh the issue workpad.
- `review <pr>`: sweep PR feedback and checks.
- `land <pr>`: land only after feedback and checks are clean.
- Any GitHub issue URL or issue number: run the issue-to-PR delivery flow.

If the `agent-harness` plugin is not installed, report this blocker and show:

```text
/plugin marketplace add majiayu000/agent-harness
/plugin install agent-harness@agent-harness
```
