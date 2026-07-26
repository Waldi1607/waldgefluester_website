#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Einmaliger Umbau: extrahiert die wiederkehrenden Enfold-Blöcke aus den
statischen Body-Snippets und erzeugt daraus

  * src/_includes/components.njk    – Nunjucks-Makros (Hero, Intro, Zickzack,
                                      Zitat-Sektion, Iconliste, Timeline,
                                      CTA-Button, Kontaktbrücke)
  * src/_includes/bodies/<slug>.njk – Seiten-Templates, die die Makros mit den
                                      seitenspezifischen Texten aufrufen;
                                      nicht erkannte Bereiche bleiben 1:1 roh.

Die Makro-Vorlagen werden byte-genau aus den bestehenden Seiten gewonnen,
damit das gerenderte HTML (bis auf normalisierte Builder-Artefakte wie
avia-builder-el-Nummern) unverändert bleibt.
"""
import re, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNIP = os.path.join(ROOT, 'src', 'snippets')
INC = os.path.join(ROOT, 'src', '_includes')
BODIES = os.path.join(INC, 'bodies')
os.makedirs(BODIES, exist_ok=True)

def load(slug):
    with open(os.path.join(SNIP, f'{slug}-body.html'), encoding='utf-8') as f:
        return f.read()

ACTIVE = {  # Verzeichnisname je Seite (für Selbstlink-Normalisierung)
 'events':'eigene-events','feiern':'feiern','trauerfeier':'trauerfeier',
 'winter':'winter','location':'location-schwaebische-alb','faq':'faq',
 'rechtliches':'rechtliches','bilder':'bilder',
 'heiraten':'heiraten-schwaebische-alb','termine':'freie-hochzeitstermine',
 'index':'index'}

def normalize_self_links(txt, active):
    """../<eigene-seite>/#anker (und bei termine index.html#anker) -> #anker"""
    txt = txt.replace(f"../{active}/#", "#")
    if active == 'freie-hochzeitstermine':
        txt = txt.replace("index.html#", "#")
    return txt

# ---------------------------------------------------------------------------
# 1. Kanonische Blöcke extrahieren und Makros bauen
# ---------------------------------------------------------------------------
events = normalize_self_links(load('events'), ACTIVE['events'])

HERO_SPAN = re.compile(r"<div id='av_section_1'.*?<!-- close content main element --></div></div></div><div class='clear'></div>", re.S)
BRIDGE_SPAN = re.compile(r"<div id='av_section_5'.*$", re.S)

hero_canon = HERO_SPAN.search(events).group(0)
bridge_canon = BRIDGE_SPAN.search(events).group(0)

D = {  # Default-Hashes der Themen-Seiten (events/feiern/trauerfeier/winter)
 'heroSection': 'av-6zkywz-1b2215787bb2706e3468f3d409662512',
 'heroHeading': 'av-m69ft26d-b23ec56615f2dcfd0e46ad44c64ee571',
 'heroHr':      'av-3o69tv-e9b53f8b8463b69f910908b0f4ebe046',
 'heroButton':  'av-32jt4z-fa47c2014a4fed595434b26c1495dcce',
}

def slot(canon, needle, repl):
    assert needle in canon, f'Slot fehlt: {needle[:60]}'
    return canon.replace(needle, repl)

m = hero_canon
m = slot(m, D['heroSection'], "av-{{ o.section or '6zkywz-1b2215787bb2706e3468f3d409662512' }}")
m = slot(m, 'post-entry-5003', 'post-entry-{{ pid }}')
m = slot(m, D['heroHeading'], "av-{{ o.heading or 'm69ft26d-b23ec56615f2dcfd0e46ad44c64ee571' }}")
m = slot(m, 'Events &amp; Waldcafé im Waldgeflüster', '{{ title | safe }}')
m = slot(m, D['heroHr'], "av-{{ o.hr or '3o69tv-e9b53f8b8463b69f910908b0f4ebe046' }}")
m = slot(m, D['heroButton'], "av-{{ o.button or '32jt4z-fa47c2014a4fed595434b26c1495dcce' }}")
m = slot(m, 'Jetzt kontaktieren', "{{ (o.buttonLabel or 'Jetzt kontaktieren') | safe }}")
HERO_MACRO = "{% macro hero(title, o={}) %}\n" + m + "\n{% endmacro %}"

