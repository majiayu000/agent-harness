#!/usr/bin/env sh
set -eu

# Drain TaskCompleted hook stdin (JSON payload). Subject tags are intentionally
# ignored: repo-controlled text must not trigger enforcement by itself.
cat >/dev/null

# Required checks are untrusted repo content. Only run them when the operator
# explicitly opts in via AGENT_HARNESS_ENFORCE=1.
case "${AGENT_HARNESS_ENFORCE:-0}" in
  1)
    ;;
  *)
    exit 0
    ;;
esac

# Prefer an explicit override, then git toplevel, then a plugin-in-checkout
# fallback. Enforcement is already active here, so resolution failure is fatal.
resolve_repo_root() {
  if [ -n "${AGENT_HARNESS_REPO_ROOT:-}" ]; then
    # Canonicalize to an absolute path before constructing checks_file so a
    # relative override (e.g. target) does not double after cd "$root".
    if ! abs_root="$(CDPATH= cd -- "$AGENT_HARNESS_REPO_ROOT" && pwd)"; then
      return 1
    fi
    printf '%s\n' "$abs_root"
    return 0
  fi

  if root="$(git rev-parse --show-toplevel 2>/dev/null)"; then
    printf '%s\n' "$root"
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

if ! root="$(resolve_repo_root)"; then
  printf 'agent-harness: enforcement active but could not resolve repository root (set AGENT_HARNESS_REPO_ROOT or run inside a git checkout)\n' >&2
  exit 2
fi

checks_file="$root/.agent-harness/required-checks.txt"

if [ ! -f "$checks_file" ]; then
  printf 'agent-harness: enforcement active but required checks file missing: %s\n' "$checks_file" >&2
  exit 2
fi

# Allowlisted bare commands that may appear as argv[0]. Repo-relative executable
# paths under the git toplevel are also allowed after path-traversal checks.
is_allowlisted_command() {
  case "$1" in
    make|npm|pnpm|yarn|bun|cargo|go|pytest|python3|node)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

# Reject shell metacharacters so checks never go through a shell -c/-lc path.
# Also reject pathname globs (* ? []) so unquoted word-splitting cannot expand
# differently based on files in the execution directory.
has_shell_metacharacters() {
  case "$1" in
    *[\;\|\&\$\`\(\)\<\>\'\"\\*\?\[]* | *\]*)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

# Resolve argv[0] to an executable path under the git toplevel, or an allowlisted
# tool from PATH. Prints the resolved executable path on success.
resolve_check_executable() {
  cmd="$1"

  case "$cmd" in
    /*)
      printf 'agent-harness: refusing absolute-path required check: %s\n' "$cmd" >&2
      return 1
      ;;
    *)
      ;;
  esac

  if is_allowlisted_command "$cmd"; then
    if ! resolved="$(command -v "$cmd" 2>/dev/null)"; then
      printf 'agent-harness: allowlisted command not found on PATH: %s\n' "$cmd" >&2
      return 1
    fi
    printf '%s\n' "$resolved"
    return 0
  fi

  # Treat as a repo-relative executable path (e.g. scripts/validate.sh).
  case "$cmd" in
    ./*)
      rel="${cmd#./}"
      ;;
    *)
      rel="$cmd"
      ;;
  esac

  case "$rel" in
    *..*)
      printf 'agent-harness: refusing path traversal in required check: %s\n' "$cmd" >&2
      return 1
      ;;
  esac

  candidate="$root/$rel"
  if [ ! -f "$candidate" ] || [ ! -x "$candidate" ]; then
    printf 'agent-harness: required check is not an executable under git toplevel: %s\n' "$cmd" >&2
    return 1
  fi

  printf '%s\n' "$candidate"
  return 0
}

# Execute checks from the resolved repository root so subdirectory Makefiles or
# CWD-relative tools cannot bypass the root project's required checks.
CDPATH= cd -- "$root" || {
  printf 'agent-harness: cannot cd to repository root: %s\n' "$root" >&2
  exit 2
}

failed=0

while IFS= read -r check || [ -n "$check" ]; do
  # Trim leading whitespace so indented comments match doctor.sh's
  # '^[[:space:]]*(#|$)' exclusion and are not treated as argv.
  check="${check#"${check%%[![:space:]]*}"}"

  case "$check" in
    ""|\#*)
      continue
      ;;
  esac

  if has_shell_metacharacters "$check"; then
    printf 'agent-harness: refusing unsafe required check (shell metacharacters): %s\n' "$check" >&2
    failed=1
    continue
  fi

  # Intentional word-splitting into argv; shell metacharacters and globs already rejected.
  # shellcheck disable=SC2086
  set -- $check
  if [ "$#" -eq 0 ]; then
    continue
  fi

  if ! exe="$(resolve_check_executable "$1")"; then
    failed=1
    continue
  fi
  shift

  printf 'agent-harness: running required check: %s' "$exe" >&2
  if [ "$#" -gt 0 ]; then
    printf ' %s' "$@" >&2
  fi
  printf '\n' >&2

  if ! "$exe" "$@"; then
    printf 'agent-harness: required check failed: %s\n' "$exe" >&2
    failed=1
  fi
done < "$checks_file"

if [ "$failed" -ne 0 ]; then
  printf 'Agent Harness blocked task completion because required checks failed.\n' >&2
  exit 2
fi

exit 0
