"""Erkennt neue Events und Duplikate zwischen mehreren Quellen.

Zwei Ebenen:
1. Exakte ID (Artist+Datum+Venue) -- verhindert, dass dieselbe Quelle beim
   nächsten Lauf erneut pingt.
2. Fuzzy-Match auf Artist-Name + gleiches Datum, unabhängig von der Venue-
   Schreibweise -- verhindert Doppel-Pings, wenn z.B. Ticketmaster und
   Eventim dasselbe Konzert leicht unterschiedlich benennen.
"""

from __future__ import annotations

from rapidfuzz import fuzz

from sources.base import Event

FUZZY_ARTIST_THRESHOLD = 88  # 0-100, höher = strenger


def find_new_events(fresh_events: list[Event], known_events: list[dict]) -> list[Event]:
    known_ids = {e["id"] for e in known_events}
    known_by_date: dict[str, list[dict]] = {}
    for e in known_events:
        known_by_date.setdefault(e["date"][:10], []).append(e)

    new_events: list[Event] = []
    seen_in_this_run: list[Event] = []

    for event in fresh_events:
        if event.id in known_ids:
            continue
        if _is_fuzzy_duplicate(event, known_by_date.get(event.date[:10], [])):
            continue
        if _is_fuzzy_duplicate(event, [e.to_dict() for e in seen_in_this_run]):
            # Gleiches Konzert von zwei Quellen im selben Lauf -> nur einmal pingen.
            continue

        new_events.append(event)
        seen_in_this_run.append(event)

    return new_events


def _is_fuzzy_duplicate(event: Event, candidates: list[dict]) -> bool:
    for candidate in candidates:
        score = fuzz.token_sort_ratio(event.artist.lower(), candidate["artist"].lower())
        if score >= FUZZY_ARTIST_THRESHOLD:
            return True
    return False
