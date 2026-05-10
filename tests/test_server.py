"""Tests for gh_mcp.server — the MCP tool layer.

These verify that each tool delegates to the correct gh wrapper function
with the right arguments.
"""

from __future__ import annotations

from unittest.mock import patch

from gh_mcp.server import (
    cancel_run,
    list_runs,
    list_workflows,
    rerun_run,
    trigger_workflow,
    view_run,
    watch_run,
)


def test_list_workflows_tool() -> None:
    with patch("gh_mcp.server.workflow_list", return_value=[{"id": 1}]) as mock:
        result = list_workflows(repo="owner/repo", all_workflows=True, limit=10)

    assert result == [{"id": 1}]
    mock.assert_called_once_with(repo="owner/repo", all_workflows=True, limit=10)


def test_trigger_workflow_tool() -> None:
    with patch("gh_mcp.server.workflow_run", return_value="https://example.com/runs/99") as mock:
        result = trigger_workflow(workflow="deploy.yml", ref="main", fields={"env": "prod"})

    assert result == "https://example.com/runs/99"
    mock.assert_called_once_with("deploy.yml", ref="main", fields={"env": "prod"}, repo=None)


def test_list_runs_tool() -> None:
    with patch("gh_mcp.server.run_list", return_value=[]) as mock:
        result = list_runs(workflow="CI", status="in_progress")

    assert result == []
    mock.assert_called_once_with(
        repo=None, workflow="CI", branch=None, status="in_progress", limit=20
    )


def test_view_run_tool() -> None:
    run_data = {"databaseId": 9001, "status": "completed"}
    with patch("gh_mcp.server.run_view", return_value=run_data) as mock:
        result = view_run(run_id=9001, repo="owner/repo")

    assert result == run_data
    mock.assert_called_once_with(9001, repo="owner/repo", verbose=True)


def test_cancel_run_tool() -> None:
    with patch("gh_mcp.server.run_cancel", return_value="cancelled") as mock:
        result = cancel_run(run_id=9001)

    assert result == "cancelled"
    mock.assert_called_once_with(9001, repo=None)


def test_rerun_run_tool() -> None:
    with patch("gh_mcp.server.run_rerun", return_value="rerun initiated") as mock:
        result = rerun_run(run_id=9001, failed_only=True, debug=True)

    assert result == "rerun initiated"
    mock.assert_called_once_with(9001, failed_only=True, debug=True, repo=None)


def test_watch_run_tool() -> None:
    with patch("gh_mcp.server.run_watch", return_value="✓ done") as mock:
        result = watch_run(run_id=9001)

    assert result == "✓ done"
    mock.assert_called_once_with(9001, repo=None, compact=True)
