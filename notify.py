"""Verschickt Push-Benachrichtigungen für neue Konzerte über ntfy.sh.

ntfy.sh braucht keinen Account: App installieren (iOS/Android), Topic
abonnieren, fertig. Doku: https://docs.ntfy.sh/
"""

from __future__ import annotations

import os

import requests

from sources.base import Event


def send_new_event_notifications(events: list[Event]) -> None:
    topic = os.environ.get("NTFY_TOPIC")
    if not topic:
        raise RuntimeError("NTFY_TOPIC ist nicht gesetzt (env var fehlt).")

    for event in events:
        _send_one(topic, event)


def _send_one(topic: str, event: Event) -> None:
    date_display = event.date[:10] if event.date else "Datum unbekannt"
    body = f"{event.artist} – {date_display}, {event.venue}"

    headers = {
        "Title": "🎵 Neues Konzert in Köln!",
        "Tags": "musical_note",
    }
    if event.url:
        headers["Click"] = event.url

    resp = requests.post(
        f"https://ntfy.sh/{topic}",
        data=body.encode("utf-8"),
        headers=headers,
        timeout=10,
    )
    resp.raise_for_status()
