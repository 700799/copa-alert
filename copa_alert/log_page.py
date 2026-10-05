"""Event log published as a static page (docs/ is served by GitHub Pages)."""

import json
from dataclasses import asdict
from html import escape
from pathlib import Path

from .classes import Alerted, Session
from .notify import BOOKING_URL, REGISTER_URL, _session, _when

LOG_FILE = Path("docs/events.json")
PAGE_FILE = Path("docs/index.html")
MAX_EVENTS = 300


def load_events(path: Path = LOG_FILE) -> list[dict]:
    return json.loads(path.read_text()) if path.exists() else []


def record(events: list[dict], added: list[Session], gone: list[Alerted], now: str) -> list[dict]:
    """Return the log with this check's events first (newest first)."""
    new_events = [{"kind": "new", "at": now, "session": asdict(s)} for s in added]
    new_events += [{"kind": "gone", "at": now, "found_at": a.found_at, "session": asdict(a.session)} for a in gone]
    return (new_events + events)[:MAX_EVENTS]


def render(events: list[dict]) -> str:
    rows = []
    for e in events:
        s = Session(**e["session"])
        if e["kind"] == "new":
            spots = f" · {escape(s.spots_left)} spot{'' if s.spots_left == '1' else 's'}" if s.spots_left else ""
            link = f' <a href="{escape(REGISTER_URL.format(s.group_id))}">Register</a>' if s.group_id else ""
            detail = f"found {escape(_when(e['at']))}{spots}{link}"
        else:
            detail = f"gone {escape(_when(e['at']))} · found {escape(_when(e['found_at']))}"
        rows.append(
            f'<li class="{e["kind"]}"><span class="tag">{e["kind"].upper()}</span>'
            f'<div><div class="what">{escape(_session(s))}</div><div class="meta">{detail}</div></div></li>'
        )
    body = "\n".join(rows) if rows else '<li class="empty">No changes yet.</li>'
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>COPA Weekend Log</title>
<style>
:root {{ --bg:#fafafa; --fg:#1a1a1a; --muted:#666; --card:#fff; --line:#e5e5e5; --new:#1a7f37; --gone:#b42318; --link:#0b57d0; }}
@media (prefers-color-scheme: dark) {{
  :root {{ --bg:#121212; --fg:#eaeaea; --muted:#9a9a9a; --card:#1c1c1c; --line:#2c2c2c; --new:#4ac26b; --gone:#ff7b72; --link:#8ab4f8; }}
}}
body {{ margin:0; background:var(--bg); color:var(--fg); font:15px/1.45 system-ui, -apple-system, sans-serif; }}
main {{ max-width:640px; margin:0 auto; padding:20px 16px 40px; }}
h1 {{ font-size:20px; margin:0 0 4px; }}
p.sub {{ color:var(--muted); margin:0 0 16px; font-size:13px; }}
ul {{ list-style:none; padding:0; margin:0; }}
li {{ display:flex; gap:10px; align-items:flex-start; background:var(--card); border:1px solid var(--line); border-radius:8px; padding:10px 12px; margin-bottom:8px; }}
.tag {{ font-size:11px; font-weight:700; letter-spacing:.04em; padding:2px 6px; border-radius:4px; color:#fff; flex:none; margin-top:2px; }}
.new .tag {{ background:var(--new); }}
.gone .tag {{ background:var(--gone); }}
.gone .what {{ text-decoration:line-through; color:var(--muted); }}
.meta {{ color:var(--muted); font-size:13px; }}
a {{ color:var(--link); }}
.empty {{ color:var(--muted); }}
</style>
</head>
<body>
<main>
<h1>COPA 12–19 weekend sessions</h1>
<p class="sub">Sessions added to or removed from the Fri–Sun schedule, newest first. Times are Pacific. <a href="{BOOKING_URL}">All sessions on DaySmart</a></p>
<ul>
{body}
</ul>
</main>
</body>
</html>
"""


def update_page(added: list[Session], gone: list[Alerted], now: str) -> None:
    events = record(load_events(), added, gone, now)
    LOG_FILE.parent.mkdir(exist_ok=True)
    LOG_FILE.write_text(json.dumps(events, indent=1) + "\n")
    PAGE_FILE.write_text(render(events))