INTRO_PAT = re.compile(
    r"<div id='(after_[a-z_0-9]+)'  class='main_color av_default_container_wrap container_wrap fullsize'  >"
    r"<div class='container av-section-cont-open' ><div class='template-page content  av-content-full alpha units'>"
    r"<div class='post-entry post-entry-type-page post-entry-(\d+)'><div class='entry-content-wrapper clearfix'>\n"
    r"<section  class='av_textblock_section av-m65eyyfr-7b027bceb6ba7b4fef7fd10049d82d98 '   itemscope=\"itemscope\" itemtype=\"https://schema.org/CreativeWork\" >"
    r"<div class='avia_textblock av_inherit_color'  itemprop=\"text\" >(.*?)</div></section>\n"
    r"</div></div></div><!-- close content main div --></div></div>", re.S)
im = INTRO_PAT.search(events)
mi = im.group(0)
mi = slot(mi, f"<div id='{im.group(1)}'", "<div id='{{ o.wrapId or 'after_submenu_1' }}'")
mi = slot(mi, f"post-entry-{im.group(2)}", 'post-entry-{{ pid }}')
mi = slot(mi, im.group(3), '{{ text | safe }}')
INTRO_MACRO = "{% macro intro(text, o={}) %}\n" + mi + "\n{% endmacro %}"

ZIG_MACRO = """{% macro _zigarrow(hr, icon, dir, char) %}
<div  class='hr {{ hr }} hr-invisible  avia-builder-el-11  el_before_av_font_icon  avia-builder-el-first '><span class='hr-inner '><span class="hr-inner-style"></span></span></div>
<span  class='av_font_icon {{ icon }} avia_animate_when_visible av-icon-style- avia-icon-pos-left pfeil{{ dir }}'><span class='av-icon-char' aria-hidden='true' data-av_icon='{{ char }}' data-av_iconfont='entypo-fontello' ></span></span>
{% endmacro %}
{% macro zigzag(o) %}
<div id='{{ o.id }}'  class='av-layout-grid-container {{ o.row }} entry-content-wrapper main_color av-flex-cells av-break-at-tablet  avia-builder-el-6  el_after_av_textblock  el_before_av_layout_row  pfeilcontainer{{ ' av-grid-order-reverse' if o.reverse }} grid-row-not-first  container_wrap fullsize'  >
<div class='flex_cell {{ o.cellA }} av-gridrow-cell av_one_half no_margin  avia-builder-el-7  el_before_av_cell_one_half  avia-builder-el-first {{ o.cellAExtra }}'  ><div class='flex_cell_inner'>
{% if o.arrowFirst %}{{ _zigarrow(o.hr, o.icon, o.dir, o.char) }}{% else %}{{ caller() }}
{% endif %}</div></div><div class='flex_cell {{ o.cellB }} av-gridrow-cell av_one_half no_margin  avia-builder-el-10  el_after_av_cell_one_half  avia-builder-el-last {{ o.cellBExtra }}'  ><div class='flex_cell_inner'>
{% if o.arrowFirst %}{{ caller() }}
{% else %}{{ _zigarrow(o.hr, o.icon, o.dir, o.char) }}{% endif %}</div></div>
</div>
{% endmacro %}"""

SECQ_MACRO = """{% macro sectionQuote(o) %}
<div id='{{ o.id }}'  class='avia-section {{ o.section }} main_color avia-section-{{ o.size or 'default' }} avia-no-border-styling {{ o.extra }} avia-builder-el-41  el_after_av_layout_row  el_before_av_section  avia-bg-style-{{ o.bg or 'scroll' }} container_wrap fullsize'  ><div class='container av-section-cont-open' ><div class='template-page content  av-content-full alpha units'><div class='post-entry post-entry-type-page post-entry-{{ pid }}'><div class='entry-content-wrapper clearfix'>
<div  {% if o.headingId %}id="{{ o.headingId }}"  {% endif %}class='av-special-heading {{ o.heading }} av-special-heading-h2 {{ o.headingExtra if o.headingExtra != none else 'custom-color-heading ' }}blockquote modern-quote modern-centered  avia-builder-el-42  el_before_av_textblock  avia-builder-el-first '><h2 class='av-special-heading-tag '  itemprop="headline"  >{{ o.title | safe }}</h2><div class="special-heading-border"><div class="special-heading-inner-border"></div></div></div>
{{ caller() }}</div></div></div><!-- close content main div --></div></div>
{% endmacro %}"""

