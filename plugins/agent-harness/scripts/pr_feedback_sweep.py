#!/usr/bin/env python3
"""Collect PR reviews, comments, inline comments, and check status with gh."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from typing import Any


def run(args: list[str], *, allowed: set[int] | None = None) -> subprocess.CompletedProcess[str]:
    allowed = allowed or {0}
    result = subprocess.run(args, text=True, capture_output=True)
    if result.returncode not in allowed:
        message = result.stderr.strip() or result.stdout.strip() or "command failed"
        raise SystemExit(f"{' '.join(args)}\n{message}")
    return result


def gh_json(args: list[str], *, allowed: set[int] | None = None) -> Any:
    result = run(["gh", *args], allowed=allowed)
    if result.stdout.strip() == "":
        return None
    return json.loads(result.stdout)


def current_repo() -> str:
    return run(["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"]).stdout.strip()


def parse_pr(target: str, repo: str | None) -> tuple[str, str, int]:
    target = target.strip()

    url_match = re.search(r"github\.com/([^/]+)/([^/]+)/pull/(\d+)", target)
    if url_match:
        owner, name, number = url_match.groups()
        return f"{owner}/{name}", target, int(number)

    shorthand_match = re.fullmatch(r"([^/\s]+/[^#\s]+)#(\d+)", target)
    if shorthand_match:
        parsed_repo, number = shorthand_match.groups()
        return parsed_repo, number, int(number)

    if re.fullmatch(r"\d+", target):
        resolved_repo = repo or current_repo()
        return resolved_repo, target, int(target)

    return repo or current_repo(), target, -1


def flatten_pages(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list) and payload and all(isinstance(page, list) for page in payload):
        return [item for page in payload for item in page]
    if isinstance(payload, list):
        return payload
    return []


def pr_view(repo: str, target: str) -> dict[str, Any]:
    return gh_json(
        [
            "pr",
            "view",
            target,
            "--repo",
            repo,
            "--json",
            "number,title,state,url,isDraft,mergeable,reviewDecision,reviews,comments,statusCheckRollup,headRefName,baseRefName",
        ]
    )


def inline_comments(repo: str, number: int) -> list[dict[str, Any]]:
    payload = gh_json(
        [
            "api",
            f"repos/{repo}/pulls/{number}/comments",
            "--paginate",
            "--slurp",
        ]
    )
    return flatten_pages(payload)


def check_runs(repo: str, target: str) -> list[dict[str, Any]]:
    payload = gh_json(
        [
            "pr",
            "checks",
            target,
            "--repo",
            repo,
            "--json",
            "name,state,bucket,link,workflow,description,startedAt,completedAt",
        ],
        allowed={0, 1, 8},
    )
    return payload if isinstance(payload, list) else []


def classify(summary: dict[str, Any]) -> dict[str, list[str]]:
    blocking: list[str] = []
    pending: list[str] = []
    informational: list[str] = []

    pr = summary["pr"]
    review_decision = pr.get("reviewDecision") or None
    if pr.get("state") != "OPEN":
        blocking.append(f"PR is not open: {pr.get('state')}")
    if pr.get("isDraft"):
        pending.append("PR is still draft")
    if pr.get("mergeable") == "CONFLICTING":
        blocking.append("PR has merge conflicts")
    if review_decision == "CHANGES_REQUESTED":
        blocking.append("Review decision is CHANGES_REQUESTED")
    if pr.get("state") == "OPEN" and review_decision in {"REVIEW_REQUIRED", None}:
        pending.append(f"Review decision is {review_decision or 'unset'}")

    for check in summary["checks"]:
        bucket = check.get("bucket")
        name = check.get("name") or "unnamed check"
        if bucket in {"fail", "cancel"}:
            blocking.append(f"Check {name} is {bucket}")
        elif bucket == "pending":
            pending.append(f"Check {name} is pending")

    if summary["inline_comments_count"]:
        informational.append(
            f"{summary['inline_comments_count']} inline review comments need human/model classification"
        )
    if summary["top_level_comments_count"]:
        informational.append(
            f"{summary['top_level_comments_count']} top-level comments need human/model classification"
        )

    return {"blocking": blocking, "pending": pending, "informational": informational}


def build_summary(repo: str, target: str, number_hint: int) -> dict[str, Any]:
    pr = pr_view(repo, target)
    number = int(pr.get("number") or number_hint)
    comments = pr.get("comments") or []
    reviews = pr.get("reviews") or []
    inline = inline_comments(repo, number)
    checks = check_runs(repo, str(number))

    summary = {
        "repo": repo,
        "pr": pr,
        "reviews_count": len(reviews),
        "top_level_comments_count": len(comments),
        "inline_comments_count": len(inline),
        "checks": checks,
        "reviews": reviews,
        "top_level_comments": comments,
        "inline_comments": inline,
    }
    summary["classification"] = classify(summary)
    return summary


def comment_excerpt(comment: dict[str, Any]) -> str:
    body = str(comment.get("body") or "").strip().replace("\r", "")
    first_line = body.splitlines()[0] if body else ""
    if len(first_line) > 140:
        first_line = first_line[:137] + "..."
    author = (comment.get("author") or {}).get("login") or comment.get("user", {}).get("login") or "unknown"
    return f"{author}: {first_line or '(empty comment)'}"


def render_markdown(summary: dict[str, Any]) -> str:
    pr = summary["pr"]
    lines = [
        "# Agent Harness PR Feedback Sweep",
        "",
        f"- Repo: {summary['repo']}",
        f"- PR: #{pr.get('number')} {pr.get('title')}",
        f"- URL: {pr.get('url')}",
        f"- State: {pr.get('state')}",
        f"- Review decision: {pr.get('reviewDecision') or 'unset'}",
        f"- Mergeable: {pr.get('mergeable') or 'unknown'}",
        f"- Checks: {len(summary['checks'])}",
        f"- Reviews: {summary['reviews_count']}",
        f"- Top-level comments: {summary['top_level_comments_count']}",
        f"- Inline comments: {summary['inline_comments_count']}",
        "",
    ]

    for title, key in [
        ("Blocking", "blocking"),
        ("Pending", "pending"),
        ("Needs Classification", "informational"),
    ]:
        lines.append(f"## {title}")
        items = summary["classification"][key]
        lines.extend([f"- {item}" for item in items] or ["- None"])
        lines.append("")

    if summary["reviews"]:
        lines.append("## Review Summaries")
        for review in summary["reviews"]:
            author = (review.get("author") or {}).get("login") or "unknown"
            state = review.get("state") or "UNKNOWN"
            submitted = review.get("submittedAt") or review.get("submitted_at") or ""
            lines.append(f"- {state} by {author} {submitted}".rstrip())
        lines.append("")

    if summary["top_level_comments"]:
        lines.append("## Top-Level Comment Excerpts")
        for comment in summary["top_level_comments"][:20]:
            lines.append(f"- {comment_excerpt(comment)}")
        lines.append("")

    if summary["inline_comments"]:
        lines.append("## Inline Comment Excerpts")
        for comment in summary["inline_comments"][:20]:
            path = comment.get("path") or "unknown path"
            line = comment.get("line") or comment.get("original_line") or "?"
            lines.append(f"- {path}:{line} {comment_excerpt(comment)}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pr", help="PR URL, number, branch, or owner/repo#number")
    parser.add_argument("--repo", help="Repository in owner/name form")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--fail-on-blocking", action="store_true")
    parser.add_argument("--fail-on-pending", action="store_true")
    args = parser.parse_args()

    repo, target, number_hint = parse_pr(args.pr, args.repo)
    summary = build_summary(repo, target, number_hint)

    if args.format == "json":
        print(json.dumps(summary, indent=2))
    else:
        print(render_markdown(summary), end="")

    blocking = bool(summary["classification"]["blocking"])
    pending = bool(summary["classification"]["pending"])
    if args.fail_on_blocking and blocking:
        return 2
    if args.fail_on_pending and (blocking or pending):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
