# Agent Harness

Agent Harness is a GitHub-first Claude Code plugin for serious issue-to-PR delivery.

It does not try to be a background daemon in v0.1. Instead, it packages the engineering
workflow that makes coding agents useful: issue intake, workpad discipline, branch setup,
focused implementation, validation, PR feedback sweep, and landing.

## Why

Coding agents fail less because of model capability and more because the workflow around them is
loose. Agent Harness gives Claude Code a repeatable delivery frame:

```text
GitHub issue
  -> inspect and claim
  -> create branch/workpad
  -> reproduce or prove the requested signal
  -> plan
  -> implement
  -> validate
  -> open/update PR
  -> sweep reviews and checks
  -> hand off or land
```

## Install For Local Development

From this repository:

```sh
claude --plugin-dir ./plugins/agent-harness
```

Inside Claude Code, reload after edits:

```text
/reload-plugins
```

## Install From A GitHub Marketplace

After this repository is pushed to GitHub:

```text
/plugin marketplace add majiayu000/agent-harness
/plugin install agent-harness@agent-harness
```

Then run the namespaced commands:

```text
/agent-harness:harness-run https://github.com/majiayu000/agent-harness/issues/123
/agent-harness:harness-review 456
/agent-harness:harness-land 456
/agent-harness:harness-doctor
```

## Requirements

- Claude Code 2.1.123 or newer is recommended.
- `git` must be available.
- GitHub access must be available through either the GitHub plugin/MCP tools or `gh` CLI.
- Repository tests should be runnable from shell commands.

## What Is Included

- Commands:
  - `harness-run`: execute a GitHub issue through PR handoff.
  - `harness-review`: sweep PR comments, reviews, and checks.
  - `harness-land`: merge only after feedback and checks are clean.
  - `harness-doctor`: verify local prerequisites.
- Agents:
  - `manager`: coordinates the delivery.
  - `researcher`: read-only code and issue investigation.
  - `executor`: implements focused changes.
  - `reviewer`: read-only review and risk check.
  - `lander`: final PR landing loop.
- Skills:
  - `github-issue-flow`
  - `workpad`
  - `validation-gate`
  - `pr-feedback-sweep`
  - `handoff`
  - `land-pr`
- Hooks:
  - Optional task completion gate for harness tasks.

## Design Principle

Agent Harness is deliberately GitHub-first and tracker-light. Linear, Jira, and other trackers can
be added later as adapters, but v0.1 optimizes for the path most open-source users can try in five
minutes.
