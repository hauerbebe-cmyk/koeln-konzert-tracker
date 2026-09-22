"""Venue-Scraper: Palladium Köln.

TODO: Noch nicht implementiert. Beispiel-Pattern, falls die Venue-Website
ihre Termine über einen internen JSON-Endpoint nachlädt (im Netzwerk-Tab
der DevTools prüfen, Stichwort "events"/"shows"/"api"):

    import requests
    from ..base import Event

    def fetch() -> list[Event]:
        resp = requests.get("https://www.palladium-koeln.de/api/events", timeout=20)
        resp.raise_for_status()
        raw_events = resp.json()
        return [
            Event(
                artist=e["title"],
                date=e["date"],
                venue="Palladium Köln",
                city="Köln",
                source="venue:palladium",
                url=e.get("url"),
            )
            for e in raw_events
        ]

Ersetze das Platzhalter-fetch() unten, sobald der echte Endpoint bekannt ist.
"""

from __future__ import annotations

from ..base import Event


def fetch() -> list[Event]:
    # TODO: echten Endpoint/HTML-Parsing für palladium-koeln.de ergänzen.
    return []
