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
  printf '%s\n' "- root: $root"
  printf '%s\n' "- branch: ${branch:-detached}"
  printf '%s\n' "- head: ${head:-unknown}"
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
fi

section "Validation Hints"

for candidate in "make test" "make all" "npm test" "pnpm test" "bun test" "cargo test" "go test ./..." "pytest"; do
  cmd="${candidate%% *}"
  if command -v "$cmd" >/dev/null 2>&1; then
    printf '%s\n' "- possible: $candidate"
  fi
done

section "Result"
printf '%s\n' "$status"
