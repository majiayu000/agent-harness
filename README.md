# Agent Harness

A Claude Code plugin for shipping GitHub issues through validated pull requests.
This repository is [majiayu000/agent-harness](https://github.com/majiayu000/agent-harness); it is distinct from the [Rust Harness control plane](https://github.com/majiayu000/harness).

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

Clone the repository, then load the plugin:

```sh
git clone https://github.com/majiayu000/agent-harness.git
cd agent-harness
claude --plugin-dir ./plugins/agent-harness
```

Inside Claude Code, reload after edits:

```text
/reload-plugins
```

## Install From A GitHub Marketplace

Inside Claude Code:

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

## First Issue Run And Common Blockers

Open Claude Code in the target repository with the plugin installed. Start with
`/agent-harness:harness doctor`; resolve any missing GitHub access or validation
prerequisites it reports. Choose a real issue in that repository whose expected
behavior and check command are clear, then run:

```text
/agent-harness:harness <full-url-of-your-github-issue>
```

The issue flow creates or refreshes one persistent workpad, investigates the
requested signal, implements on a focused branch, validates, and opens or updates
its PR. The workpad and PR contain the evidence or exact blocker; a command
invocation alone does not prove delivery. See the [issue flow](plugins/agent-harness/skills/github-issue-flow/SKILL.md),
[validation gate](plugins/agent-harness/skills/validation-gate/SKILL.md), and
[handoff](plugins/agent-harness/skills/handoff/SKILL.md) contracts.

**The command is missing.** Use the namespaced `/agent-harness:harness` after
marketplace installation. A bare `/harness` is this repository's local alias,
not a globally installed plugin command. For local plugin edits, run
`/reload-plugins`; see [Claude Code's plugin documentation](https://code.claude.com/docs/en/plugins).

**GitHub access is blocked.** Doctor reports the missing prerequisite. GitHub
plugin/MCP access or authenticated `gh` must be available with the repository
permissions the operation needs. Do not paste credentials into the workpad.

**Review or CI is still pending.** Run `/agent-harness:harness review <pr-number>`
for the feedback sweep. `land` is a separate explicit merge request and must pass
its blocking/pending checks; it is not a way around failing CI. See the
[landing contract](plugins/agent-harness/skills/land-pr/SKILL.md).

**Is this a GitHub Action or hosted service?** No. This is a Claude Code plugin
loaded in your repository session. Anthropic's [Claude Code GitHub Actions](https://code.claude.com/docs/en/github-actions)
is a separate workflow integration. This plugin does not require a new daemon or
tracker database.

For bugs, use [Issues](https://github.com/majiayu000/agent-harness/issues) with the
plugin and Claude Code versions, the command, and redacted evidence. Installation
and update metadata live in the [plugin manifest](plugins/agent-harness/.claude-plugin/plugin.json)
and [marketplace manifest](.claude-plugin/marketplace.json). The source is under
[MIT](LICENSE).

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
