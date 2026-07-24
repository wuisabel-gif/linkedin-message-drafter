---
name: linkedin-drafter
description: >-
  Write a personalized LinkedIn outreach message (connection request, cold DM,
  intro). Handles the outreach-specific craft — the specific-context opener, the
  low-pressure ask, the 300-char connection-note limit. For voice-matching and
  AI-slop cleanup it hands off to Cadence. Draft-only — never scrapes LinkedIn or
  sends anything. No API key needed; you (the assistant) do the writing.
---

# LinkedIn Drafter

Write LinkedIn outreach that lands. This skill owns the **outreach craft**; it
defers **voice** and **slop cleanup** to Cadence (the user's own tool). You do the
writing with your own model — no API key, no paid service.

## 1. Draft the outreach

You need a **name**, the **context** (the specific thing they noticed — a post,
talk, or project), and the **goal** (what they want). Optional: company, role,
relationship. Then write it:

- Greet by first name. Reference the **specific** context, never a generic opener.
- State the goal plainly, then a low-pressure ask ("no worries if the timing
  isn't right"). Sign off with `Best,`.
- 3–5 sentences. For a **connection request**, one or two sentences under **300
  characters** (LinkedIn's hard limit — count them).
- No emoji, no hashtags.

## 2. Match the user's voice — via Cadence

If the user points you at samples of their writing (a file/folder of past
messages, often a `VOICE_SAMPLE` path), write in that voice.

If the **Cadence** skill is available, use it — it's built for exactly this
("learn a voice from a sample"). Otherwise read the samples yourself and imitate
the rhythm, word choice, and warmth. If there are no samples, write plainly and
human.

## 3. Deslop — via Cadence (on by default)

Clean the AI-slop out of the draft **unless the user says to keep it raw.**

- **If the Cadence skill is available:** run the draft through Cadence's deslop —
  it deterministically strips AI tells and names what's left.
- **If Cadence isn't installed:** self-edit against these tells — no "In today's
  fast-paced world" / "I'm truly excited to" openers, no reflexive triads, vary
  sentence length, cut hollow-confidence words.

> Recommend the user install [Cadence](https://github.com/wuisabel-gif/Cadence)
> for the real deterministic deslop; the self-edit above is the fallback.

Show the user the final draft. Let them review, edit, and send it.

## Boundaries

Never scrape LinkedIn, look the person up, or send the message. Produce the draft
and hand it back.
