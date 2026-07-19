# Waldgeflüster Events — statischer Website-Klon

1:1-Kopie von [waldgefluester-events.de](https://waldgefluester-events.de/) (WordPress/Enfold) als statische Website, gehostet über GitHub Pages.

## Wie dieser Klon entstanden ist

- Komplett-Mirror der gerenderten WordPress-Seite (`wget --mirror --convert-links`), alle Links relativ
- Alle `srcset`-Bildvarianten, LayerSlider-Skins und die krpano-Panotour (5.400+ Kacheln) nachgeladen — die Seite ist vollständig eigenständig, kein Asset lädt mehr vom Original-Server
- WordPress-Reste (wp-json, Feeds, xmlrpc, Shortlinks) entfernt

## Statische Anpassungen gegenüber dem Original

- **Kontaktformular:** WordPress/AJAX funktioniert statisch nicht. Beim Klick auf „Senden" öffnet sich stattdessen das E-Mail-Programm mit vorausgefüllter Anfrage an `anfrage@waldgefluester-events.de` (Interceptor-Script am Ende jeder Seite).
- **Canonical/OG-Meta-Tags** zeigen weiterhin auf waldgefluester-events.de (verhindert Duplicate-Content in Suchmaschinen).
- Google Tag Manager / Analytics laden wie im Original extern.

## Seiten

`/` · `/heiraten-schwaebische-alb/` · `/feiern/` · `/trauerfeier/` · `/winter/` · `/eigene-events/` · `/location-schwaebische-alb/` · `/bilder/` · `/faq/` · `/rechtliches/` · `/freie-hochzeitstermine/` · `/panotour/` (virtuelle 3D-Tour)

Die drei neuen Seiten (Feiern, Trauercafé, Events — passend zu den Flyer-QR-Codes) sind Klone des Enfold-Markups; ihre Bild- und Farb-Anpassungen liegen zentral in `assets/css/pages.css`.

## Termine pflegen (`events.json`)

Termine für die Events-Seite und den Startseiten-Banner stehen in **`events.json`** im Repo-Root — einfach neue Einträge ins `events`-Array (Format siehe `_anleitung`/`_beispiel` in der Datei), committen, fertig. Vergangene Termine werden automatisch ausgeblendet; ist kein Termin vorhanden, verschwindet der Banner auf der Startseite von selbst.

## Lokal ansehen

```sh
python3 -m http.server 8765
# → http://localhost:8765/
```

## Aktualisieren

Bei Änderungen an der WordPress-Original-Seite den Mirror-Prozess wiederholen (siehe oben) und die Dateien hier ersetzen.
