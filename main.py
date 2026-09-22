"""Köln Konzert Tracker -- Hauptskript.

Fragt alle konfigurierten Quellen ab, ermittelt neue Konzerte gegenüber dem
letzten Lauf, verschickt Push-Benachrichtigungen und aktualisiert
known_events.json.

Aufruf: python main.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import generate_page
from dedupe import find_new_events
from notify import send_new_event_notifications
from sources import eventim, ticketmaster
from sources.base import Event
from sources.venues import gloria_theater, live_music_hall, palladium

KNOWN_EVENTS_PATH = Path(__file__).parent / "known_events.json"

# Neue Venue? Hier eintragen -- Modul muss ein fetch() -> list[Event] haben.
VENUE_MODULES = [palladium, live_music_hall, gloria_theater]


def load_known_events() -> list[dict]:
    if not KNOWN_EVENTS_PATH.exists():
        return []
    return json.loads(KNOWN_EVENTS_PATH.read_text(encoding="utf-8"))


def save_known_events(events: list[dict]) -> None:
    KNOWN_EVENTS_PATH.write_text(
        json.dumps(events, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def collect_all_events() -> list[Event]:
    all_events: list[Event] = []

    for source_name, fetch_fn in [
        ("ticketmaster", ticketmaster.fetch),
        ("eventim", eventim.fetch),
    ]:
        try:
            all_events.extend(fetch_fn())
        except Exception as exc:  # noqa: BLE001 -- eine Quelle darf den Rest nicht blockieren
            print(f"[WARN] Quelle '{source_name}' fehlgeschlagen: {exc}", file=sys.stderr)

    for module in VENUE_MODULES:
        try:
            all_events.extend(module.fetch())
        except Exception as exc:  # noqa: BLE001
            print(f"[WARN] Venue-Modul '{module.__name__}' fehlgeschlagen: {exc}", file=sys.stderr)

    return all_events


def main() -> None:
    known_events = load_known_events()

    fresh_events = collect_all_events()
    print(f"{len(fresh_events)} Events aus allen Quellen abgerufen.")

    new_events = find_new_events(fresh_events, known_events)
    print(f"{len(new_events)} davon sind neu.")

    if new_events:
        send_new_event_notifications(new_events)

    discovered_at = datetime.now(timezone.utc).isoformat()
    updated_known = known_events + [
        {**e.to_dict(), "added_at": discovered_at} for e in new_events
    ]
    save_known_events(updated_known)

    generate_page.generate(updated_known)
    print("index.html aktualisiert.")


if __name__ == "__main__":
    main()
