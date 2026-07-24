---
name: linkedin-drafter
description: >-
  Draft a personalized LinkedIn outreach message from a name and some context.
  Use when the user wants to write a LinkedIn connection request, cold outreach,
  or DM to a specific person. Draft-only — it never scrapes LinkedIn or sends
  anything; the user reviews and sends themselves.
---

# LinkedIn Drafter

Turn a prospect's details into a concise, warm LinkedIn outreach draft.

## When to use

The user wants to reach out to a specific person on LinkedIn and gives you (or
you can ask for) at least a **name**, **context** (the specific thing they
noticed — a post, talk, or project), and a **goal** (what they want). Optional:
company, role, relationship.

## How to draft

Prefer the installed CLI if available:

```bash
echo '{"name":"...","context":"...","goal":"...","company":"","role":""}' > /tmp/prospect.json
linkedin-draft /tmp/prospect.json          # add --short for a <300-char connection note
```

Or, if the MCP server is connected, call the `draft_message` tool with the same
fields. Either path returns the draft plus a Cadence AI-slop score.

If neither is available, write the draft yourself following these rules:

- Greet by first name. Reference the **specific** context, not a generic opener.
- State the goal plainly, then a low-pressure ask ("no worries if the timing
  isn't right"). Sign off with `Best,`.
- Keep it 3–5 sentences. For a connection request, one or two sentences under
  **300 characters**.
- No emoji, no hashtags, no "In today's fast-paced world" openers, no hollow
  confidence ("truly excited to connect"). Vary sentence rhythm.

## Boundaries

Never scrape LinkedIn, look up the person, or send the message. Produce the
draft and let the user review, edit, and send it.
