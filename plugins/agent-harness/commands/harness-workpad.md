---
description: Create or refresh the persistent Agent Harness workpad comment for a GitHub issue.
argument-hint: "<github-issue-url-or-number>"
---

# Harness Workpad

Create or update the persistent Agent Harness workpad for `$ARGUMENTS`.

Start with:

```sh
"${CLAUDE_PLUGIN_ROOT}/scripts/workpad.py" "$ARGUMENTS"
```

Then report the workpad comment URL. If the command fails because GitHub auth or issue access is
missing, report the exact blocker.
