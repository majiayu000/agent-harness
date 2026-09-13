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

# Prefer AGENT_HARNESS_REPO_ROOT over the detected git root so every
# repository-specific diagnostic matches task_completed_gate.sh precedence.
# When outside a git worktree, fall back to CLAUDE_PLUGIN_ROOT/../.. the same
# way the gate does for plugins living inside a checkout.
resolve_effective_root() {
  if [ -n "${AGENT_HARNESS_REPO_ROOT:-}" ]; then
    if abs_root="$(CDPATH= cd -- "$AGENT_HARNESS_REPO_ROOT" && pwd)"; then
      printf '%s\n' "$abs_root"
      return 0
    fi
    return 1
  fi

  if git rev-parse --show-toplevel >/dev/null 2>&1; then
    git rev-parse --show-toplevel
    return 0
  fi

  if [ -n "${CLAUDE_PLUGIN_ROOT:-}" ]; then
    # Plugin root is plugins/agent-harness; repository root is two levels up when
    # the plugin lives inside the checkout. Prefer git when available (above).
    candidate="$(CDPATH= cd -- "$CLAUDE_PLUGIN_ROOT/../.." && pwd)"
    if [ -d "$candidate/.git" ] || [ -f "$candidate/.git" ]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  fi

  return 1
}

section "Agent Harness Doctor"

check_command git
check_command gh

root=""
root_resolved=0
if root="$(resolve_effective_root)"; then
  root_resolved=1
fi

section "Repository"

if [ "$root_resolved" -eq 1 ]; then
  branch="$(git -C "$root" branch --show-current 2>/dev/null || true)"
  head="$(git -C "$root" rev-parse --short HEAD 2>/dev/null || true)"
  upstream="$(git -C "$root" rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || true)"
  printf '%s\n' "- root: $root"
  if [ -n "${AGENT_HARNESS_REPO_ROOT:-}" ]; then
    printf '%s\n' "- root source: AGENT_HARNESS_REPO_ROOT"
  elif git rev-parse --show-toplevel >/dev/null 2>&1; then
    printf '%s\n' "- root source: git toplevel"
  else
    printf '%s\n' "- root source: CLAUDE_PLUGIN_ROOT fallback"
  fi
  printf '%s\n' "- branch: ${branch:-detached}"
  printf '%s\n' "- head: ${head:-unknown}"
  printf '%s\n' "- upstream: ${upstream:-none}"
  printf '%s\n' "- status:"
  git -C "$root" status --short || true
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

  repo_info=""
  if [ "$root_resolved" -eq 1 ]; then
    repo_info="$(CDPATH= cd -- "$root" && gh repo view --json nameWithOwner,url,defaultBranchRef,viewerPermission,hasIssuesEnabled,visibility 2>/dev/null || true)"
  else
    repo_info="$(gh repo view --json nameWithOwner,url,defaultBranchRef,viewerPermission,hasIssuesEnabled,visibility 2>/dev/null || true)"
  fi
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

checks_file=""
if [ "$root_resolved" -eq 1 ]; then
  checks_file="$root/.agent-harness/required-checks.txt"
fi

if [ -n "$checks_file" ] && [ -f "$checks_file" ]; then
  check_count="$(grep -Ev '^[[:space:]]*(#|$)' "$checks_file" | wc -l | tr -d ' ')"
  printf '%s\n' "- required checks: $check_count configured ($checks_file)"
elif [ -n "$checks_file" ]; then
  printf '%s\n' "- required checks: none configured at $checks_file"
  # Align with task_completed_gate.sh: enforcement fails closed when the
  # required-checks file is missing, so doctor must not report Ready.
  if [ "${AGENT_HARNESS_ENFORCE:-0}" = "1" ]; then
    status="Blocked"
  fi
else
  printf '%s\n' "- required checks: unavailable (repository root not resolved)"
  if [ "${AGENT_HARNESS_ENFORCE:-0}" = "1" ]; then
    status="Blocked"
  fi
fi

printf '%s\n' "- required-checks trust: repo-controlled .agent-harness/required-checks.txt is untrusted input"
printf '%s\n' "- enforcement: TaskCompleted gate runs checks only when AGENT_HARNESS_ENFORCE=1 (subject tags alone never enforce)"
printf '%s\n' "- execution: checks run as argv arrays against an allowlist / repo-relative executables; never via sh -lc"

section "Validation Hints"

# Only advertise validators under the effective root. After a root has been
# resolved (including via AGENT_HARNESS_REPO_ROOT), never fall back to the
# process CWD — that can advertise another checkout's scripts for this root.
if [ "$root_resolved" -eq 1 ] && [ -x "$root/scripts/validate.sh" ]; then
  printf '%s\n' "- possible: $root/scripts/validate.sh"
fi

for candidate in "make test" "make all" "npm test" "pnpm test" "bun test" "cargo test" "go test ./..." "pytest"; do
  cmd="${candidate%% *}"
  if command -v "$cmd" >/dev/null 2>&1; then
    printf '%s\n' "- possible: $candidate"
  fi
done

section "Result"
printf '%s\n' "$status"
