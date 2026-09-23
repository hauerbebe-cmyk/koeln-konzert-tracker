"""Fragt Eventim über die inoffizielle 'pyventim'-Bibliothek nach Konzerten in Köln ab.

Eventim bietet keine offizielle Public API. pyventim nutzt undokumentierte
JSON-Endpunkte der Eventim-Website und kann sich jederzeit ohne Vorwarnung
ändern -- prüfe bei Fehlern zuerst, ob sich die pyventim-API geändert hat:
https://pypi.org/project/pyventim/
"""

from __future__ import annotations

import sys

from .base import Event

TARGET_CITY = "Köln"


def fetch(city: str = TARGET_CITY) -> list[Event]:
    from pyventim import EventimCategory, EventimClient, EventimMarket

    client = EventimClient(EventimMarket.GERMANY)
    events: list[Event] = []
    total_seen = 0
    sample_logged = False

    for product_group in client.product_groups(
        categories=[EventimCategory.CONCERTS], page_limit=10
    ):
        total_seen += 1
        group_city = getattr(product_group, "city", None) or getattr(
            product_group, "location", ""
        )

        # Debug: einmalig zeigen, wie ein Rohdaten-Objekt aussieht, damit wir
        # sehen, ob "city"/"location" überhaupt sinnvoll befüllt sind.
        if not sample_logged:
            print(f"[DEBUG eventim] Beispiel-Objekt: {vars(product_group)}", file=sys.stderr)
            sample_logged = True

        if city.lower() not in str(group_city).lower():
            continue

        events.append(
            Event(
                artist=getattr(product_group, "name", "Unbekannter Act"),
                date=str(getattr(product_group, "start_date", "")),
                venue=str(group_city) or city,
                city=city,
                source="eventim",
                url=getattr(product_group, "url", None),
                image_url=getattr(product_group, "image", None)
                or getattr(product_group, "image_url", None),
            )
        )

    print(f"[DEBUG eventim] {total_seen} Konzerte insgesamt gesehen, {len(events)} nach Köln-Filter.", file=sys.stderr)
    return events
