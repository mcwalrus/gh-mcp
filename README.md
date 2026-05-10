# gh-mcp

Minimal MCP server exposing GitHub Actions workflow tools via the `gh` CLI.

Provides 7 tools for listing, triggering, observing, cancelling, and rerunning
workflow runs — everything an agent needs for the feedback loop described in
[github_actions_remote_feedback_mechanism.md](github_actions_remote_feedback_mechanism.md).

## Tools

| Tool | Description |
|---|---|
| `list_workflows` | List workflow files in a repository |
| `trigger_workflow` | Trigger a `workflow_dispatch` event (returns run URL) |
| `list_runs` | List recent workflow runs (filter by workflow, branch, status) |
| `view_run` | View details of a single run including jobs and steps |
| `cancel_run` | Cancel a running workflow |
| `rerun_run` | Re-run a workflow (optionally only failed jobs or with debug) |
| `watch_run` | Block until a run completes and return output |

## Quick Start

```bash
just bootstrap    # install deps + pre-commit hooks
just check        # run all CI gates
```

## Running the Server

### Development (MCP inspector)

```bash
fastmcp dev main.py
```

### Production (stdio transport)

```bash
fastmcp run main.py
```

### Claude Code integration

Add to your Claude Code MCP config:

```json
{
  "mcpServers": {
    "gh-mcp": {
      "command": "fastmcp",
      "args": ["run", "main.py"]
    }
  }
}
```

Or via the CLI:

```bash
claude mcp add gh-mcp -- fastmcp run main.py
```

## Task Runner Commands

| Command            | What it does                                       |
|-------------------|-----------------------------------------------------|
| `just check`      | All gates (format, lint, typecheck, test)           |
| `just format`     | Auto-format and lint-fix all Python files           |
| `just lint`       | Run ruff lint (no auto-fix)                         |
| `just typecheck`  | Run pyright type checker                            |
| `just test`       | Run pytest                                          |
| `just sync`       | Sync dependencies from uv.lock                      |
| `just bootstrap`  | Install deps and pre-commit hooks (run once)        |

## Key Constraints

- `uv` is the package manager. Do not use `pip install` directly.
- All code must pass `pyright` in strict mode.
- Ruff replaces flake8, black, isort, and pyupgrade.
- Tests must pass. Do not commit with failing tests.
- All deps must be in `pyproject.toml`. Do not hand-edit `uv.lock`.