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

`/` · `/heiraten-schwaebische-alb/` · `/location-schwaebische-alb/` · `/winter/` · `/bilder/` · `/faq/` · `/rechtliches/` · `/freie-hochzeitstermine/` · `/panotour/` (virtuelle 3D-Tour)

## Lokal ansehen

```sh
python3 -m http.server 8765
# → http://localhost:8765/
```

## Aktualisieren

Bei Änderungen an der WordPress-Original-Seite den Mirror-Prozess wiederholen (siehe oben) und die Dateien hier ersetzen.
