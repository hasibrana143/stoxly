var CACHE_NAME = 'stoxly-cache-v2';
var PRECACHE_URLS = ['/', '/login', '/register'];

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll(PRECACHE_URLS);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames
          .filter(function(name) { return name !== CACHE_NAME; })
          .map(function(name) { return caches.delete(name); })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', function(event) {
  var request = event.request;
  if (request.method !== 'GET') return;
  if (request.url.indexOf('chrome-extension://') === 0) return;
  if (request.url.indexOf('http') !== 0) return;
  if (request.url.indexOf('/api/') !== -1) return;
  if (request.url.indexOf('/ws/') !== -1) return;
  event.respondWith(
    caches.match(request).then(function(cached) {
      var fetchPromise = fetch(request).then(function(response) {
        if (response.status === 200) {
          try {
            var clone = response.clone();
            caches.open(CACHE_NAME).then(function(cache) {
              cache.put(request, clone);
            });
          } catch (e) {
            console.error('SW cache put failed', e);
          }
        }
        return response;
      }).catch(function() {
        return cached;
      });
      return cached || fetchPromise;
    })
  );
});
