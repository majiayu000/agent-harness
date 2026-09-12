#!/usr/bin/env python3
"""Local unit checks for author-scoped workpad selection."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from workpad import MARKER, find_workpad  # noqa: E402


def comment(login: str, created_at: str, *, with_marker: bool = True, cid: int = 1) -> dict:
    body = f"{MARKER}\nstatus" if with_marker else "unrelated"
    return {
        "id": cid,
        "body": body,
        "created_at": created_at,
        "user": {"login": login},
    }


def main() -> int:
    foreign_only = [comment("attacker", "2026-09-13T10:00:00Z", cid=1)]
    assert find_workpad(foreign_only, author_login="operator") is None

    mixed = [
        comment("attacker", "2026-09-13T12:00:00Z", cid=2),
        comment("operator", "2026-09-13T11:00:00Z", cid=3),
    ]
    owned = find_workpad(mixed, author_login="operator")
    assert owned is not None and owned["id"] == 3

    owned_many = [
        comment("operator", "2026-09-13T09:00:00Z", cid=4),
        comment("operator", "2026-09-13T10:00:00Z", cid=5),
        comment("attacker", "2026-09-13T11:00:00Z", cid=6),
    ]
    newest = find_workpad(owned_many, author_login="Operator")
    assert newest is not None and newest["id"] == 5

    print("test_workpad_find: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
