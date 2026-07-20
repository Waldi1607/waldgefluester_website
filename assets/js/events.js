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

  function badge(ev) {
    var d = parseDay(ev.date);
    var wrap = el('time', 'wg-event-badge');
    var e = ev.end && ev.end !== ev.date ? parseDay(ev.end) : null;
    wrap.setAttribute('datetime', ev.date);
    wrap.setAttribute('aria-label', fmtDate(ev));
    wrap.appendChild(el('span', 'wg-badge-day', e ? d.getDate() + '.–' + e.getDate() + '.' : String(d.getDate())));
    wrap.appendChild(el('span', 'wg-badge-month', MONATE[(e || d).getMonth()]));
    wrap.appendChild(el('span', 'wg-badge-year', String(d.getFullYear())));
    return wrap;
  }

  function weekdayLine(ev) {
    var d = parseDay(ev.date);
    if (ev.end && ev.end !== ev.date) return 'Zweitägig';
    return ['Sonntag','Montag','Dienstag','Mittwoch','Donnerstag','Freitag','Samstag'][d.getDay()];
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
      var item = el('article', 'wg-event');
      item.appendChild(badge(ev));
      var body = el('div', 'wg-event-body');
      var head = el('div', 'wg-event-head');
      head.appendChild(el('span', 'wg-event-weekday', weekdayLine(ev)));
      if (ev.time) head.appendChild(el('span', 'wg-event-time', ev.time));
      body.appendChild(head);
      var title = el('h3', 'wg-event-title');
      if (ev.url) {
        var a = el('a', '', ev.title);
        a.href = ev.url;
        title.appendChild(a);
      } else {
        title.textContent = ev.title;
      }
      body.appendChild(title);
      if (ev.teaser) body.appendChild(el('p', 'wg-event-teaser', ev.teaser));
      item.appendChild(body);
      target.appendChild(item);
    });
  }

  function renderBanner(events) {
    var banner = document.getElementById('wg-event-banner');
    if (!banner || !events.length) return;
    var inner = banner.querySelector('.container') || banner;
    inner.innerHTML = '';
    inner.appendChild(el('span', 'wg-home-kicker', 'Bei uns ist was los'));
    inner.appendChild(el('h2', 'wg-home-title', 'Kommende Events & Waldcafé-Termine'));
    var grid = el('div', 'wg-home-grid');
    events.slice(0, 3).forEach(function (ev) {
      var card = el(ev.url ? 'a' : 'div', 'wg-home-card');
      if (ev.url) card.href = ev.url;
      card.appendChild(badge(ev));
      var body = el('div', 'wg-home-card-body');
      body.appendChild(el('span', 'wg-event-weekday', weekdayLine(ev) + (ev.time ? ' · ' + ev.time : '')));
      body.appendChild(el('div', 'wg-event-title', ev.title));
      if (ev.teaser) body.appendChild(el('p', 'wg-event-teaser', ev.teaser));
      card.appendChild(body);
      grid.appendChild(card);
    });
    inner.appendChild(grid);
    var more = el('a', 'wg-home-more', 'Alle Termine ansehen');
    more.href = targetUrl || '#';
    inner.appendChild(more);
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
