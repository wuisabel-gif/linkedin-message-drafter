import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .ai import build_draft_ai
from .drafts import Prospect


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python -m linkedin_message_drafter.cli PATH_TO_PROSPECT_JSON", file=sys.stderr)
        return 2
    source = Path(sys.argv[1])
    try:
        prospect = Prospect.from_dict(json.loads(source.read_text(encoding="utf-8")))
        draft = build_draft_ai(prospect)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(draft)
    output_dir = Path("drafts")
    output_dir.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = output_dir / f"{stamp}-{prospect.name.lower().replace(' ', '-')}.txt"
    output.write_text(draft + "\n", encoding="utf-8")
    print(f"\nSaved draft to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
