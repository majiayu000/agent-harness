---
description: Land a GitHub PR after Agent Harness gates pass.
---

# Land PR

Use this only when the user has asked to land or merge a PR.

## Gate

Before merging:

1. Confirm PR exists and is open.
2. Confirm the branch is up to date or mergeable.
3. Run `pr-feedback-sweep`.
4. Confirm required checks are green on the latest head.
5. Confirm validation evidence is present in PR or workpad.

## Merge

Follow repository policy. Prefer the repo's configured merge strategy. If unknown, ask only when the
choice changes history or release behavior. Otherwise use the safest standard path for the repo.

After merge:

- Report merge result and PR URL.
- Do not delete branches unless repository policy or user request says to.
