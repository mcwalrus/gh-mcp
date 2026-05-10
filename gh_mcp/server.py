"""MCP server exposing GitHub Actions workflow tools via `gh` CLI."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from gh_mcp.gh import (
    run_cancel,
    run_list,
    run_rerun,
    run_view,
    run_watch,
    workflow_list,
    workflow_run,
)

mcp = FastMCP(
    "gh-mcp",
    instructions=(
        "GitHub Actions workflow MCP server. Use these tools to list, trigger, "
        "observe, cancel, and rerun workflow runs. All operations use the "
        "authenticated `gh` CLI session."
    ),
)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool
def list_workflows(
    repo: str | None = None,
    all_workflows: bool = False,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """List workflow files in the repository.

    Args:
        repo: Optional ``OWNER/REPO`` selector (uses default otherwise).
        all_workflows: Include disabled workflows.
        limit: Maximum number of workflows to return (default 50).
    """
    return workflow_list(repo=repo, all_workflows=all_workflows, limit=limit)


@mcp.tool
def trigger_workflow(
    workflow: str,
    ref: str | None = None,
    fields: dict[str, str] | None = None,
    repo: str | None = None,
) -> str:
    """Trigger a ``workflow_dispatch`` event for a given workflow.

    Returns the URL of the created run when available (gh ≥2.87).

    Args:
        workflow: Workflow ID or filename (e.g. ``deploy.yml``).
        ref: Branch or tag to run the workflow on.
        fields: Input parameters as key-value pairs (``-f key=value``).
        repo: Optional ``OWNER/REPO`` selector.
    """
    return workflow_run(workflow, ref=ref, fields=fields, repo=repo)


@mcp.tool
def list_runs(
    repo: str | None = None,
    workflow: str | None = None,
    branch: str | None = None,
    status: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """List recent workflow runs.

    Args:
        repo: Optional ``OWNER/REPO`` selector.
        workflow: Filter by workflow name or ID.
        branch: Filter by branch name.
        status: Filter by status (queued, completed, in_progress, failure, success, etc).
        limit: Maximum number of runs to return (default 20).
    """
    return run_list(repo=repo, workflow=workflow, branch=branch, status=status, limit=limit)


@mcp.tool
def view_run(
    run_id: int,
    repo: str | None = None,
) -> dict[str, Any]:
    """View details of a single workflow run including jobs and steps.

    Args:
        run_id: The database ID of the workflow run.
        repo: Optional ``OWNER/REPO`` selector.
    """
    return run_view(run_id, repo=repo, verbose=True)


@mcp.tool
def cancel_run(
    run_id: int,
    repo: str | None = None,
) -> str:
    """Cancel a workflow run.

    Args:
        run_id: The database ID of the workflow run to cancel.
        repo: Optional ``OWNER/REPO`` selector.
    """
    return run_cancel(run_id, repo=repo)


@mcp.tool
def rerun_run(
    run_id: int,
    failed_only: bool = False,
    debug: bool = False,
    repo: str | None = None,
) -> str:
    """Re-run a workflow, optionally only failed jobs or with debug logging.

    Args:
        run_id: The database ID of the workflow run to rerun.
        failed_only: Re-run only the failed jobs.
        debug: Re-run with debug logging enabled.
        repo: Optional ``OWNER/REPO`` selector.
    """
    return run_rerun(run_id, failed_only=failed_only, debug=debug, repo=repo)


@mcp.tool
def watch_run(
    run_id: int,
    repo: str | None = None,
) -> str:
    """Watch a workflow run until it completes and return the output.

    **Blocking**: This tool polls until the run finishes. For a non-blocking
    snapshot, use ``view_run`` instead.

    Args:
        run_id: The database ID of the workflow run to watch.
        repo: Optional ``OWNER/REPO`` selector.
    """
    return run_watch(run_id, repo=repo, compact=True)
