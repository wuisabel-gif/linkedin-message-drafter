# LinkedIn Message Drafter

[![CI](https://github.com/wuisabel-gif/linkedin-message-drafter/actions/workflows/ci.yml/badge.svg)](https://github.com/wuisabel-gif/linkedin-message-drafter/actions/workflows/ci.yml)

Write LinkedIn outreach that actually gets replies — personalized, warm, and ready in seconds. Feed it a name and a bit of context; it hands back a concise, human-sounding draft you can send as-is or tweak.

**Draft-first and safe by design.** It does **not** scrape LinkedIn, automate browser actions, or send anything on its own. You stay in control of every message — review, copy, send. Ready to automate? Wire in an approved LinkedIn integration through the adapter below.

**No API key needed.** The best way to use it is inside an AI assistant you already
pay for — Claude Code, Claude Desktop, Codex, Cursor, or ChatGPT — which does the
writing on your existing subscription. See [Use it in your AI assistant](#use-it-in-your-ai-assistant--no-api-key). The standalone CLI works too: free offline via a
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

# Best-of-N — generate 3 AI drafts, keep the one cadence-deslop scores cleanest
linkedin-draft --best-of 3 my-prospect.json

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

**Automatic slop check.** If the [`cadence-deslop`](https://github.com/wuisabel-gif/Cadence) detector is installed, every AI draft is scored 0–100 for AI-slop tells (uniform rhythm, hollow-confidence words, clichéd openers). If a draft reads as slop, Claude rewrites it once with the named tells fed back, and the cleaner version is kept. It's a no-op when the detector isn't installed.

```bash
npm install -g cadence-deslop                 # or: export CADENCE_DESLOP=/path/to/deslop.mjs
```

For a deeper voice pass, run the [`/cadence`](https://github.com/wuisabel-gif/Cadence) skill on any saved draft in `drafts/`.

## Use it in your AI assistant — no API key

**This is the recommended way.** Your own assistant does the writing, powered by
the Claude / Codex / ChatGPT subscription you already pay for — no API key, no
hosting, no per-message cost. The assistant learns your voice, drafts in it, and
cleans the AI-slop with Cadence.

**Skill** (Claude Code, Codex, Cursor — anything that reads skills):

Drop [`skills/linkedin-drafter/SKILL.md`](skills/linkedin-drafter/SKILL.md) into
your assistant's skills directory. Then just ask it to draft a LinkedIn message —
it follows the **learn → draft → deslop** flow, running `npx cadence-deslop --fix`
itself to clean the result.

**MCP server** (Claude Desktop, ChatGPT — apps that can't run a terminal):

These can't run `npx`, so they reach Cadence through an MCP tool instead. Install
the extra and register `linkedin-draft-mcp` in your MCP client:

```bash
pip install "linkedin-message-drafter[mcp]"
```

It exposes one tool — `deslop` — which cleans a draft with Cadence and returns
the tells still needing a voice rewrite. The assistant writes the draft; the tool
cleans it. Needs Node + `cadence-deslop` on the machine running the server.

Both paths stay draft-only — nothing is scraped or sent.

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
