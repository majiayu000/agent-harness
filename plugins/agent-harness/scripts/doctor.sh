#!/usr/bin/env sh
set -eu

status="Ready"

section() {
  printf '\n## %s\n' "$1"
}

check_command() {
  name="$1"
  if command -v "$name" >/dev/null 2>&1; then
    printf '%s\n' "- $name: ok"
  else
    printf '%s\n' "- $name: missing"
    status="Needs setup"
  fi
}

section "Agent Harness Doctor"

check_command git
check_command gh

section "Repository"

if git rev-parse --show-toplevel >/dev/null 2>&1; then
  root="$(git rev-parse --show-toplevel)"
  branch="$(git branch --show-current 2>/dev/null || true)"
  head="$(git rev-parse --short HEAD 2>/dev/null || true)"
  upstream="$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || true)"
  printf '%s\n' "- root: $root"
  printf '%s\n' "- branch: ${branch:-detached}"
  printf '%s\n' "- head: ${head:-unknown}"
  printf '%s\n' "- upstream: ${upstream:-none}"
  printf '%s\n' "- status:"
  git status --short || true
else
  printf '%s\n' "- git repository: missing"
  status="Blocked"
fi

section "GitHub"

if command -v gh >/dev/null 2>&1; then
  if gh auth status >/dev/null 2>&1; then
    printf '%s\n' "- gh auth: ok"
  else
    printf '%s\n' "- gh auth: unavailable"
    status="Needs setup"
  fi

  repo_info="$(gh repo view --json nameWithOwner,url,defaultBranchRef,viewerPermission,hasIssuesEnabled,visibility 2>/dev/null || true)"
  if [ -n "$repo_info" ] && command -v python3 >/dev/null 2>&1; then
    REPO_INFO="$repo_info" python3 - <<'PY'
import json
import os
import sys

payload = json.loads(os.environ["REPO_INFO"])
default_branch = (payload.get("defaultBranchRef") or {}).get("name") or "unknown"
print(f"- repo: {payload.get('nameWithOwner') or 'unknown'}")
print(f"- url: {payload.get('url') or 'unknown'}")
print(f"- visibility: {payload.get('visibility') or 'unknown'}")
print(f"- default branch: {default_branch}")
print(f"- viewer permission: {payload.get('viewerPermission') or 'unknown'}")
print(f"- issues enabled: {payload.get('hasIssuesEnabled')}")
PY
  else
    printf '%s\n' "- repo: unavailable"
    status="Needs setup"
  fi
fi

section "Agent Harness"

plugin_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
for required in \
  "$plugin_root/.claude-plugin/plugin.json" \
  "$plugin_root/scripts/workpad.py" \
  "$plugin_root/scripts/pr_feedback_sweep.py" \
  "$plugin_root/scripts/task_completed_gate.sh"; do
  if [ -f "$required" ]; then
    printf '%s\n' "- $(basename "$required"): present"
  else
    printf '%s\n' "- $(basename "$required"): missing"
    status="Needs setup"
  fi
done

if [ -f ".agent-harness/required-checks.txt" ]; then
  check_count="$(grep -Ev '^[[:space:]]*(#|$)' .agent-harness/required-checks.txt | wc -l | tr -d ' ')"
  printf '%s\n' "- required checks: $check_count configured"
else
  printf '%s\n' "- required checks: none configured"
fi

section "Validation Hints"

if [ -x "scripts/validate.sh" ]; then
  printf '%s\n' "- possible: scripts/validate.sh"
fi

for candidate in "make test" "make all" "npm test" "pnpm test" "bun test" "cargo test" "go test ./..." "pytest"; do
  cmd="${candidate%% *}"
  if command -v "$cmd" >/dev/null 2>&1; then
    printf '%s\n' "- possible: $candidate"
  fi
done

section "Result"
printf '%s\n' "$status"
