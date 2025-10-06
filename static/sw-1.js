const CACHE_NAME = 'flask-pwa-v9';
const OFFLINE_URL = '/offline';

self.addEventListener('install', (event) => {
  console.log('[SW] Installing and caching offline page…');
  event.waitUntil(
    caches.open(CACHE_NAME).then(async (cache) => {
      try {
        // Pre-fetch and cache the rendered offline page
        const offlineResponse = await fetch(OFFLINE_URL);
        await cache.put(OFFLINE_URL, offlineResponse.clone());

        // Cache essential assets
        await cache.addAll([
          '/',
          '/aboutme',
          '/contact',          
          '/static/css/mdb.min.css',
          '/static/css/style.css',
          '/static/css/pygments.css',
          '/static/js/mdb.umd.min.js',          
          '/static/manifest.json',
          '/static/icons/icon-192x192.png',
          '/static/icons/icon-512x512.png'
        ]);
      } catch (err) {
        console.error('[SW] Failed to cache offline page:', err);
      }
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activated');
  event.waitUntil(
    caches.keys().then((keyList) =>
      Promise.all(keyList.map((key) => {
        if (key !== CACHE_NAME) {
          console.log('Service Worker: Removing old cache', key);
          return caches.delete(key);
        }
      }))
    )
  );
  self.skipWaiting();
  return self.clients.claim();
});

self.addEventListener('fetch', (event) => {

  if (event.request.method !== 'GET') return;

  if (event.request.mode === 'navigate') {
    // Handle navigation requests (HTML pages)
    event.respondWith(
      fetch(event.request).catch(() => {
        return caches.match(event.request)
          .then((response) => response || caches.match(OFFLINE_URL));
      })
    );
  } else {
    // Handle static files
    event.respondWith(
      caches.match(event.request).then((response) => {
        return response || fetch(event.request).then((res) => {
          return caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, res.clone());
            return res;
          });
        });
      }).catch(() => {
        // optional: return fallback image or nothing
      })
    );
  }
});
