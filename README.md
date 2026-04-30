# Agent Harness

Ship GitHub issues with Claude Code.

Agent Harness turns GitHub issues into validated pull requests with a repeatable delivery loop:
persistent workpads, focused branches, validation gates, PR feedback sweeps, and safe handoff.

## Why

Coding agents fail less because of model capability and more because the workflow around them is
loose. Agent Harness gives Claude Code a repeatable delivery frame with deterministic GitHub helper
scripts where the workflow should not rely on prompt-following alone:

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

Then run the main command:

```text
/agent-harness:harness https://github.com/majiayu000/agent-harness/issues/123
/agent-harness:harness workpad https://github.com/majiayu000/agent-harness/issues/123
/agent-harness:harness review 456
/agent-harness:harness land 456
/agent-harness:harness doctor
```

Claude Code namespaces plugin commands to avoid conflicts, so a marketplace plugin cannot directly
ship a bare `/harness` command. This repository includes `.claude/commands/harness.md` as a local
project alias, so a clone of this repo can use `/harness ...` directly after the plugin is loaded.
Other repositories can reuse that same alias file after installing the plugin.

## Requirements

- Claude Code 2.1.123 or newer is recommended.
- `git` must be available.
- GitHub access must be available through either the GitHub plugin/MCP tools or `gh` CLI.
- Repository tests should be runnable from shell commands.

## What Is Included

- Commands:
  - `harness`: one short entrypoint for issue runs, workpads, reviews, landing, and doctor checks.
  - `harness-run`: execute a GitHub issue through PR handoff.
  - `harness-workpad`: create or refresh the persistent GitHub issue workpad.
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
- Scripts:
  - `workpad.py`: create/update a single `## Agent Harness Workpad` issue comment.
  - `pr_feedback_sweep.py`: collect PR reviews, comments, inline comments, and check state.
  - `doctor.sh`: inspect local repo, GitHub auth, plugin files, and validation hints.

## Local Validation

```sh
scripts/validate.sh
```

## Design Principle

Agent Harness is deliberately GitHub-centered and tracker-light. Linear, Jira, and other trackers
can be added later as adapters, but the default path should work for most open-source repositories
in minutes.
