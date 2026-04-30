# Publishing

## Local Test

From the repository root:

```sh
claude --plugin-dir ./plugins/agent-harness
```

Inside Claude Code:

```text
/reload-plugins
/agent-harness:harness-doctor
```

## GitHub Marketplace

Push this repository to GitHub, then users can add it as a marketplace:

```text
/plugin marketplace add majiayu000/agent-harness
/plugin install agent-harness@agent-harness
```

The root `.claude-plugin/marketplace.json` exposes `plugins/agent-harness` as the installable
plugin.

## Release Versioning

The plugin currently pins `"version": "0.2.0"` in `plugins/agent-harness/.claude-plugin/plugin.json`.
Bump that version for each published release.
