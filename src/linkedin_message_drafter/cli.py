import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .ai import build_draft_ai
from .cadence import deslop
from .drafts import Prospect


def _load_prospects(paths: list[str]) -> list[Prospect]:
    """Load prospects from JSON files, directories of JSON, and CSV files.

    A directory contributes its *.json and *.csv; a CSV contributes one prospect
    per row (columns match the JSON fields). Bad rows/files raise ValueError/OSError.
    """
    prospects: list[Prospect] = []
    for p in paths:
        path = Path(p)
        sources = sorted([*path.glob("*.json"), *path.glob("*.csv")]) if path.is_dir() else [path]
        for src in sources:
            if src.suffix.lower() == ".csv":
                with src.open(encoding="utf-8", newline="") as f:
                    prospects.extend(Prospect.from_dict(row) for row in csv.DictReader(f))
            else:
                prospects.append(Prospect.from_dict(json.loads(src.read_text(encoding="utf-8"))))
    return prospects


def _save(draft: str, name: str) -> Path:
    output_dir = Path("drafts")
    output_dir.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = output_dir / f"{stamp}-{name.lower().replace(' ', '-')}.txt"
    output.write_text(draft + "\n", encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="linkedin-draft",
        description="Draft personalized LinkedIn outreach. Never scrapes or sends.",
    )
    parser.add_argument("paths", nargs="+", metavar="PATH",
                        help="prospect JSON/CSV file(s) or director(ies) of them (batch)")
    parser.add_argument("--short", action="store_true",
                        help="connection-request note under 300 characters")
    parser.add_argument("--style", default="",
                        help="Cadence voice preset name (needs CADENCE_VOICES); AI path only")
    parser.add_argument("--best-of", type=int, default=1, metavar="N",
                        help="generate N AI drafts and keep the least AI-slop one (default 1)")
    args = parser.parse_args()

    try:
        prospects = _load_prospects(args.paths)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    if not prospects:
        print("No prospects found.", file=sys.stderr)
        return 2

    for i, prospect in enumerate(prospects):
        if i:
            print("\n" + "=" * 40 + "\n")
        draft = build_draft_ai(prospect, short=args.short, style=args.style, best_of=args.best_of)
        print(draft)
        report = deslop(draft)  # show the Cadence score when the detector is available
        if report:
            print(f"\nCadence: {report['score']}/100 (grade {report['grade']}), {len(draft)} chars")
        print(f"Saved draft to {_save(draft, prospect.name)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
