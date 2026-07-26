#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Erzeugt die englischen Neben-Assets:
  * src/snippets/en/<slug>-{head,post,foot}.html – Kopien der deutschen
    Snippets mit angepassten relativen Pfaden (EN-Seiten liegen eine Ebene
    tiefer unter /en/).
  * src/snippets/en/index-head-full.html – Startseiten-Head mit englischem
    SEO-Block (aus en/index-seo.html) und angepassten Pfaden.
  * src/_includes/bodies/en/{heiraten,termine}.njk – Stubs auf den EN-Kern.
  * sitemap.xml – um die /en/-URLs ergänzt.
  * Pfad-Bump der übersetzten EN-Bodies (…/wp-content → ../../wp-content).
Idempotent: bereits verarbeitete Dateien werden erkannt und übersprungen.
"""
import os, re, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)
ASSET_DIRS = ['wp-content', 'wp-includes', 'assets', 'panotour']
SLUGS = ['index', 'events', 'feiern', 'trauerfeier', 'winter', 'location',
         'faq', 'bilder', 'heiraten', 'termine']

def bump_depth1(txt):
    """Seiten unter /<dir>/ -> /en/<dir>/ : ../X -> ../../X"""
    for d in ASSET_DIRS:
        txt = txt.replace('../' + d + '/', '../../' + d + '/')
    return txt

def bump_root(txt):
    """Startseite / -> /en/ : X -> ../X (nur nach Quote, Klammer oder Komma-Leerzeichen in srcset)"""
    for d in ASSET_DIRS:
        for pre in ['"', "'", '(', ' ']:
            txt = txt.replace(pre + d + '/', pre + '../' + d + '/')
    txt = txt.replace('data-events-src="../events.json"', 'data-events-src="../events.json"')
    txt = txt.replace('data-events-src="events.json"', 'data-events-src="../events.json"')
    return txt

# 1. Snippet-Kopien -----------------------------------------------------------
for slug in SLUGS:
    for kind in ['head', 'post', 'foot']:
        src = P('src', 'snippets', f'{slug}-{kind}.html')
        dst = P('src', 'snippets', 'en', f'{slug}-{kind}.html')
        if not os.path.exists(src):
            continue
        if os.path.exists(dst):
            continue
        txt = open(src, encoding='utf-8').read()
        txt = bump_root(txt) if slug == 'index' else bump_depth1(txt)
        open(dst, 'w', encoding='utf-8').write(txt)
        print('snippet:', f'en/{slug}-{kind}.html')

# 2. index-head-full mit englischem SEO-Block --------------------------------
dst = P('src', 'snippets', 'en', 'index-head-full.html')
if not os.path.exists(dst):
    full = open(P('src', 'snippets', 'index-head-full.html'), encoding='utf-8').read()
    seo_en = open(P('src', 'snippets', 'en', 'index-seo.html'), encoding='utf-8').read()
    m = re.search(r'<!-- This site is optimized with the Yoast SEO plugin.*?<!-- / Yoast SEO plugin\. -->',
                  full, re.S)
    assert m, 'Yoast-Block nicht gefunden'
    full = full.replace(m.group(0), seo_en.strip())
    full = bump_root(full)
    open(dst, 'w', encoding='utf-8').write(full)
    print('snippet: en/index-head-full.html (SEO getauscht)')

# 3. Wedding-Stubs ------------------------------------------------------------
STUB = ('{# Heiraten & Freie Hochzeitstermine (EN) teilen denselben Seitenkern –\n'
        '   Unterschiede (H1, Terminliste) steuert die Front Matter. #}\n'
        '{% include "bodies/en/wedding-core.njk" %}\n')
for slug in ['heiraten', 'termine']:
    dst = P('src', '_includes', 'bodies', 'en', f'{slug}.njk')
    if not os.path.exists(dst):
        open(dst, 'w', encoding='utf-8').write(STUB)
        print('stub:', f'bodies/en/{slug}.njk')

# 4. Pfad-Bump der EN-Bodies --------------------------------------------------
bodies_dir = P('src', '_includes', 'bodies', 'en')
skip = set(sys.argv[1:])  # z. B. wedding-core.njk solange der Übersetzer läuft
for fn in sorted(os.listdir(bodies_dir)):
    if not fn.endswith('.njk') or fn in ('heiraten.njk', 'termine.njk') or fn in skip:
        continue
    path = os.path.join(bodies_dir, fn)
    txt = open(path, encoding='utf-8').read()
    if '../../wp-content/' in txt or (fn == 'index.njk' and '"../wp-content/' in txt):
        continue  # schon gebumpt
    new = bump_root(txt) if fn == 'index.njk' else bump_depth1(txt)
    if new != txt:
        open(path, 'w', encoding='utf-8').write(new)
        print('body-bump:', fn)

# 5. Sitemap ------------------------------------------------------------------
sm_path = P('sitemap.xml')
sm = open(sm_path, encoding='utf-8').read()
if '/en/' not in sm:
    today = '2026-07-26'
    en_urls = []
    for m in re.finditer(r'<loc>https://waldgefluester-events\.de/([a-z-]*/?)</loc>', sm):
        path = m.group(1)
        if path.startswith('rechtliches'):
            continue
        en_urls.append(f'  <url><loc>https://waldgefluester-events.de/en/{path}</loc><lastmod>{today}</lastmod></url>')
    sm = sm.replace('</urlset>', '\n'.join(en_urls) + '\n</urlset>')
    open(sm_path, 'w', encoding='utf-8').write(sm)
    print('sitemap.xml: +', len(en_urls), 'EN-URLs')
print('fertig')
