"""Verschickt Push-Benachrichtigungen für neue Konzerte über ntfy.sh.

ntfy.sh braucht keinen Account: App installieren (iOS/Android), Topic
abonnieren, fertig. Doku: https://docs.ntfy.sh/
"""

from __future__ import annotations

import os
import sys
import time

import requests

from sources.base import Event


def send_new_event_notifications(events: list[Event]) -> None:
    topic = os.environ.get("NTFY_TOPIC")
    if not topic:
        raise RuntimeError("NTFY_TOPIC ist nicht gesetzt (env var fehlt).")

    for i, event in enumerate(events):
        try:
            _send_one(topic, event)
        except Exception as exc:  # noqa: BLE001 -- ein fehlgeschlagener Push darf den Rest nicht killen
            print(f"[WARN] Push fehlgeschlagen für '{event.artist}': {exc}", file=sys.stderr)

        # Kleine Pause, um ntfy.sh's Ratenlimit nicht zu triggern (v.a. beim ersten Lauf
        # mit vielen neuen Events auf einmal).
        if i < len(events) - 1:
            time.sleep(1.5)


def _send_one(topic: str, event: Event) -> None:
    date_display = event.date[:10] if event.date else "Datum unbekannt"
    body = f"{event.artist} – {date_display}, {event.venue}"

    headers = {
        "Title": "Neues Konzert in Koeln!",
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
