"""MCP server exposing Cadence's deslop cleaner as a tool for AI assistants.

The assistant (Claude Desktop/Code, ChatGPT, Cursor, ...) writes the draft in
your voice using its own subscription — no API key needed. This server gives it
one deterministic thing it can't do on its own: clean the AI-slop out of the
draft with cadence-deslop.

Run:  linkedin-draft-mcp        (stdio transport; register in your MCP client)
Requires:  pip install "linkedin-message-drafter[mcp]"  and Node + cadence-deslop.
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .cadence import deslop_fix

mcp = FastMCP("linkedin-message-drafter")


@mcp.tool()
def deslop(text: str) -> dict:
    """Clean AI-slop from a draft with Cadence's deterministic detector.

    Returns the mechanically-cleaned text plus the tells that still need a manual
    rewrite in the user's voice (e.g. uniform rhythm, hollow confidence). After
    calling this, rewrite the `remaining` tells yourself in the user's voice.

    Args:
        text: The draft to clean.
    """
    result = deslop_fix(text)
    if result is None:
        return {"cleaned": text, "remaining": [],
                "note": "cadence-deslop not installed; text returned unchanged"}
    return result


def main() -> int:
    mcp.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
