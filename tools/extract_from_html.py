#!/usr/bin/env python3
"""Zerlegt die 11 statischen Seiten in Eleventy-Layout + Partials + Snippets.
Referenzseite: feiern/index.html (neuester, sauberster Stand)."""
import os, re, json, hashlib

ROOT = "/Users/mastafied/waldgefluester_website"
SRC = os.path.join(ROOT, "src")
PAGES = {  # slug -> (datei, active-nav-slug, logo, permalink)
    "index":   ("index.html", "index", "standard", "index.html"),
    "heiraten": ("heiraten-schwaebische-alb/index.html", "heiraten-schwaebische-alb", "standard", "heiraten-schwaebische-alb/index.html"),
    "feiern":  ("feiern/index.html", "feiern", "standard", "feiern/index.html"),
    "trauerfeier": ("trauerfeier/index.html", "trauerfeier", "standard", "trauerfeier/index.html"),
    "winter":  ("winter/index.html", "winter", "winter", "winter/index.html"),
    "events":  ("eigene-events/index.html", "eigene-events", "standard", "eigene-events/index.html"),
    "location": ("location-schwaebische-alb/index.html", "location-schwaebische-alb", "standard", "location-schwaebische-alb/index.html"),
    "bilder":  ("bilder/index.html", "bilder", "standard", "bilder/index.html"),
    "faq":     ("faq/index.html", "faq", "standard", "faq/index.html"),
    "termine": ("freie-hochzeitstermine/index.html", "freie-hochzeitstermine", "standard", "freie-hochzeitstermine/index.html"),
    "rechtliches": ("rechtliches/index.html", "rechtliches", "standard", "rechtliches/index.html"),
}
REF = "feiern"

for d in ["_includes/partials", "snippets", "pages"]:
    os.makedirs(os.path.join(SRC, d), exist_ok=True)

import subprocess
def load(slug):
    # Quelle ist der letzte Git-Commit (Arbeitskopie ist ggf. schon Build-Output)
    return subprocess.run(["git", "-C", ROOT, "show", "HEAD:" + PAGES[slug][0]],
                          capture_output=True, text=True, check=True).stdout

def cut(s):
    """Zerlegt eine Seite in ihre Regionen."""
    r = {}
    r["html_tag"] = s[s.find("<html "):s.find(">", s.find("<html "))+1]
    hs, he = s.find("<head"), s.find("</head>")
    r["head"] = s[s.find(">", hs)+1:he]
    ys = r["head"].find("<!-- This site is optimized")
    ye = r["head"].find("<!-- / Yoast SEO plugin. -->") + len("<!-- / Yoast SEO plugin. -->")
    r["seo"] = r["head"][ys:ye]
    r["head_rest"] = r["head"][:ys] + "[[SEO]]" + r["head"][ye:]
    bs = s.find("<body ")
    r["body_tag"] = s[bs:s.find(">", bs)+1]
    h1 = s.find("<header "); h1e = s.find(">", h1)+1; h2 = s.find("</header>")
    r["body_to_header"] = s[s.find(">", bs)+1:h1]
    r["header_tag"] = s[h1:h1e]
    r["header_inner"] = s[h1e:h2]
    fp = s.find("<form action=")
    kg = s.rfind("<div id='av-layout-grid-", 0, fp)
    fe = s.find("</form>", fp)
    nb = s.find("<div id='", fe)
    ad = s.find(">Adresse<")
    fg = s.rfind("<div id='av-layout-grid-", 0, ad)
    r["content"] = s[h2+len("</header>"):kg]
    r["kontakt"] = s[kg:nb]
    r["content_post"] = s[nb:fg]
    r["footer"] = s[fg:s.find("</html>")+7]
    return r

ref = cut(load(REF))

# ---------- Layout bauen ----------
def pre_sub(t):
    return t.replace("../", "{{ pre }}")

# Head: Referenz-Head mit Slots. Per-Page-Extras werden am post-1987-Anker eingefügt.
head = ref["head_rest"]
head = head.replace("[[SEO]]", "{% rawfile 'src/snippets/' + slug + '-seo.html' %}")
anchor = "<link rel='stylesheet' id='wg-pages-css'"
assert anchor in head
head = head.replace(anchor, "{% rawfile 'src/snippets/' + slug + '-head.html' %}\n" + anchor, 1)
head = head.replace("header-reading-progress-5001", "header-reading-progress-{{ pid }}")
head = pre_sub(head)