ICONLIST_MACRO = """{% macro iconList(items, o={}) %}
{% set h = o.hash or 'av-m69hag85-16f3508aa30779086d3593b88c73d5d1' %}
<div  class='avia-icon-list-container {{ h }}  avia-builder-el-43  el_after_av_heading  avia-builder-el-last '><ul class='avia-icon-list avia_animate_when_almost_visible avia-icon-list-left av-iconlist-big {{ h }} avia-iconlist-animate'>
{% for it in items %}<li><div class='iconlist_icon {{ it.icon }} avia-font-entypo-fontello'><span class='iconlist-char' aria-hidden='true' data-av_icon='{{ it.char }}' data-av_iconfont='entypo-fontello'></span></div><article class="article-icon-entry "  itemscope="itemscope" itemtype="https://schema.org/CreativeWork" ><div class="iconlist_content_wrap"><header class="entry-content-header" aria-label="Icon: {{ it.aria | safe }}"><h3 class='av_iconlist_title iconlist_title  '  itemprop="headline" >{{ it.title | safe }}</h3></header><div class='iconlist_content '  itemprop="text" ><p>{{ it.text | safe }}</p>
</div></div><footer class="entry-footer"></footer></article><div class="iconlist-timeline"></div></li>
{% endfor %}</ul></div>
{% endmacro %}"""

TIMELINE_MACRO = """{% macro planTimeline(steps, o={}) %}
<div  id="avia-timeline-1"  class='avia-timeline-container {{ o.hash or 'av-m69hmssv-4dc7ed467078201f44df3452dd9c12a4' }} av-slideshow-ui  avia-builder-el-46  el_after_av_heading  el_before_av_button  avia-slideshow-carousel' avia-data-slides='{{ steps | length }}'><ul class='avia-timeline avia-timeline-horizontal av-milestone-placement-top avia-timeline-boxshadow avia_animate_when_almost_visible avia-timeline-animate'>
{% for st in steps %}<li  class='av-milestone {{ st.hash }} av-animated-generic fade-in av-milestone-{{ 'odd' if loop.index % 2 else 'even' }}'><h2 class='av-milestone-date ' id='milestone-{{ loop.index }}' ><strong>{{ loop.index }}<span class='av-milestone-indicator'></span></strong></h2><div class="av-milestone-icon-wrap"><span class='av-milestone-icon milestone_icon avia-font-entypo-fontello'><span class='av-milestone-icon-inner milestone_inner'><i class='milestone-char' aria-hidden='true' data-av_icon='{{ st.char }}' data-av_iconfont='entypo-fontello'></i></span></span></div><article class='av-milestone-content-wrap'><div class='av-milestone-contentbox'><header class="entry-content-header" aria-label="Milestone: {{ st.aria | safe }}"><h4 class='av-milestone-title '>{{ st.title | safe }}</h4></header><div class='av-milestone-content'><p>{{ st.text | safe }}</p>
</div></div><footer class='av-milestone-article-footer entry-footer'></footer></article></li>
{% endfor %}</ul><div class='avia-slideshow-arrows avia-slideshow-controls av-timeline-nav ' ><a href='#prev' class='prev-slide prev-slide av-timeline-nav-prev av-nav-btn' aria-hidden='true' data-av_icon='' data-av_iconfont='entypo-fontello'  tabindex='-1'>Zurück</a><a href='#next' class='next-slide next-slide av-timeline-nav-next av-nav-btn' aria-hidden='true' data-av_icon='' data-av_iconfont='entypo-fontello'  tabindex='-1'>Weiter</a></div></div>
{% endmacro %}"""

CTA_MACRO = """{% macro ctaButton(label, o={}) %}
<div  class='avia-button-wrap {{ o.hash }}-wrap avia-button-{{ o.pos or 'center' }}  avia-builder-el-47  el_after_av_timeline  avia-builder-el-last {{ o.wrapExtra }}'><a href='{{ o.href or '#kontakt' }}'  class='avia-button {{ o.hash }} av-link-btn avia-icon_select-{{ 'yes-left-icon' if o.char else 'no' }} avia-size-large avia-position-{{ o.pos or 'center' }}{{ o.color }}'   aria-label="{{ label | safe }}">{% if o.char %}<span class='avia_button_icon avia_button_icon_left' aria-hidden='true' data-av_icon='{{ o.char }}' data-av_iconfont='entypo-fontello'></span>{% endif %}<span class='avia_iconbox_title' >{{ label | safe }}</span>{% if not o.char %}<span class='avia_button_background avia-button avia-color-theme-color-subtle' ></span>{% endif %}</a></div>
{% endmacro %}"""

bm = bridge_canon
bm = slot(bm, 'post-entry-5003', 'post-entry-{{ pid }}')
bm = slot(bm, 'Fragen zu unseren Events?', '{{ heading | safe }}')
bm = slot(bm, '<p>Schreibt uns über das Formular oder ruft uns an – wir helfen euch gerne weiter.</p>\n', '{{ text | safe }}')
BRIDGE_MACRO = "{% macro contactBridge(heading, text, o={}) %}\n" + bm + "\n{% endmacro %}"

