#!/usr/bin/env python3
"""Create or update an Agent Harness workpad comment on a GitHub issue."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

MARKER = "## Agent Harness Workpad"


def run(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, text=True, capture_output=True)
    if check and result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "command failed"
        raise SystemExit(f"{' '.join(args)}\n{message}")
    return result


def gh_json(args: list[str], *, check: bool = True) -> Any:
    result = run(["gh", *args], check=check)
    if result.returncode != 0 or result.stdout.strip() == "":
        return None
    return json.loads(result.stdout)


def current_repo() -> str:
    repo = run(["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"])
    return repo.stdout.strip()


def parse_issue(target: str, repo: str | None) -> tuple[str, int]:
    target = target.strip()

    url_match = re.search(r"github\.com/([^/]+)/([^/]+)/(?:issues|pull)/(\d+)", target)
    if url_match:
        owner, name, number = url_match.groups()
        return f"{owner}/{name}", int(number)

    shorthand_match = re.fullmatch(r"([^/\s]+/[^#\s]+)#(\d+)", target)
    if shorthand_match:
        parsed_repo, number = shorthand_match.groups()
        return parsed_repo, int(number)

    if re.fullmatch(r"\d+", target):
        return repo or current_repo(), int(target)

    raise SystemExit(
        "Issue target must be a GitHub issue URL, owner/repo#number, or issue number with --repo."
    )


def flatten_pages(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list) and payload and all(isinstance(page, list) for page in payload):
        return [item for page in payload for item in page]
    if isinstance(payload, list):
        return payload
    return []


def issue_comments(repo: str, number: int) -> list[dict[str, Any]]:
    payload = gh_json(
        [
            "api",
            f"repos/{repo}/issues/{number}/comments",
            "--paginate",
            "--slurp",
        ]
    )
    return flatten_pages(payload)


def find_workpad(comments: list[dict[str, Any]]) -> dict[str, Any] | None:
    candidates = [comment for comment in comments if MARKER in str(comment.get("body", ""))]
    candidates.sort(key=lambda comment: str(comment.get("created_at", "")), reverse=True)
    return candidates[0] if candidates else None


def git_value(args: list[str], fallback: str = "unknown") -> str:
    result = subprocess.run(["git", *args], text=True, capture_output=True)
    if result.returncode != 0:
        return fallback
    value = result.stdout.strip()
    return value or fallback


def build_default_body(repo: str, number: int, status: str | None) -> str:
    issue = gh_json(
        [
            "issue",
            "view",
            str(number),
            "--repo",
            repo,
            "--json",
            "number,title,state,url,labels,assignees",
        ]
    )

    labels = ", ".join(label["name"] for label in issue.get("labels", [])) or "None"
    assignees = ", ".join(user["login"] for user in issue.get("assignees", [])) or "None"
    branch = git_value(["branch", "--show-current"], "detached")
    head = git_value(["rev-parse", "--short", "HEAD"])
    workdir = os.getcwd()
    generated = dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()
    status_line = status or "Initialized"

    return f"""\
{MARKER}

### Environment
- Repo: {repo}
- Branch: {branch}
- HEAD: {head}
- Workdir: {workdir}
- Generated: {generated}

### Issue
- Link: {issue["url"]}
- Number: #{issue["number"]}
- State: {issue["state"]}
- Labels: {labels}
- Assignees: {assignees}
- Summary: {issue["title"]}

### Status
- {status_line}

### Acceptance Criteria
- [ ] Confirm scope from the issue.
- [ ] Capture reproduction or current-behavior evidence before editing.
- [ ] Complete the focused implementation.
- [ ] Run validation that proves the changed behavior.

### Plan
- [ ] Inspect issue and repository state.
- [ ] Sync from the expected base branch.
- [ ] Implement the smallest scoped change.
- [ ] Open or update the pull request.
- [ ] Sweep PR feedback and checks.

### Evidence
- Pending.

### Validation
- [ ] Pending.

### PR
- Link: Pending.
- Status: Pending.

### Blockers
- None.
"""


def upsert_comment(repo: str, number: int, body: str, *, replace: bool) -> tuple[str, dict[str, Any]]:
    comments = issue_comments(repo, number)
    existing = find_workpad(comments)

    if existing and not replace:
        return "reused", existing

    if existing and replace:
        return "updated", gh_json(
            [
                "api",
                "-X",
                "PATCH",
                f"repos/{repo}/issues/comments/{existing['id']}",
                "-f",
                f"body={body}",
            ]
        )

    return "created", gh_json(
        [
            "api",
            f"repos/{repo}/issues/{number}/comments",
            "-f",
            f"body={body}",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("issue", help="GitHub issue URL, owner/repo#number, or issue number")
    parser.add_argument("--repo", help="Repository in owner/name form")
    parser.add_argument("--body-file", type=Path, help="Markdown file to use as the complete workpad body")
    parser.add_argument("--replace", action="store_true", help="Replace the existing workpad comment")
    parser.add_argument("--status", help="Status line for the generated default body")
    parser.add_argument("--print-url", action="store_true", help="Print only the comment URL")
    args = parser.parse_args()

    repo, number = parse_issue(args.issue, args.repo)

    if args.body_file:
        body = args.body_file.read_text(encoding="utf-8")
        if MARKER not in body:
            body = f"{MARKER}\n\n{body.strip()}\n"
    else:
        body = build_default_body(repo, number, args.status)

    action, comment = upsert_comment(repo, number, body, replace=args.replace or bool(args.body_file))
    url = comment.get("html_url") or comment.get("url")

    if args.print_url:
        print(url or "")
    else:
        print(json.dumps({"repo": repo, "issue": number, "action": action, "comment_url": url}, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