# Header-Partial: Logo-Slot + Nav aus Referenz, Actives regeneriert
hdr = ref["header_inner"]
li = hdr.find("<span class='logo avia-svg-logo'>"); lj = hdr.find("<nav class='main_menu'")
logo_standard = pre_sub(hdr[li:lj])
w = cut(load("winter"))
wi = w["header_inner"]; wli = wi.find("<span class='logo avia-svg-logo'>"); wlj = wi.find("<nav class='main_menu'")
logo_winter = pre_sub(wi[wli:wlj])
nav = hdr[lj:]
# Active-Klassen der Referenzseite (feiern) entfernen, dann pro Item Slot einsetzen
nav = re.sub(r"\b(current-menu-item|current_page_item|current-menu-ancestor|current-menu-parent|current_page_parent|current_page_ancestor|page_item page-item-\d+) ?", "", nav)
NAV_SLUGS = {  # href -> (exakter slug, [zusaetzliche Kind-Slugs fuer Ancestor-Markierung])
    "index.html": ("index", []),
    "heiraten-schwaebische-alb/": ("heiraten-schwaebische-alb", ["freie-hochzeitstermine"]),
    "feiern/": ("feiern", []), "trauerfeier/": ("trauerfeier", []),
    "winter/": ("winter", []), "eigene-events/": ("eigene-events", []),
    "location-schwaebische-alb/": ("location-schwaebische-alb", ["faq"]),
    "bilder/": ("bilder", []),
}
def mark_active(m):
    tag = m.group(0)
    href = re.search(r'href="(?:\.\./)?([^"#]*)"', tag)
    entry = NAV_SLUGS.get(href.group(1) if href else "", None)
    if entry is None:
        return tag
    slugkey, kids = entry
    marker = "{%% if active == '%s' %%}current-menu-item current_page_item {%% endif %%}" % slugkey
    for k in kids:
        marker += "{%% if active == '%s' %%}current-menu-ancestor current-menu-parent {%% endif %%}" % k
    return tag.replace('class="menu-item ', 'class="menu-item ' + marker, 1)
# nur Top-Level-Items markieren (li mit menu-item-top-level ... bis zum oeffnenden <a>)
nav = re.sub(r"<li role=\"menuitem\" id=\"menu-item-\d+\" class=\"menu-item [^\"]*menu-item-top-level[^\"]*\"><a [^>]*>", mark_active, nav)
nav = pre_sub(nav)
header_partial = (ref["header_tag"] +
    "{% if logo == 'winter' %}" + hdr[:li] + logo_winter + "{% else %}" + hdr[:li] + logo_standard + "{% endif %}" +
    nav + "</header>")

# Kontakt-Partial: Referenzblock, H2/P als Variablen
kontakt_partial = pre_sub(ref["kontakt"])

# Footer-Partial: Referenzfooter, Cookie-Self-Links vereinheitlicht, Script-Slot vor mailto
foot = ref["footer"]
foot = foot.replace("href='../feiern/#'", "href='#'").replace('href="../feiern/#"', 'href="#"')
marker = "<script>\n/* Statischer Ersatz"
assert marker in foot
foot = foot.replace(marker, "{% rawfile 'src/snippets/' + slug + '-foot.html' %}\n" + marker, 1)
foot = foot.replace("header-reading-progress-5001", "header-reading-progress-{{ pid }}")
footer_partial = pre_sub(foot)

body_to_header = pre_sub(ref["body_to_header"])
layout = (
    "<!DOCTYPE html>\n{{ htmlTag | safe }}\n"
    "{% if fullHead %}<head>{% rawfile 'src/snippets/' + slug + '-head-full.html' %}</head>\n"
    "{% else %}<head>" + head + "</head>{% endif %}\n"
    "{{ bodyTag | safe }}\n" + body_to_header +
    "{% include 'partials/header.njk' %}\n"
    "{% rawfile 'src/snippets/' + slug + '-body.html' %}\n"
    "{% include 'partials/kontakt.njk' %}\n"
    "{% rawfile 'src/snippets/' + slug + '-post.html' %}\n"
    "{% if fullFooter %}{% rawfile 'src/snippets/' + slug + '-foot-full.html' %}\n"
    "{% else %}{% include 'partials/footer.njk' %}{% endif %}\n")

