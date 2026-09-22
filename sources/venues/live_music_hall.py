"""Venue-Scraper: Live Music Hall Köln.

TODO: Noch nicht implementiert. Beispiel-Pattern für klassisches HTML-Scraping,
falls kein JSON-Endpoint auffindbar ist:

    import requests
    from bs4 import BeautifulSoup
    from ..base import Event

    def fetch() -> list[Event]:
        resp = requests.get("https://www.livemusichall.de/programm", timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        events = []
        for card in soup.select(".event-card"):  # echten Selector anpassen
            events.append(
                Event(
                    artist=card.select_one(".event-title").get_text(strip=True),
                    date=card.select_one(".event-date")["datetime"],
                    venue="Live Music Hall",
                    city="Köln",
                    source="venue:live_music_hall",
                    url=card.select_one("a")["href"],
                )
            )
        return events

Ersetze das Platzhalter-fetch() unten, sobald die echten CSS-Selektoren
feststehen (per Browser-Inspector ermitteln).
"""

from __future__ import annotations

from ..base import Event


def fetch() -> list[Event]:
    # TODO: echtes HTML-Scraping für livemusichall.de ergänzen.
    return []
