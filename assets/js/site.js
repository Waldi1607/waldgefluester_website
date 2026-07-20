(function () {
  'use strict';

  var form = document.querySelector('[data-wg-contact]');
  if (!form) return;

  var fields = Array.prototype.slice.call(form.querySelectorAll('input, select, textarea'));
  var submit = form.querySelector('.wg-contact-submit');
  var submitLabel = submit ? submit.querySelector('span') : null;
  var status = form.querySelector('[data-wg-form-status]');

  function errorMessage(field) {
    if (field.validity.valueMissing) return 'Bitte füllt dieses Feld aus.';
    if (field.validity.typeMismatch) return 'Bitte gebt eine gültige E-Mail-Adresse ein.';
    if (field.validity.patternMismatch) return 'Bitte gebt eine vierstellige Jahreszahl ein.';
    if (field.validity.tooShort) return 'Bitte schreibt uns mindestens 20 Zeichen.';
    if (field.validity.rangeUnderflow || field.validity.rangeOverflow) return 'Bitte gebt eine realistische Personenanzahl ein.';
    return 'Bitte prüft diese Angabe.';
  }

  function errorNode(field) {
    var describedBy = (field.getAttribute('aria-describedby') || '').split(/\s+/);
    for (var i = 0; i < describedBy.length; i += 1) {
      var node = document.getElementById(describedBy[i]);
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
      name: value('name'),
      email: value('email'),
      phone: value('phone'),
      event: value('event'),
      guests: Number(value('guests')),
      year: value('year'),
      message: value('message'),
      privacyAccepted: data.get('privacy') === 'on',
      source: window.location.pathname
    };
    var endpoint = form.getAttribute('data-endpoint') || window.WG_CONTACT_ENDPOINT || '';

    if (submit) {
      submit.disabled = true;
      submit.setAttribute('aria-busy', 'true');
    }
    if (submitLabel) submitLabel.textContent = 'Anfrage wird gesendet …';

    if (!endpoint) {
      if (status) status.textContent = 'Das Formular ist bereit. Der sichere Versand wird beim Onlinegang aktiviert.';
      if (submit) {
        submit.disabled = false;
        submit.removeAttribute('aria-busy');
      }
      if (submitLabel) submitLabel.textContent = submit.getAttribute('data-default-label');
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
        window.wgTrack('anfrage_abgeschickt', {
          eventform: payload.event,
          personenanzahl: payload.guests,
          wunschjahr: payload.year
        });
      }
      form.reset();
      if (status) status.textContent = 'Vielen Dank! Eure Anfrage ist angekommen. Wir melden uns persönlich bei euch.';
    } catch (error) {
      if (status) status.textContent = 'Die Anfrage konnte gerade nicht gesendet werden. Bitte versucht es erneut oder ruft uns kurz an.';
    } finally {
      if (submit) {
        submit.disabled = false;
        submit.removeAttribute('aria-busy');
      }
      if (submitLabel) submitLabel.textContent = submit.getAttribute('data-default-label');
    }
  });
})();

(function () {
  'use strict';

  var body = document.body;
  var root = document.documentElement;
  var header = document.getElementById('header');
  var burger = document.querySelector('.av-burger-menu-main > a');
  var scrollTopLink = document.getElementById('scroll-top-link');
  var cookieNotice = document.querySelector('.avia-cookie-consent');
  var mobileQuery = window.matchMedia('(max-width: 989px)');
  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  var lastScrollY = Math.max(window.scrollY, 0);
  var ticking = false;

  if (!header && !scrollTopLink) return;

  function menuIsOpen() {
    return root.classList.contains('av-burger-overlay-active') ||
      root.classList.contains('av-burger-overlay-active-delayed') ||
      body.classList.contains('av-burger-overlay-active');
  }

  function showHeader() {
    if (body.classList.contains('wg-nav-hidden')) {
      body.classList.remove('wg-nav-hidden');
    }
  }

  function cookieNoticeIsOpen() {
    return cookieNotice && cookieNotice.getAttribute('aria-hidden') === 'false';
  }

  function syncMenuState() {
    var open = menuIsOpen();
    if (burger) {
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
      burger.setAttribute('aria-label', open ? 'Menü schließen' : 'Menü öffnen');
    }
    if (open) showHeader();
  }

  function syncScrollTopLink(y) {
    if (!scrollTopLink) return;
    var visible = y > Math.max(520, window.innerHeight * 0.7) && !cookieNoticeIsOpen();
    scrollTopLink.classList.toggle('wg-scrolltop-visible', visible);
    scrollTopLink.setAttribute('aria-hidden', visible ? 'false' : 'true');
    scrollTopLink.tabIndex = visible ? 0 : -1;
  }

  function updateScrollState() {
    var y = Math.max(window.scrollY, 0);
    var delta = y - lastScrollY;

    if (mobileQuery.matches && header) {
      body.classList.toggle('wg-nav-scrolled', y > 24);

      if (menuIsOpen() || y <= 16 || delta < -3) {
        showHeader();
      } else if (delta > 3 && y > 96) {
        body.classList.add('wg-nav-hidden');
      }
    } else {
      body.classList.remove('wg-nav-hidden', 'wg-nav-scrolled');
    }

    syncScrollTopLink(y);
    lastScrollY = y;
    ticking = false;
  }

  function requestScrollUpdate() {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(updateScrollState);
  }

  if (burger) {
    burger.addEventListener('click', showHeader);
  }

  if (header) {
    header.addEventListener('focusin', showHeader);
  }

  if (scrollTopLink) {
    scrollTopLink.addEventListener('click', function (event) {
      event.preventDefault();
      window.scrollTo({ top: 0, behavior: reducedMotion.matches ? 'auto' : 'smooth' });
    });
  }

  var menuObserver = new MutationObserver(syncMenuState);
  menuObserver.observe(root, { attributes: true, attributeFilter: ['class'] });

  if (cookieNotice) {
    var cookieObserver = new MutationObserver(function () {
      var noticeOpen = cookieNoticeIsOpen();
      if (body.classList.contains('wg-cookie-notice-open') !== noticeOpen) {
        body.classList.toggle('wg-cookie-notice-open', noticeOpen);
      }
      syncScrollTopLink(Math.max(window.scrollY, 0));
    });
    cookieObserver.observe(cookieNotice, { attributes: true, attributeFilter: ['aria-hidden', 'class'] });
    var noticeOpen = cookieNoticeIsOpen();
    if (body.classList.contains('wg-cookie-notice-open') !== noticeOpen) {
      body.classList.toggle('wg-cookie-notice-open', noticeOpen);
    }
  }

  window.addEventListener('scroll', requestScrollUpdate, { passive: true });
  window.addEventListener('resize', requestScrollUpdate);
  if (typeof mobileQuery.addEventListener === 'function') {
    mobileQuery.addEventListener('change', requestScrollUpdate);
  }

  syncMenuState();
  updateScrollState();
})();
