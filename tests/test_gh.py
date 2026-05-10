"""Tests for gh_mcp.gh — subprocess wrapper around the `gh` CLI.

All subprocess calls are mocked so the tests run without `gh` installed.
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import patch

import pytest

from gh_mcp.gh import (
    GhError,
    run_cancel,
    run_list,
    run_rerun,
    run_view,
    run_watch,
    workflow_list,
    workflow_run,
)

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------


def _subprocess_result(stdout: str = "", returncode: int = 0, stderr: str = "") -> Any:
    """Build a mock subprocess.CompletedProcess."""
    return subprocess.CompletedProcess(  # type: ignore[attr-defined]
        args=["gh"],
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


import subprocess  # noqa: E402 — needed for _subprocess_result

# ---------------------------------------------------------------------------
# workflow_list
# ---------------------------------------------------------------------------


def test_workflow_list_basic() -> None:
    payload = json.dumps(
        [
            {"id": 111, "name": "CI", "path": ".github/workflows/ci.yml", "state": "active"},
            {
                "id": 222,
                "name": "Deploy",
                "path": ".github/workflows/deploy.yml",
                "state": "active",
            },
        ]
    )
    with patch("gh_mcp.gh.subprocess.run", return_value=_subprocess_result(payload)):
        result = workflow_list()

    assert len(result) == 2
    assert result[0]["name"] == "CI"
    assert result[1]["id"] == 222


def test_workflow_list_with_repo_and_all() -> None:
    payload = "[]"
    with patch("gh_mcp.gh.subprocess.run", return_value=_subprocess_result(payload)) as mock:
        workflow_list(repo="owner/repo", all_workflows=True, limit=10)

    cmd = mock.call_args[0][0]
    assert "-R" in cmd
    assert "owner/repo" in cmd
    assert "--all" in cmd
    assert "--limit" in cmd
    assert "10" in cmd


# ---------------------------------------------------------------------------
# workflow_run (trigger)
# ---------------------------------------------------------------------------


def test_workflow_run_returns_url() -> None:
    url = "https://github.com/owner/repo/actions/runs/12345"
    with patch("gh_mcp.gh.subprocess.run", return_value=_subprocess_result(url + "\n")):
        result = workflow_run("deploy.yml")

    assert result == url


def test_workflow_run_with_ref_and_fields() -> None:
    with patch("gh_mcp.gh.subprocess.run", return_value=_subprocess_result("ok\n")) as mock:
        workflow_run("deploy.yml", ref="main", fields={"env": "prod"})

    cmd = mock.call_args[0][0]
    assert "--ref" in cmd
    assert "main" in cmd
    assert "--field" in cmd
    assert "env=prod" in cmd


def test_workflow_run_error() -> None:
    with (
        patch(
            "gh_mcp.gh.subprocess.run",
            return_value=_subprocess_result(returncode=1, stderr="refused"),
        ),
        pytest.raises(GhError, match="refused"),
    ):
        workflow_run("missing.yml")


# ---------------------------------------------------------------------------
# run_list
# ---------------------------------------------------------------------------


def test_run_list_returns_runs() -> None:
    payload = json.dumps(
        [
            {"databaseId": 9001, "name": "CI", "status": "completed", "conclusion": "success"},
            {"databaseId": 9002, "name": "CI", "status": "in_progress", "conclusion": None},
        ]
    )
    with patch("gh_mcp.gh.subprocess.run", return_value=_subprocess_result(payload)):
        result = run_list(workflow="CI", branch="main", status="in_progress")

    assert len(result) == 2
    assert result[1]["status"] == "in_progress"


def test_run_list_empty() -> None:
    with patch("gh_mcp.gh.subprocess.run", return_value=_subprocess_result("")):
        result = run_list()
    assert result == []


# ---------------------------------------------------------------------------
# run_view
# ---------------------------------------------------------------------------


def test_run_view_returns_details() -> None:
    payload = json.dumps(
        {
            "databaseId": 9001,
            "name": "CI",
            "status": "completed",
            "conclusion": "success",
            "jobs": [],
        }
    )
    with patch("gh_mcp.gh.subprocess.run", return_value=_subprocess_result(payload)):
        result = run_view(9001)

    assert result["databaseId"] == 9001
    assert result["status"] == "completed"


# ---------------------------------------------------------------------------
# run_cancel
# ---------------------------------------------------------------------------


def test_run_cancel() -> None:
    with patch(
        "gh_mcp.gh.subprocess.run", return_value=_subprocess_result("Run was cancelled\n")
    ) as mock:
        result = run_cancel(9001)

    assert "cancelled" in result.lower()
    cmd = mock.call_args[0][0]
    assert "cancel" in cmd
    assert "9001" in cmd


# ---------------------------------------------------------------------------
# run_rerun
# ---------------------------------------------------------------------------


def test_run_rerun_defaults() -> None:
    with patch(
        "gh_mcp.gh.subprocess.run", return_value=_subprocess_result("Rerun initiated\n")
    ) as mock:
        result = run_rerun(9001)

    assert "Rerun" in result
    cmd = mock.call_args[0][0]
    assert "--failed" not in cmd
    assert "--debug" not in cmd


def test_run_rerun_failed_only_with_debug() -> None:
    with patch("gh_mcp.gh.subprocess.run", return_value=_subprocess_result("ok\n")) as mock:
        run_rerun(9001, failed_only=True, debug=True)

    cmd = mock.call_args[0][0]
    assert "--failed" in cmd
    assert "--debug" in cmd


# ---------------------------------------------------------------------------
# run_watch
# ---------------------------------------------------------------------------


def test_run_watch() -> None:
    with patch(
        "gh_mcp.gh.subprocess.run", return_value=_subprocess_result("✓ Run completed\n")
    ) as mock:
        result = run_watch(9001, compact=True)

    assert "completed" in result.lower()
    cmd = mock.call_args[0][0]
    assert "watch" in cmd
    assert "--compact" in cmd
