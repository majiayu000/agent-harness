#!/usr/bin/env python3
"""Exercise PR check lookup failures and gate exit codes with a fake gh."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SWEEP = Path(__file__).with_name("pr_feedback_sweep.py")

FAKE_GH = """
import json
import os
import sys

if sys.argv[1:3] == ["pr", "view"]:
    print(json.dumps({
        "number": 8,
        "state": "OPEN",
        "isDraft": False,
        "mergeable": "MERGEABLE",
        "reviewDecision": "APPROVED",
        "comments": [],
        "reviews": [],
        "statusCheckRollup": [],
    }))
elif sys.argv[1] == "api":
    print("[]")
elif sys.argv[1:3] == ["pr", "checks"]:
    sys.stdout.write(os.environ["GH_CHECKS_PAYLOAD"])
    sys.stderr.write(os.environ.get("GH_CHECKS_ERROR", ""))
    sys.exit(int(os.environ["GH_CHECKS_EXIT"]))
else:
    sys.exit("unexpected gh command")
"""


class CheckLookupTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        fake_gh = Path(self.temp.name) / "gh"
        fake_gh.write_text(f"#!{sys.executable}\n{FAKE_GH}")
        fake_gh.chmod(0o755)
        self.env = os.environ.copy()
        self.env["PATH"] = f"{self.temp.name}{os.pathsep}{self.env.get('PATH', '')}"

    def sweep(
        self, payload: str, exit_code: int = 0, *flags: str, error: str = ""
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SWEEP), "8", "--repo", "owner/repo", "--format", "json", *flags],
            env={
                **self.env,
                "GH_CHECKS_PAYLOAD": payload,
                "GH_CHECKS_EXIT": str(exit_code),
                "GH_CHECKS_ERROR": error,
            },
            capture_output=True,
            text=True,
        )

    def test_lookup_failure_never_succeeds(self) -> None:
        for error in ["network down", "no checks reported on the 'topic' branch"]:
            for flags in [(), ("--fail-on-blocking",), ("--fail-on-pending",)]:
                with self.subTest(error=error, flags=flags):
                    result = self.sweep("", 1, *flags, error=error)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(error, result.stderr)
                    self.assertEqual(result.stdout, "")

    def test_missing_or_invalid_check_array_never_succeeds(self) -> None:
        for payload in ["", "null", "{}", '"unavailable"', "not json"]:
            for exit_code in [0, 1, 8]:
                with self.subTest(payload=payload, exit_code=exit_code):
                    result = self.sweep(payload, exit_code, "--fail-on-pending")
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("check status unavailable", result.stderr)
                    self.assertEqual(result.stdout, "")

    def test_command_errors_preserve_stderr(self) -> None:
        result = self.sweep("[]", 2, "--fail-on-blocking", error="authentication failed")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("authentication failed", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_valid_check_arrays_keep_gate_behavior(self) -> None:
        for exit_code in [0, 1, 8]:
            for bucket, flag, expected in [
                ("pass", "--fail-on-pending", 0),
                ("skipping", "--fail-on-pending", 0),
                ("fail", "--fail-on-blocking", 2),
                ("cancel", "--fail-on-blocking", 2),
                ("pending", "--fail-on-pending", 2),
                ("pending", "--fail-on-blocking", 0),
            ]:
                with self.subTest(exit_code=exit_code, bucket=bucket, flag=flag):
                    checks = [{"name": "validate", "bucket": bucket}]
                    result = self.sweep(json.dumps(checks), exit_code, flag)
                    self.assertEqual(result.returncode, expected, result.stderr)
                    self.assertEqual(json.loads(result.stdout)["checks"], checks)

    def test_successful_empty_array_is_valid(self) -> None:
        result = self.sweep("[]", 0, "--fail-on-blocking", "--fail-on-pending")
        self.assertEqual(result.returncode, 0, result.stderr)
        summary = json.loads(result.stdout)
        self.assertEqual(summary["checks"], [])
        self.assertEqual(summary["classification"]["blocking"], [])
        self.assertEqual(summary["classification"]["pending"], [])


if __name__ == "__main__":
    unittest.main()