COMPONENTS = """{#
  Wiederverwendbare Seitenbausteine (aus den Enfold-Exporten extrahiert).
  Alle Makros lesen `pid` aus dem Seitenkontext – daher mit
  `{% from "components.njk" import ... with context %}` einbinden.

  hero(title, o)           – Vollbild-Hero mit H1, Trennlinie, Kontakt-Button.
                             o.section/heading/hr/button: Style-Hashes der Seite
                             (ohne 'av-'-Präfix); Default = Themen-Seiten.
  intro(text, o)           – Einleitungsabsatz direkt unter dem Hero.
  zigzag(o) {% call %}     – Bild/Text-Reihe mit Pfeil. Inhalt (Überschrift +
                             Textblock) kommt aus dem call-Block; das Bild der
                             Bildzelle liefert das CSS über o.cellA/o.cellB.
  sectionQuote(o) {% call %} – Sektion mit zentrierter Zitat-Überschrift.
  iconList(items, o)       – "Warum Waldgeflüster"-Liste (Icon, Titel, Text).
  planTimeline(steps, o)   – Ablauf in nummerierten Schritten.
  ctaButton(label, o)      – Pillen-Button (mit/ohne Icon, Farbe variabel).
  contactBridge(h, t, o)   – Abschluss-Sektion "Euer nächster Schritt" vor dem
                             Kontaktformular (inkl. Seitenabschluss-Markup).
#}
""" + "\n\n".join([HERO_MACRO, INTRO_MACRO, ZIG_MACRO, SECQ_MACRO,
                   ICONLIST_MACRO, TIMELINE_MACRO, CTA_MACRO, BRIDGE_MACRO]) + "\n"

with open(os.path.join(INC, 'components.njk'), 'w', encoding='utf-8') as f:
    f.write(COMPONENTS)
print('components.njk geschrieben:', len(COMPONENTS), 'Bytes')

# ---------------------------------------------------------------------------
# 2. Parser: erkannte Blöcke -> Makro-Aufrufe, Rest bleibt roh
# ---------------------------------------------------------------------------

def q(s):
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'") + "'"

IMPORT_LINE = ('{% from "components.njk" import hero, intro, zigzag, sectionQuote, '
               'iconList, planTimeline, ctaButton, contactBridge with context %}\n')

BJUNK = r"avia-builder-el-\d+(?:  (?:el_(?:before|after)_av_[a-z_]+|avia-builder-el-(?:first|last|no-sibling)))*"

def flex(canon):
    """Kanonischen String zu Regex machen; Builder-Nummern flexibel."""
    esc = re.escape(canon)
    esc = re.sub(r'avia-builder-el-\d+', r'avia-builder-el-\\d+', esc)
    return esc

def make_pat(canon, slots):
    marked = canon
    for i, (needle, _grp) in enumerate(slots):
        assert needle in marked, f'Parser-Slot fehlt: {needle[:60]}'
        marked = marked.replace(needle, f'@@S{i}@@')
    esc = flex(marked)
    for i, (needle, grp) in enumerate(slots):
        first = esc.find(f'@@S{i}@@')
        esc = esc[:first] + grp + esc[first + len(f'@@S{i}@@'):]
        # weitere Vorkommen desselben Werts als Backreferenz
        name = re.match(r'\(\?P<([a-z0-9]+)>', grp)
        backref = f'(?P={name.group(1)})' if name else grp
        esc = esc.replace(f'@@S{i}@@', backref)
    return re.compile(esc, re.S)

hero_pat = make_pat(hero_canon, [
    (D['heroSection'], r"(?P<section>av-[a-z0-9]+-[a-f0-9]{32})"),
    ('post-entry-5003', r"post-entry-(?P<pid>\d+)"),
    (D['heroHeading'], r"(?P<heading>av-[a-z0-9]+-[a-f0-9]{32})"),
    ('Events &amp; Waldcafé im Waldgeflüster', r"(?P<title>.*?)"),
    (D['heroHr'], r"(?P<hr>av-[a-z0-9]+-[a-f0-9]{32})"),
    (D['heroButton'], r"(?P<button>av-[a-z0-9]+-[a-f0-9]{32})"),
    ('Jetzt kontaktieren', r"(?P<label>[^<\"]+)"),
])

bridge_pat = make_pat(bridge_canon, [
    ('post-entry-5003', r"post-entry-(?P<pid>\d+)"),
    ('Fragen zu unseren Events?', r"(?P<heading>.*?)"),
    ('<p>Schreibt uns über das Formular oder ruft uns an – wir helfen euch gerne weiter.</p>\n',
     r"(?P<text>.*?)"),
])

ROW_OPEN = (r"<div id='([a-z0-9_-]+)'  class='av-layout-grid-container (av-[a-z0-9]+-[a-f0-9]{32}) "
            r"entry-content-wrapper main_color av-flex-cells av-break-at-tablet ([a-z_ 0-9-]*?) "
            r"pfeilcontainer( av-grid-order-reverse)? grid-row-not-first  container_wrap fullsize'  >\n")
