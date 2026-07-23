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


def deslop(text: str) -> dict | None:
    """Return cadence-deslop's JSON report for `text` (score/grade/findings), or None.

    None means the tool wasn't available or errored — callers treat that as
    "skip the slop check", never as a clean score.
    """
    cmd = _command()
    if not cmd:
        return None
    try:
        proc = subprocess.run(
            [*cmd, "--json"], input=text,
            capture_output=True, text=True, timeout=30,
        )
        return json.loads(proc.stdout)  # empty/failed stdout -> ValueError -> None
    except (OSError, ValueError, subprocess.SubprocessError):
        return None
