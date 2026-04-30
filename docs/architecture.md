# Architecture

Agent Harness is a Claude Code plugin, not a daemon.

The plugin owns the delivery procedure. Claude Code owns the agent loop, subagents, hooks, MCP
tools, and local shell execution. GitHub owns durable project state through issues, PRs, comments,
checks, and reviews. Bundled scripts own deterministic GitHub operations that should not depend on
prompt-following alone.

## Components

```text
commands/
  User-facing slash commands.

agents/
  Focused subagents for manager, research, execution, review, and landing.

skills/
  Reusable workflow contracts loaded by agents and commands.

hooks/
  Optional lifecycle gates. v0.2 keeps hooks conservative and opt-in.

scripts/
  Deterministic GitHub helpers used by hooks, skills, and commands.
```

## Runtime Boundary

Agent Harness intentionally does not poll forever, spawn its own workers, or keep an external
database. That belongs in an optional runner. The plugin focuses on the portable part of the
workflow:

```text
commands -> skills -> scripts -> GitHub state
```

The scripts are the hard edge:

- `workpad.py` creates or updates the single issue workpad comment.
- `pr_feedback_sweep.py` gathers PR reviews, inline comments, top-level comments, and checks.
- `doctor.sh` reports whether the current repository is ready for a harness run.

## Non-Goals For v0.2

- No always-on polling service.
- No Linear dependency.
- No custom database.
- No automatic merge without explicit user intent.

Those can be added later by a thin runner or GitHub Actions workflow without changing the core
plugin contract.