CELL = (r"<div class='flex_cell (av-[a-z0-9]+-[a-f0-9]{32}) av-gridrow-cell av_one_half no_margin "
        r"([a-z_ 0-9-]*)'  ><div class='flex_cell_inner'>\n")
CONTENT = r"((?:(?!<div class='flex_cell).)*?</section>)\n"   # nie über Zellgrenzen hinweg
ARROW = (r"<div  class='hr (av-[a-z0-9]+-[a-f0-9]{32}) hr-invisible  " + BJUNK + r" '>"
         r"<span class='hr-inner '><span class=\"hr-inner-style\"></span></span></div>\n"
         r"<span  class='av_font_icon (av-[a-z0-9]+-[a-f0-9]{32}) avia_animate_when_visible av-icon-style- avia-icon-pos-left pfeil(rechts|links)'>"
         r"<span class='av-icon-char' aria-hidden='true' data-av_icon='(.)' data-av_iconfont='entypo-fontello' ></span></span>\n")
ROW_CLOSE = r"</div></div>\n?</div>"
zig_a_pat = re.compile(ROW_OPEN + CELL + CONTENT + r"</div></div>" + CELL + ARROW + ROW_CLOSE, re.S)
zig_b_pat = re.compile(ROW_OPEN + CELL + ARROW + r"</div></div>" + CELL + CONTENT + ROW_CLOSE, re.S)

secq_pat = re.compile(
    r"<div id='(?P<id>[a-z0-9_-]+)'  class='avia-section (?P<section>av-[a-z0-9]+-[a-f0-9]{32}) main_color avia-section-(?P<size>default|small) avia-no-border-styling (?P<extra>[a-zA-Z_ 0-9-]*?) " + BJUNK + r"  avia-bg-style-(?P<bg>scroll|fixed) container_wrap fullsize'  >"
    r"<div class='container av-section-cont-open' ><div class='template-page content  av-content-full alpha units'>"
    r"<div class='post-entry post-entry-type-page post-entry-\d+'><div class='entry-content-wrapper clearfix'>\n"
    r"<div  (?:id=\"(?P<headingId>[a-z0-9_-]+)\"  )?class='av-special-heading (?P<heading>av-[a-z0-9]+-[a-f0-9]{32}) av-special-heading-h2 (?P<headingExtra>(?:custom-color-heading )?)blockquote modern-quote modern-centered  " + BJUNK + r"\s*'>"
    r"<h2 class='av-special-heading-tag '  itemprop=\"headline\"  >(?P<title>.*?)</h2>"
    r"<div class=\"special-heading-border\"><div class=\"special-heading-inner-border\"></div></div></div>\n"
    r"(?P<content>.*?)</div></div></div><!-- close content main div --></div></div>", re.S)

iconlist_pat = re.compile(
    r"<div  class='avia-icon-list-container (?P<hash>av-[a-z0-9]+-[a-f0-9]{32})  " + BJUNK + r" '>"
    r"<ul class='avia-icon-list avia_animate_when_almost_visible avia-icon-list-left av-iconlist-big (?P=hash) avia-iconlist-animate'>\n"
    r"(?P<items>.*?)</ul></div>\n(?:</p>\n)?", re.S)
iconitem_pat = re.compile(
    r"<li><div class='iconlist_icon (?P<icon>av-[a-z0-9]+-[a-f0-9]{32}) avia-font-entypo-fontello'>"
    r"<span class='iconlist-char' aria-hidden='true' data-av_icon='(?P<char>.)' data-av_iconfont='entypo-fontello'></span></div>"
    r"<article class=\"article-icon-entry \"  itemscope=\"itemscope\" itemtype=\"https://schema.org/CreativeWork\" >"
    r"<div class=\"iconlist_content_wrap\"><header class=\"entry-content-header\" aria-label=\"Icon: (?P<aria>[^\"]*)\">"
    r"<h3 class='av_iconlist_title iconlist_title  '  itemprop=\"headline\" >(?P<title>.*?)</h3></header>"
    r"<div class='iconlist_content '  itemprop=\"text\" ><p[^>]*>(?P<text>.*?)</p>\n"
    r"</div></div><footer class=\"entry-footer\"></footer></article><div class=\"iconlist-timeline\"></div></li>\n", re.S)

timeline_pat = re.compile(
    r"<div  id=\"avia-timeline-1\"  class='avia-timeline-container (?P<hash>av-[a-z0-9]+-[a-f0-9]{32}) av-slideshow-ui  " + BJUNK + r"  avia-slideshow-carousel' avia-data-slides='\d+'>"
    r"<ul class='avia-timeline avia-timeline-horizontal av-milestone-placement-top avia-timeline-boxshadow avia_animate_when_almost_visible avia-timeline-animate'>\n"
    r"(?P<items>.*?)</ul><div class='avia-slideshow-arrows.*?</div></div>", re.S)
