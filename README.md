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
- `src/_includes/partials/` — **geteilte Rahmen-Komponenten**: `header.njk` (Logo + Navigation, einmal für alle Seiten), `kontakt.njk` (Formular), `footer.njk` (Footer, Cookie-Banner, Scripts)
- `src/_includes/components.njk` — **geteilte Inhalts-Bausteine** als Nunjucks-Makros: `hero` (Vollbild-Einstieg mit H1 + Kontakt-Button), `intro` (Einleitungsabsatz), `zigzag` (Bild/Text-Reihe mit Pfeil), `sectionQuote` (Sektion mit Zitat-Überschrift), `iconList` („Warum Waldgeflüster“-Liste), `planTimeline` (Ablauf-Schritte), `ctaButton`, `contactBridge` („Euer nächster Schritt“ vor dem Formular)
- `src/_includes/bodies/<seite>.njk` — Seiteninhalte; rufen die Makros mit den seitenspezifischen (SEO-)Texten auf. `wedding-core.njk` ist der gemeinsame Kern von `/heiraten-schwaebische-alb/` und `/freie-hochzeitstermine/` (Unterschiede — eigene H1, Terminliste — steuert die Front Matter in `src/pages/`)
- `src/snippets/<seite>-{seo,head,foot,post}.html` — restliche seitenspezifische Roh-Blöcke (Meta, Per-Page-CSS, Skripte)
- `src/pages/<seite>.njk` — Seiten-Definitionen (Frontmatter: Titel-Slot, Nav-Active, Logo-Variante, Pfad-Präfix, Theme)
- `tools/componentize.py` — dokumentiert, wie die Makros/Bodies einmalig aus dem Enfold-Export extrahiert wurden (nicht erneut ausführbar, die Quell-Snippets sind entfernt)

Navigation, Formular, Cookie-Banner oder Footer ändern = **eine Datei** in `partials/` anfassen; wiederkehrende Inhaltsblöcke (Hero, CTAs, Abläufe …) = Makro in `components.njk`; Texte einer Seite = `bodies/<seite>.njk`. Danach `npm run build`, fertig.

## Zweisprachigkeit (DE/EN)

Deutsch liegt unter `/`, Englisch unter `/en/…` (gleiche Pfade). Umsetzung:

- **Geteilte UI-Strings** (Navigation, Formular, Cookie-Banner, Footer): der deutsche Text steht lesbar im Template und läuft durch den Nunjucks-Filter `t` (`{{ "Heiraten" | t | safe }}`). Die Übersetzungen stehen in `src/_data/translations.json` (DE-Text → EN-Text); fehlt ein Eintrag, bleibt der deutsche Text sichtbar. Neue UI-Strings: Filter dranhängen + Eintrag ergänzen.
- **Seiteninhalte**: `src/_includes/bodies/en/<seite>.njk` sind übersetzte Schwestern der deutschen Bodies (gleiche Struktur/Makros, englische Texte). SEO-Meta: `src/snippets/en/<seite>-seo.html`. Übrige Snippets in `src/snippets/en/` sind pfadangepasste Kopien (EN-Seiten liegen eine Ebene tiefer).
- **Seiten-Definitionen**: `src/pages/en/<seite>.njk` (permalink `en/…`, `locale: "en"`, `lang="en"`). `layout.njk` setzt daraus `base` (interne Links bleiben unter `/en/`), wählt Bodies/Snippets der Sprache und rendert die hreflang-Alternates (x-default = DE).
- **Sprachumschalter**: Pille im Header (`.wg-lang-switch`), verlinkt auf die Schwesterseite.
- **JS**: `assets/js/site.js` und `events.js` lesen `<html lang>` für Formular-/Terminlisten-Texte.
- **Bewusst deutsch**: Rezensionen der Paare (echte Kundenstimmen), `/rechtliches/` (Impressum/Datenschutz, aus EN-Seiten verlinkt als "German"), Markenslogan "IHR, WIR, PASST!".

## Wie dieser Klon entstanden ist

- Komplett-Mirror der gerenderten WordPress-Seite (`wget --mirror --convert-links`), alle Links relativ
- Alle `srcset`-Bildvarianten, LayerSlider-Skins und die krpano-Panotour (5.400+ Kacheln) nachgeladen — die Seite ist vollständig eigenständig, kein Asset lädt mehr vom Original-Server
- WordPress-Reste (wp-json, Feeds, xmlrpc, Shortlinks) entfernt

## Statische Anpassungen gegenüber dem Original

- **Kontaktformular:** Das Formular ist optisch und technisch für einen späteren HTTP-Endpunkt vorbereitet (`data-endpoint` bzw. `window.WG_CONTACT_ENDPOINT`). Solange kein Endpunkt gesetzt ist, wird nichts versendet und insbesondere kein E-Mail-Programm geöffnet. Die separat angezeigte E-Mail-Adresse bleibt als direkter Kontaktweg anklickbar.
- **Canonical/OG-Meta-Tags** zeigen weiterhin auf waldgefluester-events.de (verhindert Duplicate-Content in Suchmaschinen).
- Google Tag Manager / Analytics laden wie im Original extern.

## Seiten

`/` · `/heiraten-schwaebische-alb/` · `/feiern/` · `/trauerfeier/` · `/winter/` · `/eigene-events/` · `/location-schwaebische-alb/` · `/bilder/` · `/faq/` · `/rechtliches/` · `/freie-hochzeitstermine/` · `/panotour/` (virtuelle 3D-Tour)

Die drei neuen Seiten (Feiern, Trauercafé, Events — passend zu den Flyer-QR-Codes) sind Klone des Enfold-Markups; ihre Bild- und Farb-Anpassungen liegen zentral in `assets/css/pages.css`.


## Performance-Architektur

- **CSS-Bundle**: Die 45 Theme-Stylesheets sind zu `assets/css/bundle.css` gebündelt (url()-Pfade umgeschrieben). `assets/css/pages.css` bleibt bewusst **separat** verlinkt — das ist die Schicht für eigene Anpassungen (direkt editierbar, kein Rebuild nötig). Theme-CSS geändert? `python3 tools/css_bundle.py` neu laufen lassen.
- **Responsive Heroes**: Mobile Geräte laden kleine Hero-Varianten (Regeln am Ende von pages.css), Preloads pro Seite im Frontmatter (`heroLarge`/`heroSmall`).
- **Service Worker** (`sw.js`): network-first für HTML/events.json, stale-while-revalidate für statische Assets.
- **Bilder**: Alle Uploads sind komprimiert (340 MB → 111 MB). Neue Fotos vor dem Einchecken auf ~q75 komprimieren (`cwebp`/`sips`).

## Termine pflegen (`events.json`)

Termine für die Events-Seite und den Startseiten-Banner stehen in **`events.json`** im Repo-Root — einfach neue Einträge ins `events`-Array (Format siehe `_anleitung`/`_beispiel` in der Datei), committen, fertig. Vergangene Termine werden automatisch ausgeblendet; ist kein Termin vorhanden, verschwindet der Banner auf der Startseite von selbst.

## Lokal ansehen

```sh
python3 -m http.server 8765
# → http://localhost:8765/
```

## Aktualisieren

Bei Änderungen an der WordPress-Original-Seite den Mirror-Prozess wiederholen (siehe oben) und die Dateien hier ersetzen.
