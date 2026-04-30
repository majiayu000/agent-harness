# Architecture

Agent Harness is a Claude Code plugin, not a daemon.

The plugin owns the delivery procedure. Claude Code owns the agent loop, subagents, hooks, MCP
tools, and local shell execution. GitHub owns the durable project state through issues, PRs,
comments, checks, and reviews.

## Components

```text
commands/
  User-facing slash commands.

agents/
  Focused subagents for manager, research, execution, review, and landing.

skills/
  Reusable workflow contracts loaded by agents and commands.

hooks/
  Optional lifecycle gates. v0.1 keeps hooks conservative and opt-in.

scripts/
  Small shell helpers used by hooks or commands.
```

## Non-Goals For v0.1

- No always-on polling service.
- No Linear dependency.
- No custom database.
- No automatic merge without explicit user intent.

Those can be added later by a thin runner or GitHub Actions workflow without changing the core
plugin contract.
