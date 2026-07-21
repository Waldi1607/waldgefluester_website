/* Waldgeflüster Service Worker
   Strategie:
   - HTML-Seiten + events.json: network-first (Inhalte immer aktuell, offline-Fallback aus Cache)
   - Statische Assets (CSS/JS/Bilder/Fonts): stale-while-revalidate (sofort aus dem Cache,
     Aktualisierung im Hintergrund) — umgeht die 10-Minuten-Cache-Grenze von GitHub Pages */
const CACHE = "wg-static-v18";
const PRECACHE = [
  "assets/css/bundle.css",
  "assets/css/pages.css?v=25",
  "assets/js/site.js?v=6",
  "assets/js/events.js",
  "wp-includes/js/jquery/jquery.min.js",
  "wp-content/themes/enfold/js/avia-js.min.js",
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(PRECACHE)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return; // externe Hosts (GTM, Fonts) nicht anfassen

  const isHTML = req.mode === "navigate" || url.pathname.endsWith(".html");
  const isData = url.pathname.endsWith("events.json");

  if (isHTML || isData) {
    // network-first
    e.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy));
          return res;
        })
        .catch(() => caches.match(req))
    );
    return;
  }

  // stale-while-revalidate für statische Assets
  e.respondWith(
    caches.match(req).then((cached) => {
      const update = fetch(req)
        .then((res) => {
          if (res && res.status === 200) {
            const copy = res.clone();
            caches.open(CACHE).then((c) => c.put(req, copy));
          }
          return res;
        })
        .catch(() => cached);
      return cached || update;
    })
  );
});
