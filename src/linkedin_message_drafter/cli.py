import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from .ai import build_draft_ai
from .cadence import deslop
from .drafts import Prospect

try:
    __version__ = version("linkedin-message-drafter")
except PackageNotFoundError:  # running from source without an install
    __version__ = "0.0.0+source"


def _iter_prospects(paths: list[str]):
    """Yield (label, prospect, error) per item across JSON/CSV files and directories.

    A directory contributes its *.json and *.csv; a CSV contributes one prospect
    per row. A bad file or row yields an error for that item only — the rest of
    the batch still drafts.
    """
    for p in paths:
        path = Path(p)
        sources = sorted([*path.glob("*.json"), *path.glob("*.csv")]) if path.is_dir() else [path]
        for src in sources:
            if src.suffix.lower() == ".csv":
                try:
                    rows = list(csv.DictReader(src.open(encoding="utf-8", newline="")))
                except OSError as exc:
                    yield (str(src), None, str(exc))
                    continue
                for i, row in enumerate(rows, start=2):  # row 1 is the header
                    try:
                        yield (f"{src}:row {i}", Prospect.from_dict(row), None)
                    except ValueError as exc:
                        yield (f"{src}:row {i}", None, str(exc))
            else:
                try:
                    yield (str(src), Prospect.from_dict(json.loads(src.read_text(encoding="utf-8"))), None)
                except (OSError, json.JSONDecodeError, ValueError) as exc:
                    yield (str(src), None, str(exc))


def _save(draft: str, name: str) -> Path:
    output_dir = Path("drafts")
    output_dir.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = f"{stamp}-{name.lower().replace(' ', '-')}"
    output = output_dir / f"{base}.txt"
    n = 2  # never overwrite a draft from the same second (batch, duplicate names)
    while output.exists():
        output = output_dir / f"{base}-{n}.txt"
        n += 1
    output.write_text(draft + "\n", encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="linkedin-draft",
        description="Draft personalized LinkedIn outreach. Never scrapes or sends.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("paths", nargs="+", metavar="PATH",
                        help="prospect JSON/CSV file(s) or director(ies) of them (batch)")
    parser.add_argument("--short", action="store_true",
                        help="connection-request note under 300 characters")
    parser.add_argument("--style", default="",
                        help="Cadence voice preset name (needs CADENCE_VOICES); AI path only")
    parser.add_argument("--best-of", type=int, default=1, metavar="N",
                        help="generate N AI drafts and keep the least AI-slop one (default 1)")
    args = parser.parse_args()

    found = drafted = rc = 0
    for label, prospect, error in _iter_prospects(args.paths):
        found += 1
        if error:
            print(f"Skipped {label}: {error}", file=sys.stderr)
            rc = 1
            continue
        if drafted:
            print("\n" + "=" * 40 + "\n")
        drafted += 1
        draft = build_draft_ai(prospect, short=args.short, style=args.style, best_of=args.best_of)
        print(draft)
        report = deslop(draft)  # show the Cadence score when the detector is available
        if report:
            print(f"\nCadence: {report['score']}/100 (grade {report['grade']}), {len(draft)} chars")
        print(f"Saved draft to {_save(draft, prospect.name)}")
    if not found:
        print("No prospects found.", file=sys.stderr)
        return 2
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
