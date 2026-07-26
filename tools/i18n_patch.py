#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Einmaliger i18n-Umbau der geteilten Partials (Header, Footer, Kontakt):
deutsche UI-Strings werden mit dem t-Filter umhüllt ({{ "…" | t | safe }}),
interne Seitenlinks von {{ pre }} auf {{ base }} umgestellt (EN-Präfix) und
der Sprachumschalter in den Header eingesetzt. Die exakten Byte-Fassungen
längerer Texte werden aus den Dateien gelesen und als Schlüssel in
src/_data/translations.json übernommen."""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)

with open(P('src', '_data', 'translations.json'), encoding='utf-8') as f:
    tmap = json.load(f)
tmap.pop('', None)

def wrap_dq(s):   # Textknoten-Kontext -> doppelt gequotete njk-Strings
    assert '"' not in s, s
    return '{{ "' + s + '" | t | safe }}'

def wrap_sq(s):   # Attribut-Kontext -> einfach gequotete njk-Strings
    assert "'" not in s, s
    return "{{ '" + s + "' | t | safe }}"

changed = {}

def sub_all(txt, old, new, expect=None, fname=''):
    n = txt.count(old)
    assert n > 0, f'{fname}: nicht gefunden: {old[:70]}'
    if expect is not None:
        assert n == expect, f'{fname}: {old[:50]} erwartet {expect}, gefunden {n}'
    return txt.replace(old, new)

# --------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------
h = open(P('src/_includes/partials/header.njk'), encoding='utf-8').read()

def wrap_menu_label(m):
    label = m.group(2)
    return m.group(1) + wrap_dq(label) + m.group(3)
h, n = re.subn(r'(<span class="avia-menu-text">)([^<{]+)(</span>)', wrap_menu_label, h)
assert n >= 30, n

h = sub_all(h, "data-selectname='Wähle eine Seite'",
            "data-selectname='" + wrap_dq('Wähle eine Seite') + "'", 2, 'header')
h = sub_all(h, 'aria-label="Menü öffnen"',
            'aria-label="' + wrap_sq('Menü öffnen') + '"', 1, 'header')
h = sub_all(h, '<span class="avia_hidden_link_text">Menü</span>',
            '<span class="avia_hidden_link_text">' + wrap_dq('Menü') + '</span>', 1, 'header')

for page in ['index.html', 'heiraten-schwaebische-alb/', 'feiern/', 'trauerfeier/',
             'winter/', 'eigene-events/', 'location-schwaebische-alb/', 'bilder/',
             'faq/', 'freie-hochzeitstermine/']:
    old = '{{ pre }}' + page
    if old in h:
        h = h.replace(old, '{{ base }}' + page)

# Sprachumschalter: direkt vor der Hauptnavigation (nur erste nav).
SWITCH = ("<div class='wg-lang-switch' aria-label='" + wrap_sq('Sprache wechseln') + "'>"
          "<a href='{{ langAltUrl }}' hreflang=\"{{ 'de' if locale == 'en' else 'en' }}\" "
          "lang=\"{{ 'de' if locale == 'en' else 'en' }}\">{{ 'DE' if locale == 'en' else 'EN' }}</a></div>")
marker = "<nav class='main_menu'"
idx = h.find(marker)
assert idx > 0
h = h[:idx] + SWITCH + h[idx:]

open(P('src/_includes/partials/header.njk'), 'w', encoding='utf-8').write(h)
print('header.njk gepatcht')

# --------------------------------------------------------------------------
# Kontakt-Formular
# --------------------------------------------------------------------------
k = open(P('src/_includes/partials/kontakt.njk'), encoding='utf-8').read()

text_wraps = [  # (Literal im Textknoten-Kontext, erwartete Anzahl)
    ('<p class="wg-eyebrow">Euer nächster Schritt</p>', 1),
    ('>Ein paar Eckdaten genügen.<', 1),
    ('>Erzählt uns kurz, was ihr plant. Wir melden uns persönlich und schauen gemeinsam, was zu euch passt.<', 1),
    ('>Direkt per E-Mail<', 1),
    ('>Lieber persönlich?<', 1),
    ('>Bitte auswählen<', 1),
    ('>Hochzeit<', 1),
    ('>Geburtstag oder private Feier<', 1),
    ('>Firmen- oder Weihnachtsfeier<', 1),
    ('>Trauerfeier<', 1),
    ('>Eigenes Event oder Kooperation<', 1),
    ('>Sonstiges<', 1),
    ('>Eine ungefähre Zahl reicht.<', 1),
    ('>Vierstellige Jahreszahl.<', 1),
    ('>Ein paar Sätze helfen uns bei der ersten Einschätzung.<', 1),
    ('>Wir verwenden eure Angaben ausschließlich, um eure Anfrage persönlich zu beantworten.<', 1),
]
for lit, cnt in text_wraps:
    inner = lit[lit.find('>') + 1:lit.rfind('<')] if lit.startswith('>') else None
    if inner is None:  # eyebrow-Sonderfall
        inner = 'Euer nächster Schritt'
        k = sub_all(k, lit, lit.replace(inner, wrap_dq(inner)), cnt, 'kontakt')
    else:
        k = sub_all(k, lit, '>' + wrap_dq(inner) + '<', cnt, 'kontakt')

label_wraps = [
    ('<label for="wg-name">Name ', 'Name'),
    ('<label for="wg-email">E-Mail ', 'E-Mail'),
    ('<label for="wg-phone">Telefonnummer ', 'Telefonnummer'),
    ('<label for="wg-event">Was plant ihr? ', 'Was plant ihr?'),
    ('<label for="wg-guests">Personenanzahl ', 'Personenanzahl'),
    ('<label for="wg-year">Wunschjahr ', 'Wunschjahr'),
    ('<label for="wg-message">Was dürfen wir schon wissen? ', 'Was dürfen wir schon wissen?'),
]
for lit, word in label_wraps:
    k = sub_all(k, lit, lit.replace(word + ' ', wrap_dq(word) + ' '), 1, 'kontakt')

k = sub_all(k, '<span class="wg-optional">optional</span>',
            '<span class="wg-optional">' + wrap_dq('optional') + '</span>', 1, 'kontakt')
k = sub_all(k, 'aria-label="Direkte Kontaktmöglichkeiten"',
            'aria-label="' + wrap_sq('Direkte Kontaktmöglichkeiten') + '"', 1, 'kontakt')
k = sub_all(k, 'placeholder="z. B. 2027"', 'placeholder="' + wrap_sq('z. B. 2027') + '"', 1, 'kontakt')
k = sub_all(k, 'placeholder="Terminwunsch, Anlass und alles, was euch wichtig ist …"',
            'placeholder="' + wrap_sq('Terminwunsch, Anlass und alles, was euch wichtig ist …') + '"', 1, 'kontakt')
k = sub_all(k, '<span>Ich habe die <a href="{{ pre }}rechtliches/">Datenschutzhinweise</a> gelesen und bin mit der Verarbeitung meiner Angaben zur Bearbeitung der Anfrage einverstanden.',
            '<span>' + wrap_dq('Ich habe die') + ' <a href="{{ pre }}rechtliches/">' + wrap_dq('Datenschutzhinweise') + '</a> ' + wrap_dq('gelesen und bin mit der Verarbeitung meiner Angaben zur Bearbeitung der Anfrage einverstanden.'), 1, 'kontakt')
k = sub_all(k, 'data-default-label="Anfrage senden"', 'data-default-label="' + wrap_sq('Anfrage senden') + '"', 1, 'kontakt')
k = sub_all(k, '<span>Anfrage senden</span>', '<span>' + wrap_dq('Anfrage senden') + '</span>', 1, 'kontakt')

open(P('src/_includes/partials/kontakt.njk'), 'w', encoding='utf-8').write(k)
print('kontakt.njk gepatcht')

# --------------------------------------------------------------------------
# Footer (inkl. Cookie-Banner und -Modal)
# --------------------------------------------------------------------------
f = open(P('src/_includes/partials/footer.njk'), encoding='utf-8').read()

# Kurze, exakt bekannte Textknoten
for lit in ['Adresse', 'Kontakt', 'Impressum', 'Datenschutz', 'Nach oben scrollen',
            'Eure Privatsphäre. Eure Entscheidung.', 'Akzeptieren', 'Nur ausblenden',
            'Einstellungen', 'Cookie- und Datenschutzeinstellungen',
            'Wie wir Cookies verwenden', 'Notwendige Website Cookies',
            'Google Analytics Cookies', 'Andere externe Dienste',
            'Google Webfont Einstellungen:', 'Google Maps Einstellungen:',
            'Google reCaptcha Einstellungen:', 'Vimeo und YouTube Einstellungen:',
            'Andere Cookies', 'Datenschutzrichtlinie', 'Impressum &#038; Datenschutz']:
    old = '>' + lit + '<'
    n = f.count(old)
    assert n >= 1, f'footer: {lit}'
    f = f.replace(old, '>' + wrap_dq(lit) + '<')

# Längere Textknoten per Präfix aus der Datei lesen (Byte-genaue Schlüssel)
prefix_texts = [
    'Diese Website verwendet Cookies. Mit',
    'Wir können Cookies anfordern',
    'Klicken Sie auf die verschiedenen Kategorienüberschriften',
    'Diese Cookies sind unbedingt erforderlich',
    'Da diese Cookies für die auf unserer Webseite',
    'Wir respektieren es voll und ganz',
    'Wir stellen Ihnen eine Liste der von Ihrem Computer',
    'Aktivieren, damit die Nachrichtenleiste',
    'Hier klicken, um notwendige Cookies',
    'Diese Cookies sammeln Informationen',
    'Wenn Sie nicht wollen, dass wir Ihren Besuch',
    'Hier klicken, um Google Analytics zu',
    'Wir nutzen auch verschiedene externe Dienste',
    'Hier klicken, um Google Webfonts',
    'Hier klicken, um Google Maps',
    'Hier klicken, um Google reCaptcha',
    'Hier klicken, um Videoeinbettungen',
    'Die folgenden Cookies werden ebenfalls gebraucht',
    'Hier klicken, um _ga - Google',
    'Hier klicken, um _gid - Google',
    'Hier klicken, um _gat_* - Google',
    'Sie können unsere Cookies und Datenschutzeinstellungen',
]
for prefix in prefix_texts:
    m = re.search('>(\\s*)(' + re.escape(prefix) + '[^<]*?)(\\s*)<', f)
    assert m, f'footer: Präfix nicht gefunden: {prefix}'
    full = m.group(2)
    # exakten Dateitext als Schlüssel verwenden; EN-Wert über Präfix zuordnen
    en = None
    for key, val in list(tmap.items()):
        if key.startswith(prefix):
            en = val
            if key != full:
                del tmap[key]
            break
    assert en, f'Übersetzung fehlt für Präfix: {prefix}'
    tmap[full] = en
    f = f.replace('>' + m.group(1) + full + m.group(3) + '<',
                  '>' + m.group(1) + wrap_dq(full) + m.group(3) + '<')

# Attribut-Titel der Cookie-Buttons
for attr in ['Cookies erlauben – die Auswahl könnt ihr jederzeit in den Einstellungen anpassen',
             'Cookies erlauben – die Auswahl könnt ihr jederzeit anpassen',
             'Keine Cookies erlauben – einzelne Funktionen stehen dann evtl. nicht zur Verfügung.',
             'Mehr über Cookies erfahren und auswählen, welche ihr zulassen möchtet.']:
    old = 'title="' + attr + '"'
    n = f.count(old)
    assert n >= 1, f'footer attr: {attr[:40]}'
    f = f.replace(old, 'title="' + wrap_sq(attr) + '"')
for attr, ctx in [('Nach oben scrollen', "title='Nach oben scrollen'"),
                  ('Link zu Instagram', None),
                  ('Waldgeflüster Footer Logo', None)]:
    for q in ['"', "'"]:
        old = 'title=' + q + attr + q
        if old in f: f = f.replace(old, 'title=' + q + wrap_sq(attr) + q)
        old = 'aria-label=' + q + attr + q
        if old in f: f = f.replace(old, 'aria-label=' + q + wrap_sq(attr) + q)
        old = 'alt=' + q + attr + q
        if old in f: f = f.replace(old, 'alt=' + q + wrap_sq(attr) + q)

# Per-Seite-Fußschnipsel lokalisieren
f = sub_all(f, "{% rawfile 'src/snippets/' + slug + '-foot.html' %}",
            "{% rawfile snip + slug + '-foot.html' %}", 1, 'footer')

open(P('src/_includes/partials/footer.njk'), 'w', encoding='utf-8').write(f)
print('footer.njk gepatcht')

with open(P('src', '_data', 'translations.json'), 'w', encoding='utf-8') as fh:
    json.dump(tmap, fh, ensure_ascii=False, indent=2)
print('translations.json aktualisiert:', len(tmap), 'Einträge')
