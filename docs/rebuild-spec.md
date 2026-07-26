# Lean-Rebuild: Komponenten-Spezifikation

Der WordPress/Enfold-Unterbau ist entfernt. Seiten-Bodies (`src/_includes/bodies/*.njk`,
englisch in `bodies/en/`) bestehen aus **sauberem semantischem HTML** plus den
Nunjucks-Makros aus `src/_includes/components.njk`. Ein einziges Stylesheet
(`assets/css/site.css`) und ein Vanilla-JS (`assets/js/site.js`) treiben alles an.

**Referenz-Beispiele** (fertig migriert, daran orientieren):
`src/_includes/bodies/feiern.njk` und `src/_includes/bodies/winter.njk`.

## Layout-Kontrakt

- Das Layout rendert `<main id="main">` um den Body; der Body beginnt direkt
  mit seinem ersten `<section>` (kein `<div id='main'>`-Wrapper, kein
  Enfold-Markup, kein `footer-page`-Div).
- Kontaktformular + Footer kommen aus dem Layout — der Body endet üblicherweise
  mit `{{ contactBridge(...) }}`.
- Bild-/Asset-Pfade: relative Pfade aus den alten Bodies unverändert übernehmen
  (`../wp-content/...` auf DE-Unterseiten, `../../wp-content/...` auf EN-Seiten,
  `wp-content/...` auf der DE-Startseite, `../wp-content/...` auf der EN-Startseite).
- Vorhandene Anker-IDs (z. B. `#tour`, `#rezensionen`, `#anfahrt`, `#impressum`)
  MÜSSEN erhalten bleiben (Navigation/Untermenüs verlinken darauf).

## Makros (Import-Zeile ganz oben in jedem Body)

```njk
{% from "components.njk" import hero, intro, zigzag, sectionQuote, iconList, planTimeline, ctaButton, contactBridge, subnav, gallery with context %}
```

- `{{ hero(titleHtml, {}) }}` — Vollbild-Hero; Bild kommt automatisch aus der
  Front Matter (heroLarge/heroSmall). `{ button: false }` unterdrückt den Button.
- `{{ intro(textHtml) }}` — Einleitungskarte unter dem Hero.
- `{% call zigzag({ id: 'anker' }) %} <h2>…</h2> <p>…</p> {% endcall %}` —
  Bild/Text-Karte. Bild via `cellA/cellB`-Hash aus `src/_data/zigimages.json`;
  wenn kein Mapping existiert, stattdessen von Hand bauen:
  `<section class="wg-split"><div class="wg-split__media"><img …></div><div class="wg-split__body">…</div></section>`
- `{% call sectionQuote({ id: 'x', title: varOderString }) %} … {% endcall %}` —
  Sektion mit zentrierter Zitat-Überschrift auf Themenfläche.
- `{{ iconList([{ title: '…', text: '…' }, …]) }}` — Vorteils-Karten (3er-Grid).
- `{{ planTimeline([{ title: '…', text: '…' }, …]) }}` — nummerierte Schritte.
- `{{ ctaButton('Label', { href: '#kontakt' }) }}` — Pillen-Button, zentriert.
- `{{ contactBridge(headingVar, textVar) }}` — Abschluss vor dem Formular.
- `{{ subnav([{ href: '#a', label: 'A' }, …]) }}` — klebrige Sektions-Navigation.
- `{{ gallery([{ full: 'wp-content/…1030x687.webp', thumb: 'wp-content/…495x400.webp', alt: '…' }, …]) }}`
  — Bildraster mit Lightbox. Pfade OHNE ../-Präfix angeben (Makro setzt `pre` davor).

## CSS-Klassen für Freiform-Markup

- Sektionen: `<section class="wg-section" id="…"><div class="wg-container">…</div></section>`;
  `wg-band` zusätzlich für Themenfläche; `wg-container--narrow` für Lesespalten.
- Überschrift zentriert mit Akzentlinie: `<h2 class="wg-quote">…</h2>`;
  Unterzeile in Überschrift: `<span class="wg-sub">…</span>`.
- Zahlenband: `<div class="wg-counters"><div><strong data-count-to="2000">0</strong><span>m² Außenfläche</span></div>…</div>`
- Rezensionen: `<div class="wg-reviews"><blockquote><p>Zitat…</p><footer><strong>Name</strong> · Google</footer></blockquote>…</div>`
- Tabs: `<div class="wg-tabs"><ul class="wg-tabs__list" role="tablist"><li><button type="button">Tab</button></li>…</ul><div class="wg-tabs__panel">…</div>…</div>`
  (JS verdrahtet Auswahl/hidden automatisch; Reihenfolge Buttons = Reihenfolge Panels)
- FAQ: `<div class="wg-faq"><h2>Kategorie</h2><details><summary>Frage</summary><div><p>Antwort</p></div></details>…</div>`
- Karten/Iframes (Maps, 3D-Tour): `<div class="wg-embed"><iframe … loading="lazy" title="…"></iframe></div>`
- Bilderreihe horizontal scrollbar: `<div class="wg-carousel"><img …>…</div>`
- Buttons frei platziert: `<a class="btn" href>…</a>` (`btn--light` auf Fotos, `btn--outline` dezent).

## Regeln

1. **Alle sichtbaren Texte 1:1 übernehmen** (SEO!) — nichts kürzen, nichts umformulieren.
   `<span class='special_amp'>&amp;</span>`-Konstrukte zu schlichtem `&amp;` vereinfachen.
2. Enfold-Markup restlos entfernen: keine `av-*`/`avia-*`/`flex_*`-Klassen, keine
   Icon-Fonts (`data-av_icon`), keine `data-pm-slice`, keine Builder-Wrapper,
   keine Inline-`<style>`-Blöcke, kein `<div class='hr …'>`.
3. `loading="lazy" decoding="async"` auf alle Bilder außerhalb des Heros; alt-Texte übernehmen.
4. IDs/Anker erhalten; `aria-label` sinnvoll setzen; Überschriften-Hierarchie sauber (eine h1 pro Seite, aus dem Hero).
5. Für Bilder aus alten `srcset`-Angaben: die 1030er-Variante als `full`, die 495x400 als `thumb`.
