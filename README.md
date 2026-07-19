# Waldgeflüster Events — statische Website

Statische Website von [waldgefluester-events.de](https://waldgefluester-events.de/) (ursprünglich WordPress/Enfold-Mirror), gehostet über GitHub Pages, gebaut mit **Eleventy**.

## ⚠️ Wichtig: HTML-Dateien sind Build-Output

Die `index.html`-Dateien im Root und in den Seitenordnern werden aus **`src/`** generiert — **niemals direkt editieren!** Stattdessen:

```sh
# Quellen ändern in src/ (Layout, Partials, Snippets), dann:
npm install        # einmalig
npm run build      # generiert die HTML-Dateien in den Repo-Root
```

Struktur:
- `src/_includes/layout.njk` — Dokument-Gerüst (Head, Consent, Meta)
- `src/_includes/partials/` — **geteilte Komponenten**: `header.njk` (Logo + Navigation, einmal für alle Seiten), `kontakt.njk` (Formular), `footer.njk` (Footer, Cookie-Banner, Scripts)
- `src/snippets/<seite>-{seo,head,body,foot,post}.html` — seitenspezifische Inhalte
- `src/pages/<seite>.njk` — Seiten-Definitionen (Frontmatter: Titel-Slot, Nav-Active, Logo-Variante, Pfad-Präfix)

Navigation, Formular, Cookie-Banner oder Footer ändern = **eine Datei** in `partials/` anfassen, `npm run build`, fertig.

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
