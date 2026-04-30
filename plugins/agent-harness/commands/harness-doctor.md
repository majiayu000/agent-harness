---
description: Check whether the current repository can run the Agent Harness workflow.
argument-hint: ""
---

# Harness Doctor

Inspect the current repository and report readiness for Agent Harness.

Start by running:

```sh
"${CLAUDE_PLUGIN_ROOT}/scripts/doctor.sh"
```

Check:

- Current directory is inside a git repository.
- Working tree status and current branch.
- GitHub remote is configured.
- `gh auth status` works, or GitHub MCP tools are available.
- Repository has an obvious validation command.
- Claude Code can see the `agent-harness` agents and skills.

Return a concise readiness report with:

- `Ready`
- `Needs setup`
- `Blocked`