open(os.path.join(SRC, "_includes/layout.njk"), "w", encoding="utf-8").write(layout)
open(os.path.join(SRC, "_includes/partials/header.njk"), "w", encoding="utf-8").write(header_partial)
open(os.path.join(SRC, "_includes/partials/kontakt.njk"), "w", encoding="utf-8").write(kontakt_partial)
open(os.path.join(SRC, "_includes/partials/footer.njk"), "w", encoding="utf-8").write(footer_partial)

# ---------- Pro Seite: Snippets + Template ----------
ref_head_lines = set(l.strip().replace("../","") for l in ref["head_rest"].splitlines() if l.strip())
diag = []
for slug, (fpath, active, logo, permalink) in PAGES.items():
    r = cut(load(slug))
    pre = "" if slug == "index" else "../"
    # Head-Extras: Zeilen, die die Referenz nicht hat (Reihenfolge erhalten)
    page_lines = [l for l in r["head_rest"].splitlines() if l.strip()]
    extras = [l for l in page_lines if l.strip().replace("../","") not in ref_head_lines
              and "avia_posts_css/post-1987.css" not in l and l.strip().startswith("<")]
    # Kontakt-Texte extrahieren
    kh = kt = None
    # Footer-Extras: script-Zeilen, die die Referenz nicht hat
    ref_foot_lines = set(l.strip() for l in ref["footer"].splitlines() if l.strip())
    foot_extras = [l for l in r["footer"].splitlines()
                   if l.strip() and l.strip() not in ref_foot_lines and "<script" in l and "src=" in l]
    body = r["content"].replace("winter.html", "winter/")
    W = lambda name, txt: open(os.path.join(SRC, "snippets", f"{slug}-{name}.html"), "w", encoding="utf-8").write(txt)
    full = (slug == "index")
    if full:
        head_full = r["head"]
        if "post-1987.css" not in head_full:
            head_full = head_full.replace("<link rel='stylesheet' id='wg-pages-css'",
                "<link rel='stylesheet' id='avia-single-post-1987-css' href='wp-content/uploads/dynamic_avia/avia_posts_css/post-1987.css' media='all' />\n<link rel='stylesheet' id='wg-pages-css'", 1)
        W("head-full", head_full)
        W("foot-full", r["footer"])
    W("seo", r["seo"]); W("head", "\n".join(extras)); W("body", body); W("foot", "\n".join(foot_extras))
    W("post", r["content_post"])
    pid_m = re.search(r"page-id-(\d+)", r["body_tag"])
    fm = {
        "layout": "layout.njk", "permalink": permalink, "slug": slug, "pre": pre,
        "active": active, "logo": logo, "pid": pid_m.group(1) if pid_m else "0",
        "fullHead": full, "fullFooter": full,
        "htmlTag": r["html_tag"], "bodyTag": r["body_tag"],
        "kontaktHeading": kh.group(1) if kh else "", "kontaktText": kt.group(1) if kt else "",
    }
    open(os.path.join(SRC, "pages", f"{slug}.njk"), "w", encoding="utf-8").write(
        "---json\n" + json.dumps(fm, ensure_ascii=False, indent=1) + "\n---\n")
    diag.append(f"{slug}: head-extras={len(extras)} foot-extras={len(foot_extras)} kontaktH={'ja' if kh else 'NEIN'}")

# winter.html Redirect-Stub
open(os.path.join(SRC, "pages", "winter-redirect.njk"), "w", encoding="utf-8").write(
    '---json\n{"permalink": "winter.html", "layout": null, "eleventyExcludeFromCollections": true}\n---\n'
    '<!DOCTYPE html><html lang="de"><head><meta charset="utf-8">'
    '<meta http-equiv="refresh" content="0; url=winter/">'
    '<link rel="canonical" href="https://waldgefluester-events.de/winter/">'
    '<title>Winterevents – Waldgeflüster</title></head>'
    '<body><a href="winter/">Weiter zu den Winterevents …</a></body></html>\n')

print("\n".join(diag))
print("\nGerüst geschrieben nach src/")
EOF = None
