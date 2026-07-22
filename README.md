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

## AI drafting (optional)

Set `ANTHROPIC_API_KEY` to draft with Claude instead of the built-in template — richer, more personalized copy. With no key set, the tool uses the dependency-free template and works fully offline.

```bash
export ANTHROPIC_API_KEY=sk-ant-...
PYTHONPATH=src python3 -m linkedin_message_drafter.cli my-prospect.json
```

### Sounds like you (Cadence)

Point `VOICE_SAMPLE` at a file of your own past writing (a few LinkedIn messages, an email, a blog post) and the AI draft matches your tone and rhythm — the same learn-from-a-sample approach as the Cadence voice skill, applied inline:

```bash
export VOICE_SAMPLE=~/my-writing-sample.txt
```

For a deeper voice pass, run the `/cadence` skill on any saved draft in `drafts/`.

## Adding an approved API integration

`src/linkedin_message_drafter/linkedin.py` contains a deliberately unimplemented `LinkedInClient`. Implement only the endpoints and scopes that LinkedIn has approved for your application. Keep the default workflow draft-only and require a user confirmation before any send operation. Do not add scraping, credential collection, or bulk/unattended sending.

Read `TUTORIAL.md` before configuring credentials or requesting permissions.

## Tests

```bash
python -m unittest discover -s tests -v
```
