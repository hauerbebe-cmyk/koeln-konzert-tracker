"""Fragt Eventim über die inoffizielle 'pyventim'-Bibliothek nach Konzerten in Köln ab.

Eventim bietet keine offizielle Public API. pyventim nutzt undokumentierte
JSON-Endpunkte der Eventim-Website und kann sich jederzeit ohne Vorwarnung
ändern -- prüfe bei Fehlern zuerst, ob sich die pyventim-API geändert hat:
https://pypi.org/project/pyventim/
"""

from __future__ import annotations

from .base import Event

TARGET_CITY = "Köln"


def fetch(city: str = TARGET_CITY) -> list[Event]:
    # Lazy import, damit das Modul nicht bricht, falls pyventim (noch) nicht
    # installiert ist oder Chromium für patchright fehlt.
    from pyventim import EventimCategory, EventimClient, EventimMarket

    client = EventimClient(EventimMarket.GERMANY)
    events: list[Event] = []

    for product_group in client.product_groups(
        categories=[EventimCategory.CONCERTS], page_limit=10
    ):
        group_city = getattr(product_group, "city", None) or getattr(
            product_group, "location", ""
        )
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
            )
        )

    return events
