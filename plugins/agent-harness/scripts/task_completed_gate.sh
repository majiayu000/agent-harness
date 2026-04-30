#!/usr/bin/env sh
set -eu

input_file="$(mktemp)"
cat > "$input_file"

cleanup() {
  rm -f "$input_file"
}
trap cleanup EXIT

if ! command -v python3 >/dev/null 2>&1; then
  exit 0
fi

subject="$(python3 - "$input_file" <<'PY'
import json
import sys

try:
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        payload = json.load(f)
except Exception:
    print("")
    raise SystemExit(0)

print(payload.get("task_subject") or "")
PY
)"

case "${AGENT_HARNESS_ENFORCE:-0}:$subject" in
  1:*|*:"[harness]"*|*:"[Harness]"*)
    ;;
  *)
    exit 0
    ;;
esac

checks_file=".agent-harness/required-checks.txt"

if [ ! -f "$checks_file" ]; then
  exit 0
fi

failed=0

while IFS= read -r check || [ -n "$check" ]; do
  case "$check" in
    ""|\#*)
      continue
      ;;
  esac

  printf 'agent-harness: running required check: %s\n' "$check" >&2

  if ! sh -lc "$check"; then
    printf 'agent-harness: required check failed: %s\n' "$check" >&2
    failed=1
  fi
done < "$checks_file"

if [ "$failed" -ne 0 ]; then
  printf 'Agent Harness blocked task completion because required checks failed.\n' >&2
  exit 2
fi

exit 0
