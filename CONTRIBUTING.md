# Contributing

Agent Harness is intentionally small: keep changes focused on making issue-to-PR delivery more
reliable inside Claude Code.

## Good First Contributions

- Better repository detection in `harness-doctor`.
- New workflow adapters for GitHub Projects, Linear, or Jira.
- More robust PR feedback collection examples.
- Documentation for real-world repository setups.

## Local Validation

Run:

```sh
scripts/validate.sh
```

If Claude Code is installed, the script also runs the official plugin validator.

## Design Rules

- Keep GitHub as the default path.
- Do not add a database or daemon to the plugin core.
- Keep merge behavior explicit.
- Prefer small skills, commands, and scripts that users can inspect.