milestone_pat = re.compile(
    r"<li  class='av-milestone (?P<hash>av-[a-z0-9]+-[a-f0-9]{32}) av-animated-generic fade-in av-milestone-(?:odd|even)'>"
    r"<h2 class='av-milestone-date ' id='milestone-\d+' ><strong>\d+<span class='av-milestone-indicator'></span></strong></h2>"
    r"<div class=\"av-milestone-icon-wrap\"><span class='av-milestone-icon milestone_icon avia-font-entypo-fontello'><span class='av-milestone-icon-inner milestone_inner'>"
    r"<i class='milestone-char' aria-hidden='true' data-av_icon='(?P<char>.)' data-av_iconfont='entypo-fontello'></i></span></span></div>"
    r"<article class='av-milestone-content-wrap'><div class='av-milestone-contentbox'>"
    r"<header class=\"entry-content-header\" aria-label=\"Milestone: (?P<aria>[^\"]*)\"><h4 class='av-milestone-title '>(?P<title>.*?)</h4></header>"
    r"<div class='av-milestone-content'><p[^>]*>(?P<text>.*?)</p>\n"
    r"</div></div><footer class='av-milestone-article-footer entry-footer'></footer></article></li>\n", re.S)

cta_pat = re.compile(
    r"<div  class='avia-button-wrap (?P<hash>av-[a-z0-9]+-[a-f0-9]{32})-wrap avia-button-(?P<pos>center|left)  " + BJUNK + r"(?P<wrapExtra>(?: {1,2}[a-z-]+)*) '>"
    r"<a href='(?P<href>[^']*)'  class='avia-button (?P=hash) av-link-btn avia-icon_select-(?P<iconsel>no|yes-left-icon) avia-size-large avia-position-(?P=pos)(?P<color>(?: avia-(?:font-)?color-[a-z-]+)*)'   aria-label=\"(?P<label>[^\"]*)\">"
    r"(?:<span class='avia_button_icon avia_button_icon_left' aria-hidden='true' data-av_icon='(?P<char>.)' data-av_iconfont='entypo-fontello'></span>)?"
    r"<span class='avia_iconbox_title' >(?P<label2>[^<]*)</span>"
    r"(?P<bg><span class='avia_button_background avia-button avia-color-theme-color-subtle' ></span>)?</a></div>", re.S)

def emit_iconlist(mm):
    items, pos, src = [], 0, mm.group('items')
    for it in iconitem_pat.finditer(src):
        if it.start() != pos: return None
        pos = it.end()
        items.append(it.groupdict())
    if pos != len(src) or not items: return None
    entries = [(f"  {{ icon: {q(it['icon'])}, char: {q(it['char'])}, aria: {q(it['aria'])},\n"
                f"    title: {q(it['title'])},\n"
                f"    text: {q(it['text'])} }}") for it in items]
    return ("{{ iconList([\n" + ",\n".join(entries) + "\n"
            + f"], {{ hash: {q(mm.group('hash'))} }}) }}}}")

def emit_timeline(mm):
    steps, pos, src = [], 0, mm.group('items')
    for it in milestone_pat.finditer(src):
        if it.start() != pos: return None
        pos = it.end()
        steps.append(it.groupdict())
    if pos != len(src) or not steps: return None
    entries = [(f"  {{ hash: {q(st['hash'])}, char: {q(st['char'])}, aria: {q(st['aria'])},\n"
                f"    title: {q(st['title'])},\n"
                f"    text: {q(st['text'])} }}") for st in steps]
    return ("{{ planTimeline([\n" + ",\n".join(entries) + "\n"
            + f"], {{ hash: {q(mm.group('hash'))} }}) }}}}")

def emit_cta(mm):
    if mm.group('label2') != mm.group('label'): return None
    has_char, has_bg = bool(mm.group('char')), bool(mm.group('bg'))
    if has_char == has_bg: return None            # Makro bildet nur char XOR bg ab
    if has_char and mm.group('iconsel') != 'yes-left-icon': return None
    if not has_char and mm.group('iconsel') != 'no': return None
    o = [f"hash: {q(mm.group('hash'))}"]
    if mm.group('pos') != 'center': o.append(f"pos: {q(mm.group('pos'))}")
    if mm.group('href') != '#kontakt': o.append(f"href: {q(mm.group('href'))}")
    if has_char: o.append(f"char: {q(mm.group('char'))}")
    if mm.group('color'): o.append(f"color: {q(mm.group('color'))}")
    extra = (mm.group('wrapExtra') or '').strip()
    if extra: o.append(f"wrapExtra: {q(extra)}")
    return "{{ ctaButton(" + q(mm.group('label')) + ", { " + ", ".join(o) + " }) }}"

