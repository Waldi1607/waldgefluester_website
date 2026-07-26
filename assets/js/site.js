/* Waldgeflüster – schlankes Site-Script des Neuaufbaus.
   Module: Navigation, Scroll-Zustand, Cookie-Consent (GTM Consent Mode),
   Lightbox, Tabs, Zähler, Kontaktformular. Kein jQuery, keine Frameworks. */
(function () {
  'use strict';

  var WG_EN = (document.documentElement.lang || 'de').indexOf('en') === 0;
  var body = document.body;

  /* ---------- Navigation (Burger) ---------- */
  var navToggle = document.querySelector('[data-nav-toggle]');
  if (navToggle) {
    navToggle.addEventListener('click', function () {
      var open = body.classList.toggle('nav-open');
      navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      navToggle.setAttribute('aria-label', open ? (WG_EN ? 'Close menu' : 'Menü schließen') : (WG_EN ? 'Open menu' : 'Menü öffnen'));
    });
    document.querySelectorAll('.wg-nav a').forEach(function (a) {
      a.addEventListener('click', function () {
        body.classList.remove('nav-open');
        navToggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* ---------- Scroll-Zustand (Nach-oben-Pfeil) ---------- */
  var onScroll = function () {
    body.classList.toggle('scrolled', window.scrollY > Math.max(520, window.innerHeight * 0.7));
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------- Hero-Scrollpfeil: zur nächsten Sektion ---------- */
  var heroScroll = document.querySelector('[data-hero-scroll]');
  if (heroScroll) {
    heroScroll.addEventListener('click', function (e) {
      var hero = heroScroll.closest('.wg-hero');
      var next = hero && hero.nextElementSibling;
      if (next) { e.preventDefault(); next.scrollIntoView({ behavior: 'smooth' }); }
    });
  }

  /* ---------- Cookie-Consent (Google Consent Mode v2) ---------- */
  var bar = document.getElementById('wg-cookie-bar');
  if (bar) {
    var stored = null;
    try { stored = localStorage.getItem('wgConsent'); } catch (e) {}
    if (!stored) bar.hidden = false;
    bar.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-consent]');
      if (!btn) return;
      var granted = btn.getAttribute('data-consent') === 'accept';
      try { localStorage.setItem('wgConsent', granted ? 'granted' : 'denied'); } catch (err) {}
      if (granted && typeof gtag === 'function') {
        gtag('consent', 'update', { ad_storage: 'granted', ad_user_data: 'granted', ad_personalization: 'granted', analytics_storage: 'granted' });
      }
      bar.hidden = true;
    });
  }

  /* ---------- Lightbox für Galerien ---------- */
  var lightbox = null;
  function openLightbox(href, alt) {
    if (!lightbox) {
      lightbox = document.createElement('dialog');
      lightbox.className = 'wg-lightbox';
      lightbox.innerHTML = '<button type="button" aria-label="' + (WG_EN ? 'Close' : 'Schließen') + '">×</button><img alt="">';
      lightbox.addEventListener('click', function (e) {
        if (e.target === lightbox || e.target.tagName === 'BUTTON') lightbox.close();
      });
      document.body.appendChild(lightbox);
    }
    var img = lightbox.querySelector('img');
    img.src = href;
    img.alt = alt || '';
    lightbox.showModal();
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest('[data-lightbox]');
    if (!a) return;
    e.preventDefault();
    var thumb = a.querySelector('img');
    openLightbox(a.getAttribute('href'), thumb && thumb.alt);
  });

  /* ---------- Tabs ---------- */
  document.querySelectorAll('.wg-tabs').forEach(function (tabs) {
    var buttons = tabs.querySelectorAll('.wg-tabs__list button');
    var panels = tabs.querySelectorAll('.wg-tabs__panel');
    buttons.forEach(function (btn, i) {
      btn.setAttribute('aria-selected', i === 0 ? 'true' : 'false');
      if (panels[i]) panels[i].hidden = i !== 0;
      btn.addEventListener('click', function () {
        buttons.forEach(function (b, j) {
          b.setAttribute('aria-selected', b === btn ? 'true' : 'false');
          if (panels[j]) panels[j].hidden = b !== btn;
        });
      });
    });
  });

  /* ---------- Zähler (Faktenband) ---------- */
  var counters = document.querySelectorAll('[data-count-to]');
  if (counters.length && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        io.unobserve(entry.target);
        var el = entry.target;
        var target = parseInt(el.getAttribute('data-count-to'), 10) || 0;
        var start = null;
        function tick(ts) {
          if (!start) start = ts;
          var p = Math.min((ts - start) / 1200, 1);
          el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3))).toLocaleString(WG_EN ? 'en-US' : 'de-DE');
          if (p < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
      });
    }, { threshold: 0.4 });
    counters.forEach(function (el) { io.observe(el); });
  }

  /* ---------- Kontaktformular ---------- */
  var form = document.querySelector('[data-wg-contact]');
  if (!form) return;
  var fields = Array.prototype.slice.call(form.querySelectorAll('input, select, textarea'));
  var submit = form.querySelector('.wg-contact-submit');
  var submitLabel = submit ? submit.querySelector('span') : null;
  var status = form.querySelector('[data-wg-form-status]');

  function errorMessage(field) {
    if (field.validity.valueMissing) return WG_EN ? 'Please fill in this field.' : 'Bitte füllt dieses Feld aus.';
    if (field.validity.typeMismatch) return WG_EN ? 'Please enter a valid e-mail address.' : 'Bitte gebt eine gültige E-Mail-Adresse ein.';
    if (field.validity.patternMismatch) return WG_EN ? 'Please enter a four-digit year.' : 'Bitte gebt eine vierstellige Jahreszahl ein.';
    if (field.validity.tooShort) return WG_EN ? 'Please write at least 20 characters.' : 'Bitte schreibt uns mindestens 20 Zeichen.';
    if (field.validity.rangeUnderflow || field.validity.rangeOverflow) return WG_EN ? 'Please enter a realistic number of guests.' : 'Bitte gebt eine realistische Personenanzahl ein.';
    return WG_EN ? 'Please check this entry.' : 'Bitte prüft diese Angabe.';
  }
  function errorNode(field) {
    var ids = (field.getAttribute('aria-describedby') || '').split(/\s+/);
    for (var i = 0; i < ids.length; i += 1) {
      var node = document.getElementById(ids[i]);
      if (node && node.classList.contains('wg-field-error')) return node;
    }
    return null;
  }
  function showError(field) {
    var node = errorNode(field);
    var wrapper = field.closest('.wg-field') || field.closest('.wg-consent');
    if (wrapper) wrapper.classList.add('is-invalid');
    field.setAttribute('aria-invalid', 'true');
    if (node) node.textContent = errorMessage(field);
  }
  function clearError(field) {
    if (!field.validity.valid) return;
    var node = errorNode(field);
    var wrapper = field.closest('.wg-field') || field.closest('.wg-consent');
    if (wrapper) wrapper.classList.remove('is-invalid');
    field.removeAttribute('aria-invalid');
    if (node) node.textContent = '';
  }
  fields.forEach(function (field) {
    field.addEventListener('invalid', function () { showError(field); });
    field.addEventListener('input', function () { clearError(field); });
    field.addEventListener('change', function () { clearError(field); });
  });

  form.addEventListener('submit', async function (event) {
    event.preventDefault();
    var data = new FormData(form);
    var value = function (name) { return String(data.get(name) || '').trim(); };
    var payload = {
      name: value('name'), email: value('email'), phone: value('phone'),
      event: value('event'), guests: Number(value('guests')), year: value('year'),
      message: value('message'), privacyAccepted: data.get('privacy') === 'on',
      source: window.location.pathname
    };
    var endpoint = form.getAttribute('data-endpoint') || window.WG_CONTACT_ENDPOINT || '';
    if (submit) { submit.disabled = true; submit.setAttribute('aria-busy', 'true'); }
    if (submitLabel) submitLabel.textContent = WG_EN ? 'Sending inquiry …' : 'Anfrage wird gesendet …';

    function resetSubmit() {
      if (submit) { submit.disabled = false; submit.removeAttribute('aria-busy'); }
      if (submitLabel) submitLabel.textContent = submit.getAttribute('data-default-label');
    }
    if (!endpoint) {
      if (status) status.textContent = WG_EN
        ? 'The form is ready. Secure sending will be activated at launch.'
        : 'Das Formular ist bereit. Der sichere Versand wird beim Onlinegang aktiviert.';
      resetSubmit();
      return;
    }
    try {
      var response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!response.ok) throw new Error('contact_request_failed');
      if (window.wgTrack) {
        window.wgTrack('anfrage_abgeschickt', { eventform: payload.event, personenanzahl: payload.guests, wunschjahr: payload.year });
      }
      form.reset();
      if (status) status.textContent = WG_EN
        ? 'Thank you! Your inquiry has arrived. We will get back to you personally.'
        : 'Vielen Dank! Eure Anfrage ist angekommen. Wir melden uns persönlich bei euch.';
    } catch (error) {
      if (status) status.textContent = WG_EN
        ? 'The inquiry could not be sent right now. Please try again or give us a quick call.'
        : 'Die Anfrage konnte gerade nicht gesendet werden. Bitte versucht es erneut oder ruft uns kurz an.';
    } finally {
      resetSubmit();
    }
  });
})();
