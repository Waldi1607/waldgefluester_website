/* Waldgeflüster Termine: rendert events.json als Liste (/eigene-events/) oder Banner (Startseite).
   Konfiguration über data-Attribute am eigenen <script>-Tag:
   data-events-src (Pfad zur events.json), data-mode ("list"|"banner"), data-target-url (Banner-Linkziel). */
(function () {
  var script = document.currentScript;
  if (!script) return;
  var src = script.getAttribute('data-events-src') || 'events.json';
  var mode = script.getAttribute('data-mode') || 'list';
  var targetUrl = script.getAttribute('data-target-url') || '';

  var MONATE = ['Jan', 'Feb', 'März', 'Apr', 'Mai', 'Juni', 'Juli', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'];
  var TAGE = ['So', 'Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa'];

  function parseDay(str) {
    var p = (str || '').split('-');
    return new Date(+p[0], +p[1] - 1, +p[2]);
  }

  function fmtDate(ev) {
    var d = parseDay(ev.date);
    var out = TAGE[d.getDay()] + ', ' + d.getDate() + '. ' + MONATE[d.getMonth()] + ' ' + d.getFullYear();
    if (ev.end && ev.end !== ev.date) {
      var e = parseDay(ev.end);
      out = d.getDate() + '. ' + MONATE[d.getMonth()] + ' – ' + e.getDate() + '. ' + MONATE[e.getMonth()] + ' ' + e.getFullYear();
    }
    return out;
  }

  function upcoming(data) {
    var today = new Date();
    today.setHours(0, 0, 0, 0);
    return (data.events || [])
      .filter(function (ev) { return ev && ev.title && ev.date && parseDay(ev.end || ev.date) >= today; })
      .sort(function (a, b) { return parseDay(a.date) - parseDay(b.date); });
  }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text) n.textContent = text;
    return n;
  }

  function renderList(events) {
    var target = document.getElementById('wg-event-list');
    if (!target) return;
    target.innerHTML = '';
    if (!events.length) {
      target.appendChild(el('p', 'wg-events-empty',
        'Aktuell sind keine Termine geplant – schaut bald wieder vorbei oder folgt uns auf Instagram!'));
      return;
    }
    events.forEach(function (ev) {
      var item = el('div', 'wg-event');
      var head = el('div', 'wg-event-head');
      head.appendChild(el('span', 'wg-event-date', fmtDate(ev)));
      if (ev.time) head.appendChild(el('span', 'wg-event-time', ev.time));
      item.appendChild(head);
      if (ev.url) {
        var a = el('a', 'wg-event-title', ev.title);
        a.href = ev.url;
        item.appendChild(a);
      } else {
        item.appendChild(el('div', 'wg-event-title', ev.title));
      }
      if (ev.teaser) item.appendChild(el('p', 'wg-event-teaser', ev.teaser));
      target.appendChild(item);
    });
  }

  function renderBanner(events) {
    var banner = document.getElementById('wg-event-banner');
    if (!banner || !events.length) return;
    var inner = banner.querySelector('.container') || banner;
    inner.innerHTML = '';
    var wrap = el('a', 'wg-banner-link');
    wrap.href = targetUrl || '#';
    wrap.appendChild(el('span', 'wg-banner-label', 'Aktuelle Termine'));
    var list = el('span', 'wg-banner-items');
    events.slice(0, 3).forEach(function (ev) {
      var item = el('span', 'wg-banner-item');
      item.appendChild(el('span', 'wg-banner-date', fmtDate(ev)));
      item.appendChild(el('span', 'wg-banner-title', ev.title));
      list.appendChild(item);
    });
    wrap.appendChild(list);
    wrap.appendChild(el('span', 'wg-banner-more', 'Alle Termine →'));
    inner.appendChild(wrap);
    banner.hidden = false;
  }

  function init() {
    fetch(src, { cache: 'no-store' })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (data) {
        var events = upcoming(data);
        if (mode === 'banner') renderBanner(events);
        else renderList(events);
      })
      .catch(function () {
        if (mode !== 'banner') {
          var target = document.getElementById('wg-event-list');
          if (target) target.appendChild(el('p', 'wg-events-empty',
            'Termine konnten nicht geladen werden – ruft uns gerne an: +49 (0)173 614 98 96.'));
        }
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
