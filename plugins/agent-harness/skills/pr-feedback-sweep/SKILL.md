---
description: Sweep GitHub PR comments, review threads, and checks before handoff or landing.
---

# PR Feedback Sweep

Use this before declaring a pull request ready, and again before landing.

## Required Sources

Start with the bundled helper:

```sh
"${CLAUDE_PLUGIN_ROOT}/scripts/pr_feedback_sweep.py" <pr-url-or-number>
```

Gather all available feedback:

- PR summary and status.
- Review states.
- Top-level issue/PR comments.
- Inline review comments.
- Check runs and failing job logs when available.

Prefer GitHub MCP tools when available. Otherwise use `gh`:

```sh
gh pr view <pr> --json number,title,state,mergeable,reviewDecision,comments,reviews,commits,statusCheckRollup
gh api repos/{owner}/{repo}/pulls/<pr>/comments
gh pr checks <pr>
```

## Decision For Each Actionable Item

Use one of:

- `fix`: implement and rerun validation.
- `reply`: explain why no code change is needed.
- `defer`: create a follow-up issue only when the item is out of scope and non-blocking.
- `block`: stop because the feedback reveals a missing requirement or unsafe ambiguity.

## Handoff Rule

Do not move to ready-for-review or landed state while actionable feedback is unresolved.
