---
name: linkedin-drafter
description: >-
  Write a personalized LinkedIn outreach message in the user's own voice, then
  clean it of AI-slop with Cadence. Use when the user wants to draft a LinkedIn
  connection request, cold outreach, or DM. Draft-only — never scrapes LinkedIn
  or sends anything; the user reviews and sends themselves. No API key needed —
  you (the assistant) do the writing.
---

# LinkedIn Drafter

Draft LinkedIn outreach that sounds like the user, not like AI. You write it with
your own model — no API key, no paid service. Runs in any assistant: Claude Code,
Claude Desktop, Codex, Cursor, ChatGPT.

Follow three steps: **learn → draft → deslop.**

## 1. Learn the user's voice

If the user points you at samples of their past writing (a file or folder of old
LinkedIn messages, emails, posts — often via a `VOICE_SAMPLE` path), read them and
study the voice: sentence rhythm, word choice, how warm or blunt, how they open and
close. You will imitate *that*, not a generic "professional" tone. If no samples
exist, ask for one or two, or proceed in a plain, warm, human voice.

## 2. Draft

You need a **name**, the **context** (the specific thing they noticed — a post,
talk, or project), and the **goal** (what they want). Optional: company, role,
relationship. Then write the message:

- Greet by first name. Reference the **specific** context, never a generic opener.
- State the goal plainly, then a low-pressure ask ("no worries if the timing
  isn't right"). Sign off with `Best,`.
- 3–5 sentences. For a connection request, one or two sentences under **300
  characters**.
- No emoji, no hashtags. Match the voice from step 1.

## 3. Deslop

Clean the draft of AI tells with Cadence's deterministic detector.

- **If you can run a terminal** (Claude Code, Codex, Cursor): pipe the draft
  through it and apply what it flags —

  ```bash
  printf '%s' "<your draft>" | npx cadence-deslop --fix
  ```

  It prints the mechanically-cleaned text and reports on stderr how many tells
  still need a manual rewrite. Rewrite those remaining tells yourself, in the
  user's voice (vary rhythm, cut hollow-confidence words and clichéd openers).

- **If you can't run a terminal** (Claude Desktop, ChatGPT app): call the
  `deslop` tool from the `linkedin-message-drafter` MCP server if it's connected —
  it returns the cleaned text plus a `remaining` list of tells for you to rewrite.
  If neither is available, self-edit: no "In today's fast-paced world" openers, no
  "truly excited to connect," and vary your sentence lengths.

Show the user the final cleaned draft. Let them review, edit, and send it.

## Boundaries

Never scrape LinkedIn, look the person up, or send the message. Produce the draft
and hand it back.
