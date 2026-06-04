// DesiBazaar Service Worker v1.0
const CACHE_NAME = 'desibazaar-v1';
const STATIC_ASSETS = [
  '/',
  '/products/',
  '/deals/',
  '/static/css/style.css',
  '/static/js/main.js',
];

// Install — cache static assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(STATIC_ASSETS).catch(() => {});
    })
  );
  self.skipWaiting();
});

// Activate — clean old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Fetch — network-first with cache fallback
self.addEventListener('fetch', event => {
  // Skip non-GET, API calls, admin
  if (event.request.method !== 'GET') return;
  const url = new URL(event.request.url);
  if (url.pathname.startsWith('/admin/') ||
      url.pathname.startsWith('/api/') ||
      url.pathname.startsWith('/cart/') ||
      url.pathname.startsWith('/checkout/') ||
      url.pathname.startsWith('/orders/')) return;

  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Cache successful responses for static assets
        if (response.ok && (
          url.pathname.startsWith('/static/') ||
          url.hostname.includes('cdn.jsdelivr.net') ||
          url.hostname.includes('fonts.googleapis.com')
        )) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        }
        return response;
      })
      .catch(() => {
        // Fallback to cache
        return caches.match(event.request).then(cached => {
          return cached || caches.match('/');
        });
      })
  );
});
