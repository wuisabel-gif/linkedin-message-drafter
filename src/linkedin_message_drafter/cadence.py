"""Cadence integration — score drafts with the real cadence-deslop detector.

Calls the published cadence-deslop package (https://github.com/wuisabel-gif/Cadence),
a deterministic AI-slop detector that scores prose 0-100 and names each AI tell.
Returns None whenever the tool isn't installed, so the draft path degrades cleanly.

Make it available either way:
  - npm install -g cadence-deslop        (puts `cadence-deslop` on PATH), or
  - export CADENCE_DESLOP=/path/to/skills/cadence/scripts/deslop.mjs
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess


def _command() -> list[str] | None:
    """Resolve how to invoke cadence-deslop, or None if it isn't available."""
    script = os.environ.get("CADENCE_DESLOP")  # explicit path to deslop.mjs
    if script:
        return ["node", script]
    binary = shutil.which("cadence-deslop")
    return [binary] if binary else None


def _run(args: list[str], text: str) -> subprocess.CompletedProcess | None:
    cmd = _command()
    if not cmd:
        return None
    try:
        return subprocess.run([*cmd, *args], input=text,
                              capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None


def deslop(text: str) -> dict | None:
    """Return cadence-deslop's JSON report for `text` (score/grade/findings), or None.

    None means the tool wasn't available or errored — callers treat that as
    "skip the slop check", never as a clean score.
    """
    proc = _run(["--json"], text)
    if not proc:
        return None
    try:
        return json.loads(proc.stdout)  # empty/failed stdout -> ValueError -> None
    except ValueError:
        return None


def deslop_fix(text: str) -> dict | None:
    """Mechanically clean AI-slop from `text` with cadence-deslop --fix.

    Returns {"cleaned": str, "remaining": [rule, ...]} — the auto-cleaned text
    plus the tells that still need a manual (voice) rewrite. None if unavailable.
    """
    proc = _run(["--fix"], text)
    if not proc or not proc.stdout:
        return None
    cleaned = proc.stdout.rstrip("\n")
    report = deslop(cleaned)  # what still needs a human/LLM rewrite
    remaining = sorted({f["rule"] for f in report["findings"]}) if report else []
    return {"cleaned": cleaned, "remaining": remaining}
