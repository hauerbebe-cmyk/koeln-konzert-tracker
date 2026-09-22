"""Fragt die offizielle Ticketmaster Discovery API nach Musik-Events in Köln ab.

Doku: https://developer.ticketmaster.com/products-and-docs/apis/discovery-api/v2/
"""

from __future__ import annotations

import os

import requests

from .base import Event

API_URL = "https://app.ticketmaster.com/discovery/v2/events.json"


def fetch(city: str = "Cologne") -> list[Event]:
    api_key = os.environ.get("TICKETMASTER_API_KEY")
    if not api_key:
        raise RuntimeError("TICKETMASTER_API_KEY ist nicht gesetzt (env var fehlt).")

    events: list[Event] = []
    page = 0

    while True:
        params = {
            "apikey": api_key,
            "city": city,
            "countryCode": "DE",
            "classificationName": "Music",
            "size": 200,
            "page": page,
        }
        resp = requests.get(API_URL, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()

        page_events = data.get("_embedded", {}).get("events", [])
        for raw in page_events:
            events.append(_parse_event(raw, city))

        page_info = data.get("page", {})
        if page >= page_info.get("totalPages", 1) - 1:
            break
        page += 1

    return events


def _parse_event(raw: dict, fallback_city: str) -> Event:
    artist = raw.get("name", "Unbekannter Act")

    date_info = raw.get("dates", {}).get("start", {})
    date = date_info.get("dateTime") or date_info.get("localDate") or ""

    venue_name = fallback_city
    venues = raw.get("_embedded", {}).get("venues", [])
    if venues:
        venue_name = venues[0].get("name", fallback_city)

    return Event(
        artist=artist,
        date=date,
        venue=venue_name,
        city=fallback_city,
        source="ticketmaster",
        url=raw.get("url"),
    )
