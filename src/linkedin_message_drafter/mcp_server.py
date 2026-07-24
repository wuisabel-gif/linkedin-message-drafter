"""MCP server exposing the drafter as tools for Claude, ChatGPT, and other hosts.

Run:  linkedin-draft-mcp        (stdio transport; configure it in your MCP client)
Requires the [mcp] extra:  pip install "linkedin-message-drafter[mcp]"

Tools:
  draft_message — build a personalized draft (+ its Cadence slop score)
  score_text    — score any text 0-100 with the cadence-deslop detector
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .ai import build_draft_ai
from .cadence import deslop
from .drafts import Prospect

mcp = FastMCP("linkedin-message-drafter")


@mcp.tool()
def draft_message(name: str, context: str, goal: str, company: str = "",
                  role: str = "", relationship: str = "", short: bool = False) -> dict:
    """Draft a personalized LinkedIn outreach message. Never scrapes or sends.

    Args:
        name: The prospect's name (greeting uses the first name).
        context: The specific thing you noticed (a post, talk, project).
        goal: What you want, in one line.
        company: The prospect's company (optional).
        role: The prospect's role/title (optional).
        relationship: How you know them, if at all (optional).
        short: If true, a connection-request note under 300 characters.
    """
    prospect = Prospect.from_dict({
        "name": name, "context": context, "goal": goal,
        "company": company, "role": role, "relationship": relationship,
    })
    draft = build_draft_ai(prospect, short=short)
    report = deslop(draft)
    return {
        "draft": draft,
        "chars": len(draft),
        "cadence_score": report["score"] if report else None,
        "cadence_grade": report["grade"] if report else None,
    }


@mcp.tool()
def score_text(text: str) -> dict:
    """Score text 0-100 for AI-slop tells with the cadence-deslop detector.

    Returns null fields when the detector isn't installed.
    """
    report = deslop(text)
    if not report:
        return {"score": None, "grade": None, "findings": []}
    return {"score": report["score"], "grade": report["grade"],
            "findings": [f["rule"] for f in report.get("findings", [])]}


def main() -> int:
    mcp.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
