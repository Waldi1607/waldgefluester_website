/* Waldgeflüster – Messpunkte für Google Tag Manager.
   Schiebt Events in den dataLayer; im GTM werden daraus GA4-Events/Conversions.
   Kein Tracking ohne Consent: GA4 wertet die Events erst aus, wenn der
   Cookie-Banner analytics_storage auf 'granted' gesetzt hat (Consent Mode v2). */
(function () {
  window.dataLayer = window.dataLayer || [];
  var push = function (name, params) {
    var data = { event: name, seite: location.pathname };
    for (var k in params) if (params.hasOwnProperty(k)) data[k] = params[k];
    window.dataLayer.push(data);
  };
  window.wgTrack = push;

  document.addEventListener('click', function (e) {
    var t = e.target.closest ? e.target : null;
    if (!t) return;
    var a = t.closest('a');
    if (!a) return;
    var href = a.getAttribute('href') || '';

    if (href.indexOf('tel:') === 0) {
      push('telefon_klick', { telefonnummer: href.replace('tel:', '') });
    } else if (href.indexOf('mailto:') === 0) {
      push('email_klick', { adresse: href.replace('mailto:', '').split('?')[0] });
    } else if (a.closest('#wg-event-banner')) {
      push('termin_banner_klick', {});
    } else if (href.indexOf('instagram.com') > -1) {
      push('instagram_klick', {});
    } else if (a.closest('.av-menu-button') || /#kontakt$/.test(href)) {
      push('anfrage_button_klick', { position: a.closest('#header') ? 'header' : 'inhalt' });
    }
  }, true);

  // Virtuelle 3D-Tour: sichtbar geworden = angeschaut
  var tour = document.querySelector('iframe[src*="Panotour"]');
  if (tour && 'IntersectionObserver' in window) {
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { push('tour_3d_angesehen', {}); obs.disconnect(); }
      });
    }, { threshold: 0.5 });
    obs.observe(tour);
  }

  // Formular angefangen (erste Eingabe) – zeigt Abbruchquote zwischen Start und Absenden
  var started = false;
  document.addEventListener('input', function (e) {
    if (started) return;
    var form = e.target.closest ? e.target.closest('form.avia_ajax_form') : null;
    if (!form) return;
    started = true;
    push('formular_begonnen', {});
  }, true);
})();
