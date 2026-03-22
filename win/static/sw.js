var CACHE = 'mystic-v1';
var PRECACHE = ['/', '/static/index.html'];

self.addEventListener('install', function(e) {
  e.waitUntil(
    caches.open(CACHE).then(function(cache) {
      return cache.addAll(PRECACHE);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', function(e) {
  e.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', function(e) {
  var url = new URL(e.request.url);

  // API 请求：先返回缓存，后台更新
  if (url.pathname.startsWith('/api/')) {
    e.respondWith(
      caches.open(CACHE).then(function(cache) {
        return cache.match(e.request).then(function(cached) {
          var fetchPromise = fetch(e.request).then(function(response) {
            cache.put(e.request, response.clone());
            return response;
          }).catch(function() {
            return cached;
          });
          return cached || fetchPromise;
        });
      })
    );
    return;
  }

  // 页面请求：缓存优先
  e.respondWith(
    caches.match(e.request).then(function(cached) {
      return cached || fetch(e.request).then(function(response) {
        return caches.open(CACHE).then(function(cache) {
          cache.put(e.request, response.clone());
          return response;
        });
      });
    })
  );
});
