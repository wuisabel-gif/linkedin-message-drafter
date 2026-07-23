"""Optional AI-backed draft generation via the Claude API.

Falls back to the deterministic template in drafts.py when no API key is set,
so the tool still works offline and in tests. Set ANTHROPIC_API_KEY to enable.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from .cadence import deslop
from .drafts import NOTE_LIMIT, Prospect, build_draft, fit

MODEL = "claude-opus-4-8"  # ponytail: swap to claude-haiku-4-5 if cost matters more than polish
SLOP_THRESHOLD = 15  # cadence-deslop score above which we ask Claude to rewrite once

# --style <name> loads a Cadence voice preset (voices/<name>.md) as a style guide.
# Point CADENCE_VOICES at Cadence's voices/ dir; unknown/missing presets are ignored.
STYLE_DIR = os.environ.get("CADENCE_VOICES")


def _load_style(name: str) -> str:
    """Return the text of a Cadence voice preset, or '' if unavailable."""
    if not name or not STYLE_DIR:
        return ""
    preset = Path(STYLE_DIR) / f"{name}.md"
    if preset.is_file():
        return preset.read_text(encoding="utf-8").strip()
    print(f"Note: style preset '{name}' not found in {STYLE_DIR}; ignoring.", file=sys.stderr)
    return ""

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


def build_draft_ai(prospect: Prospect, short: bool = False, style: str = "",
                   best_of: int = 1) -> str:
    """Draft with Claude if credentials resolve; otherwise fall back to the template.

    Any credential the SDK understands works — ANTHROPIC_API_KEY, an `ant auth
    login` profile, etc. On missing creds, no SDK, or an API error, we fall back
    so the tool always produces a draft. (ponytail: broad fallback is deliberate.)

    short=True targets LinkedIn's 300-char connection-note limit. style names a
    Cadence voice preset (see CADENCE_VOICES). best_of>1 generates that many
    candidates and keeps whichever cadence-deslop scores cleanest.
    """
    try:
        import anthropic  # lazy: the template path needs no dependency
    except ImportError:
        return build_draft(prospect, short=short)

    facts = "\n".join(
        f"- {k}: {v}"
        for k, v in (
            ("name", prospect.name), ("context", prospect.context), ("goal", prospect.goal),
            ("company", prospect.company), ("role", prospect.role),
            ("relationship", prospect.relationship),
        ) if v
    )
    if short:
        system = (
            "Write a LinkedIn connection-request note — one or two sentences, "
            f"strictly under {NOTE_LIMIT} characters. Greet by first name, name "
            "the specific context, and make a brief low-pressure ask. No emoji, "
            "no hashtags, no sign-off, no placeholders. Output only the note."
        )
    else:
        system = (
            "Write one short, warm LinkedIn outreach message (3-5 sentences). "
            "Greet by first name, reference the specific context, state the goal, "
            "end with a low-pressure ask. No subject line, no emoji, no hashtags, "
            "no placeholders. Sign off with 'Best,' and nothing after it. "
            "Output only the message."
        )
    preset = _load_style(style)
    if preset:
        system += f"\n\nWrite in this voice:\n\n{preset}"
    sample = _load_voice(VOICE_SAMPLE) if VOICE_SAMPLE else ""
    if sample:
        system += (
            "\n\nMatch the voice of these writing samples — tone, rhythm, word "
            "choice, and sentence rhythm. Mimic how this person speaks; do not "
            f"copy their content:\n\n{sample}"
        )
    def generate(sys_prompt: str) -> str:
        resp = anthropic.Anthropic().messages.create(
            model=MODEL, max_tokens=1024, system=sys_prompt,
            messages=[{"role": "user", "content": facts}],
        )
        text = next(b.text for b in resp.content if b.type == "text").strip()
        return fit(text) if short else text  # hard-cap short notes at 300 chars

    try:
        candidates = [generate(system) for _ in range(max(1, best_of))]
    except anthropic.AnthropicError:  # no creds, auth failure, API/connection error
        return build_draft(prospect, short=short)

    # Best-of-N: score each candidate with the real cadence-deslop detector and
    # keep the cleanest. When the detector isn't installed, take the first draft.
    reports = [deslop(c) for c in candidates]
    if any(r is not None for r in reports):
        best = min(range(len(candidates)),
                   key=lambda i: reports[i]["score"] if reports[i] else 10**6)
        draft, report = candidates[best], reports[best]
    else:
        return candidates[0]

    # If the cleanest draft still reads as slop, rewrite once with the named
    # tells fed back and keep whichever the detector scores cleaner.
    if report and report.get("score", 0) > SLOP_THRESHOLD and report.get("findings"):
        tells = ", ".join(sorted({f["rule"] for f in report["findings"]}))
        retry_system = system + (
            f"\n\nThe previous draft scored {report['score']}/100 on the Cadence "
            f"AI-slop detector, flagged for: {tells}. Rewrite to eliminate those "
            "tells — vary sentence rhythm, and cut hollow-confidence words, "
            "reflexive triads, and clichéd openers."
        )
        try:
            retry = generate(retry_system)
        except anthropic.AnthropicError:
            return draft
        retry_report = deslop(retry)
        if retry_report and retry_report.get("score", 100) < report["score"]:
            return retry  # keep whichever the detector scores cleaner
    return draft
