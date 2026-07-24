# LinkedIn Message Drafter

[![CI](https://github.com/wuisabel-gif/linkedin-message-drafter/actions/workflows/ci.yml/badge.svg)](https://github.com/wuisabel-gif/linkedin-message-drafter/actions/workflows/ci.yml)

A lightweight CLI companion to [Cadence](https://github.com/wuisabel-gif/Cadence) for LinkedIn outreach. Feed it a name and a bit of context; it hands back a concise, human-sounding draft you review and send yourself.

It handles the outreach-specific plumbing — batch/CSV input, the deterministic ≤300-character connection-note limit, offline templates. For the smart part (voice-matching and AI-slop cleanup), it defers to **Cadence**. If you just want great outreach, `/cadence write` plus a voice covers most of it; this repo is the scriptable/offline CLI around that.

**Draft-first and safe by design.** It does **not** scrape LinkedIn, automate browser actions, or send anything on its own. You stay in control of every message — review, copy, send. Ready to automate? Wire in an approved LinkedIn integration through the adapter below.

**No API key needed.** The best way to use it is inside an AI assistant you already
pay for — Claude Code, Claude Desktop, Codex, Cursor, or ChatGPT — which does the
writing on your existing subscription. See [Use it in your AI assistant](#use-it-in-your-ai-assistant--no-api-key-recommended). The standalone CLI works too: free offline via a
built-in template, or with your own Anthropic API key for richer copy.

## Install

```bash
pipx install linkedin-message-drafter          # or: pip install linkedin-message-drafter
# for the Claude draft path: pipx install "linkedin-message-drafter[ai]"
```

[![PyPI](https://img.shields.io/pypi/v/linkedin-message-drafter)](https://pypi.org/project/linkedin-message-drafter/)

## Quick start

```bash
linkedin-draft prospect.json      # prints a draft and saves it to drafts/
```

### From source (development)

```bash
git clone https://github.com/wuisabel-gif/linkedin-message-drafter.git
cd linkedin-message-drafter
python3 -m venv .venv && source .venv/bin/activate
pip install -e .                  # add [ai] for the Claude draft path: pip install -e ".[ai]"
linkedin-draft src/linkedin_message_drafter/examples/prospect.json
```

## Web UI

Prefer a form to the CLI? A zero-dependency local UI ships with it:

```bash
linkedin-draft-web            # then open http://127.0.0.1:8000
```

Binds to localhost only, uses the same drafting engine (voice matching, slop check, short mode), and still just drafts — nothing is sent.

## Input

See `src/linkedin_message_drafter/examples/prospect.json`. Required fields are `name`, `context`, and `goal`; `company`, `role`, and `relationship` are optional. CSV input uses the same column names, one prospect per row.

## Options

```bash
# Batch — pass multiple files, a CSV, or a whole folder
linkedin-draft ./prospects/
linkedin-draft prospects.csv

# Connection-request note, guaranteed under LinkedIn's 300-char limit
linkedin-draft --short my-prospect.json

# Write in a Cadence voice preset (AI path; needs CADENCE_VOICES)
export CADENCE_VOICES=/path/to/Cadence/voices
linkedin-draft --style punchy my-prospect.json
```

`--short` works with both the template and AI paths; `--style` applies to AI drafts only. Available presets are the `.md` files in Cadence's `voices/` (`punchy`, `column`, `plain`, `dispatch`, …).

## AI drafting via the API (advanced / power users)

Prefer the assistant path above — it needs no key. But if you want the *standalone
CLI* to generate AI copy (for scripting or batch runs), set `ANTHROPIC_API_KEY` to
draft with Claude. This uses the pay-as-you-go Anthropic API (a subscription does
**not** cover it). With no key set, the CLI uses the dependency-free template and works fully offline.

```bash
export ANTHROPIC_API_KEY=sk-ant-...
linkedin-draft my-prospect.json
```

### Sounds like you ([Cadence](https://github.com/wuisabel-gif/Cadence))

Point `VOICE_SAMPLE` at your own past writing and the AI draft mimics the way you speak — tone, rhythm, and word choice. It takes a single file **or a directory**: drop in a folder of all your previous posts and messages and [Cadence](https://github.com/wuisabel-gif/Cadence) learns from the whole corpus.

```bash
export VOICE_SAMPLE=~/my-writing-sample.txt   # one sample
export VOICE_SAMPLE=~/my-linkedin-posts/       # or a folder of everything you've written
```

**AI-slop cleanup is Cadence's job.** This tool writes the outreach; to strip AI
tells, run the draft through [Cadence](https://github.com/wuisabel-gif/Cadence) —
its deterministic `cadence-deslop` detector. The drafter doesn't bundle its own
copy; it composes with Cadence so there's one source of truth for voice + slop.

## Use it in your AI assistant — no API key (recommended)

Your own assistant does the writing, powered by the Claude / Codex / ChatGPT
subscription you already pay for — no API key, no hosting, no per-message cost.

Drop [`skills/linkedin-drafter/SKILL.md`](skills/linkedin-drafter/SKILL.md) into
your assistant's skills directory (Claude Code, Codex, Cursor, …). Then just ask
it to draft a LinkedIn message. The skill owns the **outreach craft** — the
specific-context opener, the low-pressure ask, the 300-char note limit — and
**hands off voice-matching and deslop to [Cadence](https://github.com/wuisabel-gif/Cadence)** if you have it installed (with a self-edit fallback if you don't).

Install Cadence too for the real deterministic voice + deslop. Everything stays
draft-only — nothing is scraped or sent.

## Adding an approved API integration

`src/linkedin_message_drafter/linkedin.py` contains a deliberately unimplemented `LinkedInClient`. Implement only the endpoints and scopes that LinkedIn has approved for your application. Keep the default workflow draft-only and require a user confirmation before any send operation. Do not add scraping, credential collection, or bulk/unattended sending.

Read `TUTORIAL.md` before configuring credentials or requesting permissions.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Publishing

Releases publish to PyPI automatically via [Trusted Publishing](https://docs.pypi.org/trusted-publishers/) — no API token is stored anywhere. One-time setup:

1. On [pypi.org](https://pypi.org/manage/account/publishing/), add a *pending publisher*: project `linkedin-message-drafter`, owner `wuisabel-gif`, repo `linkedin-message-drafter`, workflow `publish.yml`, environment `pypi`.
2. Cut a release: bump `version` in `pyproject.toml`, then

   ```bash
   git tag v0.1.0 && git push origin v0.1.0
   gh release create v0.1.0 --generate-notes
   ```

The `Publish to PyPI` workflow builds the sdist + wheel and uploads them. Local dry run:

```bash
python -m build && twine check dist/*
```
