---
description: GitHub issue-to-PR delivery workflow. Use when executing a GitHub issue through Agent Harness.
---

# GitHub Issue Flow

Use this skill to move a GitHub issue toward a validated pull request.

## Flow

1. Identify the issue.
   - Accept a GitHub issue URL, `owner/repo#number`, or issue number in the current repo.
   - Read title, body, labels, assignees, linked PRs, and recent comments.
2. Check repository state.
   - Record current branch, HEAD, remote, and dirty files.
   - If the working tree has unrelated changes, do not overwrite them.
3. Create or reuse a branch.
   - Prefer `agent-harness/issue-<number>-<slug>`.
   - Base new branches on the current default branch unless the user specified otherwise.
4. Create or update the workpad.
   - Use the `workpad` skill.
   - Capture issue summary, acceptance criteria, plan, validation, and status.
5. Reproduce or prove the issue signal.
   - Use a command output, failing test, screenshot, log, or direct code-path proof.
   - Record evidence before editing.
6. Implement narrowly.
   - Keep changes scoped to the issue.
   - File follow-up issues for meaningful out-of-scope work instead of expanding scope.
7. Validate.
   - Use `validation-gate`.
   - Run targeted checks first; run broader checks when the change touches shared behavior.
8. Open or update the pull request.
   - PR title must describe the shipped change.
   - PR body must include summary, validation, and risk.
   - Link the issue with a closing keyword when appropriate.
9. Sweep feedback.
   - Use `pr-feedback-sweep`.
10. Handoff.
   - Use `handoff`.

## Stop Conditions

Stop only when:

- The PR is ready for review.
- The change is landed by explicit request.
- A real blocker prevents progress, such as missing auth, missing secrets, unavailable required
  service, or ambiguous product intent with high risk.
