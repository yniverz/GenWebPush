// ---------- PUSH NOTIFICATIONS (unchanged) ----------
self.addEventListener("push", event => {
  if (!event.data) return;
  const data = event.data.json();
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: "https://static-00.iconduck.com/assets.00/notification-icon-512x512-0sa5r440.png",
      data: { url: data.navigate }
    })
  );
});

self.addEventListener("notificationclick", event => {
  event.notification.close();
  const url = (event.notification.data && event.notification.data.url) || "/";
  event.waitUntil(
    clients.matchAll({ type: "window", includeUncontrolled: true })
      .then(winClients =>
        winClients.find(win => win.url === url && "focus" in win) ||
        clients.openWindow(url)
      )
  );
});

// ---------- OFFLINE FALLBACK (new) ----------
const CACHE_NAME  = "offline-page-v1";   // bump when you change offline.html
const OFFLINE_URL = "/offline.html";

/* 1.  Install: precache *only* the offline fallback page */
self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.add(OFFLINE_URL))
      .then(() => self.skipWaiting())         // activate immediately
  );
});

/* 2.  Activate: clean up old versions and claim open tabs */
self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(key => key.startsWith("offline-page-") && key !== CACHE_NAME)
          .map(key => caches.delete(key))
      )
    ).then(() => self.clients.claim())
  );
});

/* 3.  Fetch: network-first for navigations, fall back to offline.html */
self.addEventListener("fetch", event => {
  if (event.request.mode === "navigate") {
    event.respondWith(
      fetch(event.request).catch(err => {
        // If the user is *offline*, show the cached fallback;
        // otherwise surface the original error (e.g. bad SSL cert)
        if (!self.navigator.onLine) {
          return caches.match(OFFLINE_URL);
        }
        throw err;        // lets the browser show its SSL error page
      })
    );
  }
});
