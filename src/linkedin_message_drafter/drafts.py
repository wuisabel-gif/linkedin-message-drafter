from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Prospect:
    name: str
    context: str
    goal: str
    company: str = ""
    role: str = ""
    relationship: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "Prospect":
        missing = [key for key in ("name", "context", "goal") if not str(data.get(key, "")).strip()]
        if missing:
            raise ValueError("Missing required field(s): " + ", ".join(missing))
        return cls(
            name=str(data["name"]).strip(), context=str(data["context"]).strip(),
            goal=str(data["goal"]).strip(), company=str(data.get("company", "")).strip(),
            role=str(data.get("role", "")).strip(), relationship=str(data.get("relationship", "")).strip(),
        )


NOTE_LIMIT = 300  # LinkedIn connection-request notes are capped at 300 characters


def _sentence(text: str) -> str:
    # Uppercase first letter only; str.capitalize() would lowercase "ML", "Q4", etc.
    text = text.rstrip(".")
    return text[:1].upper() + text[1:]


def fit(text: str, limit: int = NOTE_LIMIT) -> str:
    """Trim text to `limit` chars at a word boundary (adds an ellipsis if cut)."""
    text = text.strip()
    if len(text) <= limit:
        return text
    cut = text[: limit - 1].rsplit(" ", 1)[0].rstrip(",.;:—- ")
    return cut + "…"


def build_draft(prospect: Prospect, short: bool = False) -> str:
    """Create a concise draft without contacting LinkedIn or any external service.

    short=True returns a one-line note that fits LinkedIn's 300-char connection
    request limit; otherwise a full multi-line message.
    """
    first_name = prospect.name.split()[0]
    # ponytail: simple string assembly; swap for an LLM prompt if you want richer copy.
    at_company = f" at {prospect.company}" if prospect.company else ""
    if short:
        note = (
            f"Hi {first_name}, {_sentence(prospect.context)} caught my eye. "
            f"{_sentence(prospect.goal)}. Open to connecting?"
        )
        return fit(note)
    role = f", and what you're doing as {prospect.role}{at_company}" if prospect.role else at_company
    return (
        f"Hi {first_name},\n\n"
        f"{_sentence(prospect.context)} caught my eye{role}. "
        f"{_sentence(prospect.goal)}.\n\n"
        "Would a quick 15-minute chat be worth it? Happy to work around your schedule — "
        "and no worries if the timing isn't right.\n\n"
        "Best,"
    )
