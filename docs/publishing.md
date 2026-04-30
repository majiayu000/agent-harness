# Publishing

## Local Test

From the repository root:

```sh
claude --plugin-dir ./plugins/agent-harness
```

Inside Claude Code:

```text
/reload-plugins
/agent-harness:harness doctor
```

## GitHub Marketplace

Push this repository to GitHub, then users can add it as a marketplace:

```text
/plugin marketplace add majiayu000/agent-harness
/plugin install agent-harness@agent-harness
```

The root `.claude-plugin/marketplace.json` exposes `plugins/agent-harness` as the installable
plugin.

## Command Names

The primary command is:

```text
/agent-harness:harness <github-issue-url-or-number>
```

It also accepts:

```text
/agent-harness:harness workpad <github-issue-url-or-number>
/agent-harness:harness review <github-pr-url-or-number>
/agent-harness:harness land <github-pr-url-or-number>
/agent-harness:harness doctor
```

Claude Code automatically namespaces plugin commands. A published plugin cannot provide bare
`/harness`; this repository includes `.claude/commands/harness.md` as a local project alias for
that short form.

## Release Versioning

The plugin currently pins `"version": "0.0.2"` in `plugins/agent-harness/.claude-plugin/plugin.json`.
Bump that version for each published release.
