"""Gemeinsames Datenmodell für alle Konzert-Quellen (Ticketmaster, Eventim, Venues)."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field


@dataclass
class Event:
    artist: str
    date: str  # ISO 8601, z.B. "2027-03-12" oder "2027-03-12T20:00:00"
    venue: str
    city: str
    source: str  # "ticketmaster" | "eventim" | "venue:palladium" | ...
    url: str | None = None
    id: str = field(default="", init=False)

    def __post_init__(self) -> None:
        # Stabile ID aus Artist + Datum + Venue, für Dedupe/Vergleich über Quellen hinweg.
        key = f"{self.artist.strip().lower()}|{self.date[:10]}|{self.venue.strip().lower()}"
        self.id = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "artist": self.artist,
            "date": self.date,
            "venue": self.venue,
            "city": self.city,
            "source": self.source,
            "url": self.url,
        }
