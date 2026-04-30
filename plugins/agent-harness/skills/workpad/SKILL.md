---
description: Maintain a persistent Agent Harness workpad in GitHub comments or local markdown.
---

# Workpad

The workpad is the source of truth for the agent run.

Prefer a single persistent GitHub issue comment headed `## Agent Harness Workpad`. If GitHub comment
write access is unavailable, use `.agent-harness/workpad.md` locally and mention that limitation in
the handoff.

## Required Sections

```md
## Agent Harness Workpad

### Environment
- Repo:
- Branch:
- HEAD:
- Workdir:

### Issue
- Link:
- Summary:

### Acceptance Criteria
- [ ] ...

### Plan
- [ ] ...

### Evidence
- ...

### Validation
- [ ] ...

### PR
- Link:
- Status:

### Blockers
- None
```

## Rules

- Update the same workpad; do not create a new progress comment each time.
- Keep checklist state accurate.
- Add evidence before claiming completion.
- Do not include secrets, tokens, or private logs.
- If the issue has explicit validation requirements, copy them into `Validation` as required
  checklist items.
