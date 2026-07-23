"""Optional AI-backed draft generation via the Claude API.

Falls back to the deterministic template in drafts.py when no API key is set,
so the tool still works offline and in tests. Set ANTHROPIC_API_KEY to enable.
"""
from __future__ import annotations

import os
from pathlib import Path

from .drafts import Prospect, build_draft

MODEL = "claude-opus-4-8"  # ponytail: swap to claude-haiku-4-5 if cost matters more than polish

# Cadence (https://github.com/wuisabel-gif/Cadence) collaboration: point
# VOICE_SAMPLE at your own past writing and the draft is written to match that
# voice. It accepts either a single file OR a directory — point it at a folder of
# all your previous posts and messages and Cadence learns from the whole corpus.
# This is Cadence's learn-from-a-sample mechanism inline; for a deeper voice pass,
# run the /cadence skill on a saved draft in drafts/.
VOICE_SAMPLE = os.environ.get("VOICE_SAMPLE")


def _load_voice(path: str) -> str:
    """Return the writing sample(s): one file's text, or every file in a directory."""
    p = Path(path)
    if p.is_file():
        return p.read_text(encoding="utf-8").strip()
    if p.is_dir():
        # ponytail: reads every readable file, sorted; 1M context easily holds a
        # personal corpus. If yours is huge, keep the most representative samples.
        texts = []
        for f in sorted(p.rglob("*")):
            if f.is_file() and not f.name.startswith("."):
                try:
                    texts.append(f.read_text(encoding="utf-8").strip())
                except (UnicodeDecodeError, OSError):
                    continue  # skip binaries / unreadable files
        return "\n\n---\n\n".join(t for t in texts if t)
    return ""


def build_draft_ai(prospect: Prospect) -> str:
    """Draft with Claude if credentials resolve; otherwise fall back to the template.

    Any credential the SDK understands works — ANTHROPIC_API_KEY, an `ant auth
    login` profile, etc. On missing creds, no SDK, or an API error, we fall back
    so the tool always produces a draft. (ponytail: broad fallback is deliberate.)
    """
    try:
        import anthropic  # lazy: the template path needs no dependency
    except ImportError:
        return build_draft(prospect)

    facts = "\n".join(
        f"- {k}: {v}"
        for k, v in (
            ("name", prospect.name), ("context", prospect.context), ("goal", prospect.goal),
            ("company", prospect.company), ("role", prospect.role),
            ("relationship", prospect.relationship),
        ) if v
    )
    system = (
        "Write one short, warm LinkedIn outreach message (3-5 sentences). "
        "Greet by first name, reference the specific context, state the goal, "
        "end with a low-pressure ask. No subject line, no emoji, no hashtags, "
        "no placeholders. Sign off with 'Best,' and nothing after it. "
        "Output only the message."
    )
    sample = _load_voice(VOICE_SAMPLE) if VOICE_SAMPLE else ""
    if sample:
        system += (
            "\n\nMatch the voice of these writing samples — tone, rhythm, word "
            "choice, and sentence rhythm. Mimic how this person speaks; do not "
            f"copy their content:\n\n{sample}"
        )
    try:
        resp = anthropic.Anthropic().messages.create(
            model=MODEL,
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": facts}],
        )
        return next(b.text for b in resp.content if b.type == "text").strip()
    except anthropic.AnthropicError:  # no creds, auth failure, API/connection error
        return build_draft(prospect)
