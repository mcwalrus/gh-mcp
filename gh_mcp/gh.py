"""Thin subprocess wrapper around the `gh` CLI.

All MCP tools delegate to functions here so that subprocess invocation is
centralised and easy to mock in tests.
"""

from __future__ import annotations

import json
import subprocess
from typing import Any


class GhError(Exception):
    """Raised when a `gh` invocation exits non-zero."""

    def __init__(self, returncode: int, stderr: str) -> None:
        self.returncode = returncode
        self.stderr = stderr
        super().__init__(f"gh exited {returncode}: {stderr}")


def _run(*args: str, repo: str | None = None) -> str:
    """Invoke ``gh`` with *args*, returning stdout.

    Parameters
    ----------
    *args:
        Positional arguments forwarded to ``gh``.
    repo:
        Optional ``OWNER/REPO`` selector.  When set, ``-R <repo>`` is
        prepended to the argument list.
    """
    cmd: list[str] = ["gh"]
    if repo:
        cmd += ["-R", repo]
    cmd.extend(args)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise GhError(result.returncode, result.stderr.strip())
    return result.stdout


def _run_json(*args: str, repo: str | None = None) -> list[Any] | dict[str, Any]:
    """Invoke ``gh`` with ``--json`` and parse the result."""
    # We inject --json right after the subcommand so callers don't have to.
    # e.g. gh workflow list --json id,name,path,state
    #      gh run list --json ...
    # The caller supplies the remaining args after the subcommand.
    raw = _run(*args, repo=repo)
    raw = raw.strip()
    if not raw:
        return []
    return json.loads(raw)


# ---------------------------------------------------------------------------
# Workflow operations
# ---------------------------------------------------------------------------


def workflow_list(
    *, repo: str | None = None, all_workflows: bool = False, limit: int = 50
) -> list[dict[str, Any]]:
    """List workflow files.  Returns a list of dicts with id, name, path, state."""
    args = ["workflow", "list", "--json", "id,name,path,state", "--limit", str(limit)]
    if all_workflows:
        args.append("--all")
    result = _run_json(*args, repo=repo)
    assert isinstance(result, list)
    return result


def workflow_run(
    workflow: str,
    *,
    ref: str | None = None,
    fields: dict[str, str] | None = None,
    repo: str | None = None,
) -> str:
    """Trigger a workflow dispatch.  Returns the URL of the created run (gh ≥2.87)."""
    args = ["workflow", "run", workflow]
    if ref:
        args += ["--ref", ref]
    if fields:
        for key, value in fields.items():
            args += ["--field", f"{key}={value}"]
    return _run(*args, repo=repo).strip()


def run_list(
    *,
    repo: str | None = None,
    workflow: str | None = None,
    branch: str | None = None,
    status: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """List recent workflow runs."""
    json_fields = (
        "attempt,conclusion,createdAt,databaseId,displayTitle,event,"
        "headBranch,headSha,name,number,startedAt,status,updatedAt,url,"
        "workflowDatabaseId,workflowName"
    )
    args = ["run", "list", "--json", json_fields, "--limit", str(limit)]
    if workflow:
        args += ["--workflow", workflow]
    if branch:
        args += ["--branch", branch]
    if status:
        args += ["--status", status]
    result = _run_json(*args, repo=repo)
    assert isinstance(result, list)
    return result


def run_view(
    run_id: int,
    *,
    repo: str | None = None,
    verbose: bool = False,
) -> dict[str, Any]:
    """View details of a single workflow run."""
    json_fields = (
        "attempt,conclusion,createdAt,databaseId,displayTitle,event,"
        "headBranch,headSha,jobs,name,number,startedAt,status,updatedAt,url,"
        "workflowDatabaseId,workflowName"
    )
    args = ["run", "view", str(run_id), "--json", json_fields]
    if verbose:
        args.append("--verbose")
    result = _run_json(*args, repo=repo)
    assert isinstance(result, dict)
    return result


def run_cancel(run_id: int, *, repo: str | None = None) -> str:
    """Cancel a workflow run."""
    return _run("run", "cancel", str(run_id), repo=repo).strip()


def run_rerun(
    run_id: int,
    *,
    failed_only: bool = False,
    debug: bool = False,
    repo: str | None = None,
) -> str:
    """Re-run a workflow (optionally only failed jobs, or with debug logging)."""
    args = ["run", "rerun", str(run_id)]
    if failed_only:
        args.append("--failed")
    if debug:
        args.append("--debug")
    return _run(*args, repo=repo).strip()


def run_watch(
    run_id: int,
    *,
    repo: str | None = None,
    exit_status: bool = False,
    compact: bool = False,
) -> str:
    """Block until a run completes, returning the final output.

    **Note**: This is a long-polling operation that blocks for the duration
    of the workflow run.  Prefer ``run_view`` for a non-blocking snapshot.
    """
    args = ["run", "watch", str(run_id)]
    if exit_status:
        args.append("--exit-status")
    if compact:
        args.append("--compact")
    return _run(*args, repo=repo).strip()
