# SOP: Drafting a LinkedIn Outreach Message

**Purpose:** Turn a prospect's details into a personalized, ready-to-send LinkedIn draft.
**Scope:** Draft-only. This tool never contacts, scrapes, or messages LinkedIn. You send messages yourself.
**Time:** ~2 minutes per prospect.

---

## How it works (the flow)

```
prospect.json  →  CLI  →  validate fields  →  build draft  →  print + save to drafts/
```

1. You write a small JSON file describing one prospect.
2. The CLI (`cli.py`) reads it and validates the three required fields.
3. `build_draft()` assembles a concise message from your inputs — pure string templating, no network, no AI, no API.
4. The draft is printed to your screen **and** saved as a timestamped `.txt` in `drafts/`.
5. You review, copy, and paste it into LinkedIn manually.

---

## One-time setup

```bash
cd ~/linkedin-message-drafter
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt   # no third-party deps; harmless to run
```

---

## Procedure (per prospect)

### Step 1 — Create the input file

Copy the example and edit it:

```bash
cp src/linkedin_message_drafter/examples/prospect.json my-prospect.json
```

Fill in the fields:

| Field          | Required | What to put                                              |
|----------------|----------|----------------------------------------------------------|
| `name`         | ✅       | Full name. Only the first name is used in the greeting.  |
| `context`      | ✅       | The specific thing you noticed (a post, talk, project).  |
| `goal`         | ✅       | What you want — one plain sentence.                      |
| `company`      | ⬜       | Their company. Appears only if `role` is also set.       |
| `role`         | ⬜       | Their title, e.g. "Head of Growth".                      |
| `relationship` | ⬜       | Reserved for future use.                                 |

**Tip:** Write `context` and `goal` in lowercase or sentence case — the tool capitalizes the first letter for you (and preserves acronyms like `ML`, `Q4`).

### Step 2 — Generate the draft

```bash
PYTHONPATH=src python3 -m linkedin_message_drafter.cli my-prospect.json
```

You'll see the draft printed, plus a line like:

```
Saved draft to drafts/20260722T191758Z-alex-rivera.txt
```

### Step 3 — Review and send

1. Open the printed draft (or the saved file in `drafts/`).
2. Read it top to bottom. Adjust anything that sounds off.
3. Copy it into a LinkedIn connection request or message. **You do this manually.**

---

## Quality checklist before sending

- [ ] First name is correct (greeting uses `name.split()[0]`).
- [ ] The `context` line names something real and specific to them.
- [ ] The ask (`goal`) is clear and matches what you actually want.
- [ ] `role`/`company` read naturally — a real title works best (e.g. "Head of Partnerships", not "partnerships").
- [ ] No leftover placeholder text.

---

## Troubleshooting

| Message                                   | Cause                            | Fix                                          |
|-------------------------------------------|----------------------------------|----------------------------------------------|
| `Missing required field(s): ...`          | Empty/absent name, context, goal | Fill those fields in the JSON.               |
| `Error: Expecting value: line 1 ...`      | Malformed JSON                   | Check commas, quotes, and braces.            |
| `Usage: python -m ... PATH_TO_...JSON`    | No file path passed              | Pass exactly one path argument.              |
| `ModuleNotFoundError`                     | `PYTHONPATH=src` missing         | Prefix the command with `PYTHONPATH=src`.    |

---

## Do NOT

- Do not use this to bulk-send or auto-send. It has no send capability by default.
- Do not scrape LinkedIn or collect credentials.
- The `LinkedInClient` in `linkedin.py` is an unimplemented stub. Only wire it up with **LinkedIn-approved** messaging permissions, and keep a human confirmation before any send. See `TUTORIAL.md`.

---

## Verify the tool is healthy

```bash
python -m unittest discover -s tests -v
```

All tests should pass before relying on a draft.
