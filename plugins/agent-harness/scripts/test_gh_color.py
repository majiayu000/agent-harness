#!/usr/bin/env python3
"""Fake-gh checks for CLICOLOR_FORCE isolation and the doctor JSON fallback."""

from __future__ import annotations

import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parents[3]
DOCTOR = SCRIPTS / "doctor.sh"

sys.path.insert(0, str(SCRIPTS))

import pr_feedback_sweep  # noqa: E402
import workpad  # noqa: E402

CONDITIONAL_GH = r"""#!/bin/sh
printf '%s\n' "${CLICOLOR_FORCE-unset}" >> "$GH_COLOR_LOG"
if [ "${CLICOLOR_FORCE:-}" = "0" ]; then
  printf '%s\n' '{"nameWithOwner":"majiayu000/agent-harness","url":"https://github.com/majiayu000/agent-harness","defaultBranchRef":{"name":"main"},"viewerPermission":"ADMIN","hasIssuesEnabled":true,"visibility":"PUBLIC","number":7,"title":"color"}'
  exit 0
fi
printf '\033[1;38m{\033[m\n'
exit 0
"""

ALWAYS_ANSI_GH = r"""#!/bin/sh
printf '\033[1;38m{\033[m\n'
exit 0
"""


def install_gh(directory: Path, script: str) -> None:
    path = directory / "gh"
    path.write_text(script)
    path.chmod(path.stat().st_mode | stat.S_IEXEC)


def doctor_env(bin_dir: Path, log_path: Path | None = None) -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"
    env["CLICOLOR_FORCE"] = "1"
    env["NO_COLOR"] = "1"
    env["AGENT_HARNESS_ENFORCE"] = "0"
    env["AGENT_HARNESS_REPO_ROOT"] = str(REPO)
    if log_path is not None:
        env["GH_COLOR_LOG"] = str(log_path)
    return env


def run_doctor(env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(DOCTOR)],
        cwd=REPO,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_python_helpers_force_plain_color() -> None:
    saved = {
        "CLICOLOR_FORCE": os.environ.get("CLICOLOR_FORCE"),
        "PATH": os.environ.get("PATH"),
        "GH_COLOR_LOG": os.environ.get("GH_COLOR_LOG"),
    }
    os.environ["CLICOLOR_FORCE"] = "1"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp)
            log_path = bin_dir / "gh.log"
            install_gh(bin_dir, CONDITIONAL_GH)
            os.environ["PATH"] = f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"
            os.environ["GH_COLOR_LOG"] = str(log_path)
            sweep = pr_feedback_sweep.gh_json(["repo", "view", "--json", "nameWithOwner"])
            pad = workpad.gh_json(["issue", "view", "7", "--json", "number,title"])
            assert sweep["nameWithOwner"] == "majiayu000/agent-harness"
            assert pad["number"] == 7
            lines = log_path.read_text().splitlines()
            assert lines and all(line == "0" for line in lines), lines
            assert os.environ["CLICOLOR_FORCE"] == "1"
    finally:
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def test_doctor_parses_when_child_color_disabled() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        bin_dir = Path(tmp)
        log_path = bin_dir / "gh.log"
        install_gh(bin_dir, CONDITIONAL_GH)
        result = run_doctor(doctor_env(bin_dir, log_path))
        assert result.returncode == 0, result.stderr
        assert f"- root: {REPO}" in result.stdout
        assert "- repo: majiayu000/agent-harness" in result.stdout
        assert "## Result" in result.stdout
        assert "- repo: unavailable" not in result.stdout
        assert "JSONDecodeError" not in result.stderr
        lines = log_path.read_text().splitlines()
        assert len(lines) >= 2, lines
        assert all(line == "0" for line in lines), lines


def test_doctor_fallback_when_json_stays_colored() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        bin_dir = Path(tmp)
        install_gh(bin_dir, ALWAYS_ANSI_GH)
        result = run_doctor(doctor_env(bin_dir))
        assert result.returncode == 0, result.stderr
        assert f"- root: {REPO}" in result.stdout
        assert "- repo: unavailable" in result.stdout
        assert "## Result" in result.stdout
        assert result.stdout.strip().splitlines()[-1] == "Needs setup"
        assert "JSONDecodeError" not in result.stderr


def main() -> int:
    test_python_helpers_force_plain_color()
    test_doctor_parses_when_child_color_disabled()
    test_doctor_fallback_when_json_stays_colored()
    print("test_gh_color: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

