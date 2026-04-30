#!/usr/bin/env sh
set -eu

root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
plugin="$root/plugins/agent-harness"

require_file() {
  path="$1"
  if [ ! -f "$path" ]; then
    printf 'missing required file: %s\n' "$path" >&2
    exit 1
  fi
}

require_executable() {
  path="$1"
  require_file "$path"
  if [ ! -x "$path" ]; then
    printf 'required script is not executable: %s\n' "$path" >&2
    exit 1
  fi
}

require_file "$root/.claude-plugin/marketplace.json"
require_file "$plugin/.claude-plugin/plugin.json"

for dir in commands agents skills hooks scripts; do
  if [ ! -d "$plugin/$dir" ]; then
    printf 'missing plugin directory: %s\n' "$plugin/$dir" >&2
    exit 1
  fi
done

require_executable "$plugin/scripts/doctor.sh"
require_executable "$plugin/scripts/task_completed_gate.sh"
require_executable "$plugin/scripts/workpad.py"
require_executable "$plugin/scripts/pr_feedback_sweep.py"

python3 - "$root" <<'PY'
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
marketplace = json.loads((root / ".claude-plugin" / "marketplace.json").read_text())
plugin = json.loads((root / "plugins" / "agent-harness" / ".claude-plugin" / "plugin.json").read_text())

assert marketplace["name"] == "agent-harness"
assert marketplace["plugins"][0]["name"] == plugin["name"] == "agent-harness"
assert marketplace["plugins"][0]["source"] == "./plugins/agent-harness"
assert plugin["version"]
assert plugin["repository"].startswith("https://github.com/")
PY

python3 -m py_compile \
  "$plugin/scripts/workpad.py" \
  "$plugin/scripts/pr_feedback_sweep.py"

if command -v claude >/dev/null 2>&1; then
  claude plugin validate "$plugin"
  claude plugin validate "$root"
else
  printf '%s\n' "claude CLI not found; skipped official plugin validation"
fi

printf '%s\n' "agent-harness validation passed"
