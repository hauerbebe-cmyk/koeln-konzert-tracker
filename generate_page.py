"""Erzeugt eine statische index.html aus known_events.json.

Wird von GitHub Pages gehostet -- keine eigene Server-Logik nötig, nur eine
Datei, die bei jedem Lauf neu geschrieben wird. Sortierung nach Datum passiert
client-seitig per JavaScript (Spaltenkopf antippen).
"""

from __future__ import annotations

import html
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

OUTPUT_PATH = Path(__file__).parent / "index.html"

# Events, die innerhalb dieses Zeitraums entdeckt wurden, gelten als "neu".
RECENTLY_ADDED_WINDOW = timedelta(days=3)


def generate(events: list[dict]) -> None:
    now = datetime.now(timezone.utc)

    recent = [
        e for e in events
        if _added_within(e, now, RECENTLY_ADDED_WINDOW)
    ]
    recent.sort(key=lambda e: e.get("added_at", ""), reverse=True)

    all_sorted = sorted(events, key=lambda e: e.get("date", ""))

    html_content = _render(recent, all_sorted, now)
    OUTPUT_PATH.write_text(html_content, encoding="utf-8")


def _added_within(event: dict, now: datetime, window: timedelta) -> bool:
    added_at = event.get("added_at")
    if not added_at:
        return False
    try:
        added_dt = datetime.fromisoformat(added_at)
    except ValueError:
        return False
    return now - added_dt <= window


def _event_row(e: dict, highlight: bool = False) -> str:
    artist = html.escape(e.get("artist", "Unbekannt"))
    date = html.escape((e.get("date") or "")[:10] or "Datum unbekannt")
    venue = html.escape(e.get("venue", ""))
    source = html.escape(e.get("source", ""))
    url = e.get("url")
    link = f'<a href="{html.escape(url)}" target="_blank" rel="noopener">Link</a>' if url else "–"
    cls = ' class="highlight"' if highlight else ""
    return (
        f"<tr{cls} data-date=\"{date}\">"
        f"<td>{date}</td><td>{artist}</td><td>{venue}</td>"
        f"<td class=\"source\">{source}</td><td>{link}</td></tr>"
    )


def _render(recent: list[dict], all_events: list[dict], now: datetime) -> str:
    recent_rows = "\n".join(_event_row(e, highlight=True) for e in recent) or (
        "<tr><td colspan=\"5\">Keine neuen Konzerte in den letzten Tagen.</td></tr>"
    )
    all_rows = "\n".join(_event_row(e) for e in all_events) or (
        "<tr><td colspan=\"5\">Noch keine Konzerte erfasst.</td></tr>"
    )
    updated_display = now.strftime("%d.%m.%Y %H:%M UTC")

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Köln Konzert Tracker</title>
<style>
  :root {{
    color-scheme: dark;
    --bg: #0d1117;
    --card: #161b22;
    --border: #30363d;
    --text: #e6edf3;
    --muted: #8b949e;
    --accent: #58a6ff;
    --highlight: #1f2d1f;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 1rem;
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }}
  h1 {{ font-size: 1.4rem; margin: 0 0 0.25rem; }}
  .updated {{ color: var(--muted); font-size: 0.85rem; margin-bottom: 1.5rem; }}
  h2 {{ font-size: 1.1rem; margin: 1.5rem 0 0.75rem; }}
  .card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow-x: auto;
    margin-bottom: 1.5rem;
  }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
  th, td {{
    text-align: left;
    padding: 0.6rem 0.75rem;
    border-bottom: 1px solid var(--border);
    white-space: nowrap;
  }}
  th {{
    color: var(--muted);
    font-weight: 600;
    cursor: pointer;
    user-select: none;
    position: sticky;
    top: 0;
    background: var(--card);
  }}
  th.sortable::after {{ content: " ⇅"; color: var(--muted); font-size: 0.75em; }}
  tr:last-child td {{ border-bottom: none; }}
  tr.highlight {{ background: var(--highlight); }}
  td.source {{ color: var(--muted); font-size: 0.8rem; }}
  a {{ color: var(--accent); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .count {{ color: var(--muted); font-weight: normal; font-size: 0.85rem; }}
</style>
</head>
<body>
  <h1>🎵 Köln Konzert Tracker</h1>
  <div class="updated">Zuletzt aktualisiert: {updated_display}</div>

  <h2>Zuletzt hinzugekommen <span class="count">(letzte {RECENTLY_ADDED_WINDOW.days} Tage)</span></h2>
  <div class="card">
    <table>
      <thead><tr><th>Datum</th><th>Artist</th><th>Venue</th><th>Quelle</th><th>Link</th></tr></thead>
      <tbody>{recent_rows}</tbody>
    </table>
  </div>

  <h2>Alle Konzerte <span class="count">({len(all_events)})</span></h2>
  <div class="card">
    <table id="all-table">
      <thead>
        <tr>
          <th class="sortable" data-col="0">Datum</th>
          <th class="sortable" data-col="1">Artist</th>
          <th class="sortable" data-col="2">Venue</th>
          <th>Quelle</th>
          <th>Link</th>
        </tr>
      </thead>
      <tbody>{all_rows}</tbody>
    </table>
  </div>

<script>
  // Einfache Client-seitige Sortierung per Spaltenkopf-Klick, kein Server nötig.
  document.querySelectorAll('#all-table th.sortable').forEach(function (th) {{
    var asc = true;
    th.addEventListener('click', function () {{
      var table = document.getElementById('all-table');
      var tbody = table.querySelector('tbody');
      var col = parseInt(th.getAttribute('data-col'), 10);
      var rows = Array.from(tbody.querySelectorAll('tr'));
      rows.sort(function (a, b) {{
        var av = a.children[col].innerText.trim().toLowerCase();
        var bv = b.children[col].innerText.trim().toLowerCase();
        if (av < bv) return asc ? -1 : 1;
        if (av > bv) return asc ? 1 : -1;
        return 0;
      }});
      rows.forEach(function (r) {{ tbody.appendChild(r); }});
      asc = !asc;
    }});
  }});
</script>
</body>
</html>
"""
