/* Aufräum-Worker des Neuaufbaus: alte Caches löschen und sich selbst
   abmelden. Browser mit dem früheren Service Worker holen dieses Update,
   entfernen alle wg-Caches und laden künftig direkt vom Netz. */
self.addEventListener('install', function () { self.skipWaiting(); });
self.addEventListener('activate', function (event) {
  event.waitUntil(
    caches.keys()
      .then(function (keys) { return Promise.all(keys.map(function (k) { return caches.delete(k); })); })
      .then(function () { return self.registration.unregister(); })
      .then(function () { return self.clients.matchAll(); })
      .then(function (clients) { clients.forEach(function (c) { c.navigate(c.url); }); })
  );
});
