"""Entry point for the gh-mcp server.

Run with::

    fastmcp dev main.py        # dev mode (MCP inspector)
    fastmcp run main.py        # production stdio transport
"""

from gh_mcp.server import mcp


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