def parse_content(content):
    """Inhalt einer Zitat-Sektion in Makros + Roh-Chunks übersetzen."""
    out, pos, scan = [], 0, 0
    while scan < len(content):
        best = None
        for pat, emitter in ((iconlist_pat, emit_iconlist),
                             (timeline_pat, emit_timeline),
                             (cta_pat, emit_cta)):
            mm = pat.search(content, scan)
            if mm and (best is None or mm.start() < best[0].start()):
                best = (mm, emitter)
        if not best: break
        mm, emitter = best
        code = emitter(mm)
        if code is None:
            scan = mm.start() + 1
            continue
        out.append(content[pos:mm.start()])
        out.append(code + "\n")
        pos = scan = mm.end()
    out.append(content[pos:])
    return "".join(out)

def build_body(slug):
    txt = normalize_self_links(load(slug), ACTIVE[slug])
    pieces, consumed = [], []

    def try_block(pat, emitter, once=False):
        pos = 0
        while True:
            mm = pat.search(txt, pos)
            if not mm: return
            if any(s < mm.end() and mm.start() < e for s, e in consumed):
                pos = mm.start() + 1          # verdeckt spätere Treffer nicht
                continue
            code = emitter(mm)
            if code is None:
                pos = mm.start() + 1
                continue
            consumed.append((mm.start(), mm.end()))
            pieces.append((mm.start(), mm.end(), code))
            pos = mm.end()
            if once: return

    def emit_hero(mm):
        o = []
        if mm.group('section') != D['heroSection']: o.append(f"section: {q(mm.group('section')[3:])}")
        if mm.group('heading') != D['heroHeading']: o.append(f"heading: {q(mm.group('heading')[3:])}")
        if mm.group('hr') != D['heroHr']: o.append(f"hr: {q(mm.group('hr')[3:])}")
        if mm.group('button') != D['heroButton']: o.append(f"button: {q(mm.group('button')[3:])}")
        if mm.group('label') != 'Jetzt kontaktieren': o.append(f"buttonLabel: {q(mm.group('label'))}")
        arg = "{ " + ", ".join(o) + " }" if o else "{}"
        return ("{% set heroTitle %}" + mm.group('title') + "{% endset %}\n"
                "{{ hero(heroTitle, " + arg + ") }}")

    def emit_intro(mm):
        o = f", {{ wrapId: {q(mm.group(1))} }}" if mm.group(1) != 'after_submenu_1' else ""
        return ("{% set introText %}" + mm.group(3) + "{% endset %}\n"
                "{{ intro(introText" + o + ") }}")

    def emit_bridge(mm):
        return ("{% set kontaktHeading %}" + mm.group('heading') + "{% endset %}\n"
                "{% set kontaktText %}" + mm.group('text') + "{% endset %}\n"
                "{{ contactBridge(kontaktHeading, kontaktText) }}")

    def zig_opts(rid, row, reverse, cellA, extraA, cellB, extraB, hr, icon, direction, char, arrow_first):
        o = [f"id: {q(rid)}", f"row: {q(row)}", f"cellA: {q(cellA)}", f"cellB: {q(cellB)}"]
        ea = ' '.join(t for t in extraA.split() if not t.startswith(('avia-builder-el', 'el_before', 'el_after')))
        eb = ' '.join(t for t in extraB.split() if not t.startswith(('avia-builder-el', 'el_before', 'el_after')))
        if ea: o.append(f"cellAExtra: {q(' ' + ea)}")
        if eb: o.append(f"cellBExtra: {q(' ' + eb)}")
        if reverse: o.append("reverse: true")
        if arrow_first: o.append("arrowFirst: true")
        o += [f"hr: {q(hr)}", f"icon: {q(icon)}", f"dir: {q(direction)}", f"char: {q(char)}"]
        return o

    def emit_zig_a(mm):   # Inhalt links, Pfeil rechts
        (rid, row, _junk, rev, cellA, extraA, content, cellB, extraB, hr, icon, direction, char) = mm.groups()
        o = zig_opts(rid, row, rev, cellA, extraA, cellB, extraB, hr, icon, direction, char, False)
        return ("{% call zigzag({ " + ", ".join(o) + " }) %}\n" + content + "\n{% endcall %}")

    def emit_zig_b(mm):   # Pfeil links, Inhalt rechts
        (rid, row, _junk, rev, cellA, extraA, hr, icon, direction, char, cellB, extraB, content) = mm.groups()
        o = zig_opts(rid, row, rev, cellA, extraA, cellB, extraB, hr, icon, direction, char, True)
        return ("{% call zigzag({ " + ", ".join(o) + " }) %}\n" + content + "\n{% endcall %}")

    secq_count = [0]
    def emit_secq(mm):
        secq_count[0] += 1
        n = secq_count[0]
        o = [f"id: {q(mm.group('id'))}", f"section: {q(mm.group('section'))}",
             f"heading: {q(mm.group('heading'))}", f"title: secTitle{n}"]
        if mm.group('size') != 'default': o.append(f"size: {q(mm.group('size'))}")
        if mm.group('bg') != 'scroll': o.append(f"bg: {q(mm.group('bg'))}")
        extra = (mm.group('extra') or '').strip()
        if extra: o.append(f"extra: {q(extra + ' ')}")
        if mm.group('headingId'): o.append(f"headingId: {q(mm.group('headingId'))}")
        if mm.group('headingExtra') != 'custom-color-heading ':
            o.append(f"headingExtra: {q(mm.group('headingExtra'))}")
        body = parse_content(mm.group('content'))
        return ("{% set secTitle" + str(n) + " %}" + mm.group('title') + "{% endset %}\n"
                "{% call sectionQuote({ " + ", ".join(o) + " }) %}\n" + body + "{% endcall %}")

    try_block(hero_pat, emit_hero, once=True)
    try_block(INTRO_PAT, emit_intro, once=True)
    try_block(bridge_pat, emit_bridge, once=True)
    try_block(secq_pat, emit_secq)
    try_block(zig_a_pat, emit_zig_a)
    try_block(zig_b_pat, emit_zig_b)

    pieces.sort()
    out, pos = [IMPORT_LINE], 0
    for s, e, code in pieces:
        out.append(txt[pos:s]); out.append(code); pos = e
    out.append(txt[pos:])
    raw = len(txt) - sum(e - s for s, e, _ in pieces)
    print(f"{slug:12s} blocks={len(pieces):2d} raw={raw:7d}/{len(txt)} bytes")
    return "".join(out)

