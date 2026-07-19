#!/usr/bin/env python3
"""Bündelt die Theme-CSS-Dateien aus layout.njk zu einer Datei.
url()-Pfade werden beim Zusammenführen auf die Bundle-Position umgeschrieben."""
import os, re, posixpath

ROOT = "/Users/mastafied/waldgefluester_website"
LAYOUT = os.path.join(ROOT, "src/_includes/layout.njk")
BUNDLE_REL = "assets/css/bundle.css"
BUNDLE_DIR = "assets/css"

layout = open(LAYOUT, encoding="utf-8").read()

# Alle lokalen Stylesheet-Links im Layout-Head finden ({{ pre }}-präfixiert)
LINK_RE = re.compile(r"<link rel='stylesheet' id='([^']*)' href='\{\{ pre \}\}([^']+)' media='[^']*' />\n?")
links = LINK_RE.findall(layout)
print(f"{len(links)} Stylesheet-Links im Layout gefunden")

def rewrite_urls(css, src_rel):
    """url()-Referenzen von src_rel-Position auf BUNDLE_DIR-Position umschreiben."""
    src_dir = posixpath.dirname(src_rel)
    def fix(m):
        u = m.group(1).strip("'\"")
        if u.startswith(("data:", "http://", "https://", "//", "#")):
            return m.group(0)
        target = posixpath.normpath(posixpath.join(src_dir, u))
        rel = posixpath.relpath(target, BUNDLE_DIR)
        return f"url({rel})"
    return re.sub(r"url\(\s*([^)]+?)\s*\)", fix, css)

parts = []
skipped = []
for cid, href in links:
    path = os.path.join(ROOT, href)
    if not os.path.exists(path):
        skipped.append(href); continue
    css = open(path, encoding="utf-8", errors="replace").read()
    css = re.sub(r'@charset [^;]+;', '', css)
    css = rewrite_urls(css, href)
    parts.append(f"/* ===== {href} ===== */\n" + css)

os.makedirs(os.path.join(ROOT, BUNDLE_DIR), exist_ok=True)
bundle_path = os.path.join(ROOT, BUNDLE_REL)
open(bundle_path, "w", encoding="utf-8").write("\n".join(parts))
size = os.path.getsize(bundle_path)
print(f"Bundle: {BUNDLE_REL} = {size//1024} KB aus {len(parts)} Dateien; übersprungen: {skipped}")

# Layout: alle Links durch einen Bundle-Link ersetzen (an Position des ersten)
first = LINK_RE.search(layout)
bundle_link = f"<link rel='stylesheet' id='wg-bundle-css' href='{{{{ pre }}}}{BUNDLE_REL}' media='all' />\n"
layout = LINK_RE.sub("", layout)
# an der Stelle des früheren ersten Links einfügen: vor dem SEO-Slot? Besser: direkt nach </title>-Bereich –
# wir nehmen den Anker des rawfile-head-Slots (Extras laden NACH dem Bundle, z.B. post-NNN.css)
anchor = "{% rawfile 'src/snippets/' + slug + '-head.html' %}"
assert anchor in layout
layout = layout.replace(anchor, bundle_link + anchor, 1)
open(LAYOUT, "w", encoding="utf-8").write(layout)
print("layout.njk: Links ersetzt durch Bundle + Extras-Anker")
