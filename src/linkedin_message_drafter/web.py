"""Tiny local web UI over build_draft_ai — zero dependencies (stdlib http.server).

Run:  linkedin-draft-web        (or: python -m linkedin_message_drafter.web)
Then open http://127.0.0.1:8000 . Binds to localhost only; drafts still save to
drafts/ and nothing is sent anywhere. ponytail: stdlib server, no web framework.
"""
from __future__ import annotations

import html
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

from .ai import build_draft_ai
from .cadence import deslop
from .drafts import Prospect

FIELDS = ("name", "context", "goal", "company", "role", "relationship")

PAGE = """<!doctype html><meta charset=utf-8><title>LinkedIn Message Drafter</title>
<style>
 body{{font:16px/1.5 system-ui,sans-serif;max-width:640px;margin:2rem auto;padding:0 1rem}}
 label{{display:block;margin:.6rem 0 .2rem;font-weight:600}}
 input,textarea{{width:100%;padding:.5rem;font:inherit;box-sizing:border-box}}
 .row{{display:flex;gap:1rem}}.row>div{{flex:1}}
 button{{margin-top:1rem;padding:.6rem 1.2rem;font:inherit;cursor:pointer}}
 pre{{white-space:pre-wrap;background:#f4f4f4;padding:1rem;border-radius:6px}}
 .meta{{color:#555;font-size:.9rem}} .err{{color:#b00}}
</style>
<h1>LinkedIn Message Drafter</h1>
<p class=meta>Draft-first. Never scrapes or sends — you copy and send yourself.</p>
<form method=post>
 <label>Name*</label><input name=name required value="{name}">
 <label>Context* — the specific thing you noticed</label>
 <textarea name=context rows=2 required>{context}</textarea>
 <label>Goal* — what you want, in one line</label>
 <textarea name=goal rows=2 required>{goal}</textarea>
 <div class=row>
  <div><label>Company</label><input name=company value="{company}"></div>
  <div><label>Role</label><input name=role value="{role}"></div>
 </div>
 <label>Relationship</label><input name=relationship value="{relationship}">
 <div class=row>
  <div><label>Style preset (optional)</label><input name=style value="{style}"></div>
  <div><label><input type=checkbox name=short {short}> Short (≤300-char note)</label></div>
 </div>
 <button>Draft</button>
</form>
{result}
"""

RESULT = """<h2>Draft</h2><pre id=d>{draft}</pre>
<p class=meta>{meta}</p>
<button onclick="navigator.clipboard.writeText(document.getElementById('d').innerText)">Copy</button>
"""


def _render(values: dict, result: str = "") -> bytes:
    fill = {f: html.escape(values.get(f, "")) for f in FIELDS}
    fill["style"] = html.escape(values.get("style", ""))
    fill["short"] = "checked" if values.get("short") else ""
    fill["result"] = result
    return PAGE.format(**fill).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    def _send(self, body: bytes):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._send(_render({}))

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        form = parse_qs(self.rfile.read(length).decode("utf-8"))
        values = {k: (v[0] if v else "") for k, v in form.items()}
        try:
            prospect = Prospect.from_dict(values)
            draft = build_draft_ai(prospect, short="short" in form, style=values.get("style", ""))
        except ValueError as exc:
            self._send(_render(values, f'<p class="err">{html.escape(str(exc))}</p>'))
            return
        report = deslop(draft)
        meta = f"Cadence {report['score']}/100 (grade {report['grade']}), " \
               f"{len(draft)} chars" if report else f"{len(draft)} chars"
        result = RESULT.format(draft=html.escape(draft), meta=meta)
        self._send(_render(values, result))

    def log_message(self, *args):  # quiet: no per-request stderr noise
        pass


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    try:
        server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    except OSError as exc:
        print(f"Cannot start on port {port}: {exc}.\n"
              f"Try another port:  linkedin-draft-web {port + 1}", file=sys.stderr)
        return 1
    print(f"Serving on http://127.0.0.1:{port}  (Ctrl-C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