for slug in ['events', 'feiern', 'trauerfeier', 'winter', 'location', 'bilder',
             'faq', 'rechtliches', 'index']:
    with open(os.path.join(BODIES, f'{slug}.njk'), 'w', encoding='utf-8') as f:
        f.write(build_body(slug))

# ---------------------------------------------------------------------------
# 3. Gemeinsamer Kern für /heiraten-schwaebische-alb/ und
#    /freie-hochzeitstermine/ (Seiten sind zu ~95 % identisch).
#    Basis ist die redesignte Heiraten-Fassung (inkl. wg-*-Themenklassen);
#    Termine ergänzt nur den Terminblock und eine eigene H1.
# ---------------------------------------------------------------------------
core = build_body('heiraten')

H1 = 'Heiraten im Wald – Eure Traumhochzeit in der Natur'
needle = '{% set heroTitle %}' + H1 + '{% endset %}'
assert needle in core, 'Hero-Titel nicht gefunden'
core = core.replace(needle, "{% set heroTitle = heroTitle or '" + H1 + "' %}")

# Terminliste aus der Termine-Seite übernehmen; Überschrift bekommt den von
# post-1143.css gestylten Hash (beide Seiten laden dieselbe Per-Post-CSS).
termine_txt = normalize_self_links(load('termine'), ACTIVE['termine'])
tm = re.search(r"<div  id=\"termine\".*?</section>\n?", termine_txt, re.S)
assert tm, 'Terminblock nicht gefunden'
tblock = tm.group(0).replace('av-2pj97b-4a134c329b8f681333f8f01c1ea8ac89',
                             'av-2pj97b-cb7123c9b476ae51f44c1ef8ee8b315e')
anchor = '</div></section>\n<div  id="location"'
assert anchor in core, 'Einfügepunkt für Terminblock nicht gefunden'
core = core.replace(anchor, '</div></section>\n{% if termineList %}' + tblock
                    + '{% endif %}<div  id="location"', 1)

core = core.replace('post-entry-1143', 'post-entry-{{ pid }}')
with open(os.path.join(BODIES, 'wedding-core.njk'), 'w', encoding='utf-8') as f:
    f.write(core)

STUB = ('{# Heiraten & Freie Hochzeitstermine teilen denselben Seitenkern –\n'
        '   Unterschiede (H1, Terminliste) steuert die Front Matter. #}\n'
        '{% include "bodies/wedding-core.njk" %}\n')
for slug in ['heiraten', 'termine']:
    with open(os.path.join(BODIES, f'{slug}.njk'), 'w', encoding='utf-8') as f:
        f.write(STUB)
print('wedding-core.njk geschrieben:', len(core), 'Bytes')
print('OK')
