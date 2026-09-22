"""Einzelne Venue-Scraper. Jede Datei stellt eine fetch() -> list[Event] Funktion bereit.

Reihenfolge beim Hinzufügen einer neuen Venue:
1. Website im Browser öffnen, DevTools -> Netzwerk-Tab, nach Spielplan/Event-Liste
   filtern (z.B. "events", "json", "api").
2. Lädt die Seite ihre Termine über einen JSON-Endpoint nach? -> requests.get() darauf,
   siehe palladium.py als Beispiel.
3. Falls nicht: klassisches HTML-Scraping mit BeautifulSoup, siehe
   live_music_hall.py als Beispiel-Grundgerüst.
4. Neues Modul in main.py unter VENUE_MODULES eintragen.
"""
