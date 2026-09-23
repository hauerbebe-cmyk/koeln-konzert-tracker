"""Fragt Eventim über die inoffizielle 'pyventim'-Bibliothek nach Konzerten in Köln ab.

Eventim bietet keine offizielle Public API. pyventim nutzt undokumentierte
JSON-Endpunkte der Eventim-Website und kann sich jederzeit ohne Vorwarnung
ändern -- prüfe bei Fehlern zuerst, ob sich die pyventim-API geändert hat:
https://pypi.org/project/pyventim/

Hinweis: product_groups() selbst hat keinen Stadt-Filter (der existiert nur
pro-Tour bei products(), was bei hunderten Touren zu langsam wäre). Wir nutzen
daher Eventims eigene Volltextsuche (search_term="Köln"), die wie auf der
Website selbst auch nach Stadt matcht, und prüfen zusätzlich, wo möglich, die
verschachtelte Standort-Info als zweite Absicherung.
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

    for product_group in client.product_groups(
        categories=[EventimCategory.CONCERTS],
        search_term=city,
        page_limit=10,
    ):
        total_seen += 1
        location = _extract_location(product_group)
        group_city = (location or {}).get("city", "")
        venue_name = (location or {}).get("name") or group_city or city

        events.append(
            Event(
                artist=getattr(product_group, "name", "Unbekannter Act"),
                date=str(getattr(product_group, "start_date", "")),
                venue=venue_name,
                city=city,
                source="eventim",
                url=getattr(product_group, "link", None),
                image_url=getattr(product_group, "image_url", None),
            )
        )

    print(f"[DEBUG eventim] {total_seen} Treffer für Suchbegriff '{city}'.", file=sys.stderr)
    return events


def _extract_location(product_group) -> dict | None:
    products = getattr(product_group, "products", None) or []
    for product in products:
        type_attrs = getattr(product, "type_attributes", None) or {}
        live_ent = type_attrs.get("liveEntertainment") if isinstance(type_attrs, dict) else None
        if live_ent and "location" in live_ent:
            return live_ent["location"]
    return None
