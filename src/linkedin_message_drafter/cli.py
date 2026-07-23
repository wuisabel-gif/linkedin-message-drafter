import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .ai import build_draft_ai
from .drafts import Prospect


def _prospect_files(paths: list[str]) -> list[Path]:
    """Expand paths into prospect JSON files (a directory contributes its *.json)."""
    files: list[Path] = []
    for p in paths:
        path = Path(p)
        files.extend(sorted(path.glob("*.json")) if path.is_dir() else [path])
    return files


def _draft_one(source: Path, short: bool, style: str) -> int:
    try:
        prospect = Prospect.from_dict(json.loads(source.read_text(encoding="utf-8")))
        draft = build_draft_ai(prospect, short=short, style=style)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"Error ({source}): {exc}", file=sys.stderr)
        return 1
    print(draft)
    output_dir = Path("drafts")
    output_dir.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = output_dir / f"{stamp}-{prospect.name.lower().replace(' ', '-')}.txt"
    output.write_text(draft + "\n", encoding="utf-8")
    print(f"\nSaved draft to {output}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="linkedin_message_drafter.cli",
        description="Draft personalized LinkedIn outreach. Never scrapes or sends.",
    )
    parser.add_argument("paths", nargs="+", metavar="PATH",
                        help="prospect JSON file(s) or director(ies) of them (batch)")
    parser.add_argument("--short", action="store_true",
                        help="connection-request note under 300 characters")
    parser.add_argument("--style", default="",
                        help="Cadence voice preset name (needs CADENCE_VOICES); AI path only")
    args = parser.parse_args()

    files = _prospect_files(args.paths)
    if not files:
        print("No prospect JSON files found.", file=sys.stderr)
        return 2
    rc = 0
    for i, source in enumerate(files):
        if i:
            print("\n" + "=" * 40 + "\n")
        rc |= _draft_one(source, args.short, args.style)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
