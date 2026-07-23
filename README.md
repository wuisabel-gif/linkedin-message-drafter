# LinkedIn Message Drafter

Write LinkedIn outreach that actually gets replies — personalized, warm, and ready in seconds. Feed it a name and a bit of context; it hands back a concise, human-sounding draft you can send as-is or tweak.

**Draft-first and safe by design.** It does **not** scrape LinkedIn, automate browser actions, or send anything on its own. You stay in control of every message — review, copy, send. Ready to automate? Wire in an approved LinkedIn integration through the adapter below.

## Quick start

```bash
cd ~/linkedin-message-drafter
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
PYTHONPATH=src python3 -m linkedin_message_drafter.cli src/linkedin_message_drafter/examples/prospect.json
```

The command prints a draft and saves it to `drafts/`.

## Input

See `src/linkedin_message_drafter/examples/prospect.json`. Required fields are `name`, `context`, and `goal`; `company`, `role`, and `relationship` are optional.

## Options

```bash
# Batch — pass multiple files or a whole folder of prospect JSONs
PYTHONPATH=src python3 -m linkedin_message_drafter.cli ./prospects/

# Connection-request note, guaranteed under LinkedIn's 300-char limit
PYTHONPATH=src python3 -m linkedin_message_drafter.cli --short my-prospect.json

# Write in a Cadence voice preset (AI path; needs CADENCE_VOICES)
export CADENCE_VOICES=/path/to/Cadence/voices
PYTHONPATH=src python3 -m linkedin_message_drafter.cli --style punchy my-prospect.json
```

`--short` works with both the template and AI paths; `--style` applies to AI drafts only. Available presets are the `.md` files in Cadence's `voices/` (`punchy`, `column`, `plain`, `dispatch`, …).

## AI drafting (optional)

Set `ANTHROPIC_API_KEY` to draft with Claude instead of the built-in template — richer, more personalized copy. With no key set, the tool uses the dependency-free template and works fully offline.

```bash
export ANTHROPIC_API_KEY=sk-ant-...
PYTHONPATH=src python3 -m linkedin_message_drafter.cli my-prospect.json
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

## Adding an approved API integration

`src/linkedin_message_drafter/linkedin.py` contains a deliberately unimplemented `LinkedInClient`. Implement only the endpoints and scopes that LinkedIn has approved for your application. Keep the default workflow draft-only and require a user confirmation before any send operation. Do not add scraping, credential collection, or bulk/unattended sending.

Read `TUTORIAL.md` before configuring credentials or requesting permissions.

## Tests

```bash
python -m unittest discover -s tests -v
```
