// Rock Marker service worker — caches the app shell so the app opens and
// stays usable with weak or no signal. Map tiles, search, and shared-map
// sync all go straight to the network (they're never cached here).
var CACHE_NAME = "rock-marker-shell-v5";
var SHELL_FILES = [
  "./",
  "./index.html",
  "./manifest.json",
  "./icon-192.png",
  "./icon-512.png",
  "./icon-512-maskable.png",
  "./apple-touch-icon.png",
  "./favicon-32.png"
];

self.addEventListener("install", function(event){
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache){ return cache.addAll(SHELL_FILES); })
      .then(function(){ return self.skipWaiting(); })
  );
});

self.addEventListener("activate", function(event){
  event.waitUntil(
    caches.keys().then(function(names){
      return Promise.all(names.map(function(name){
        if(name !== CACHE_NAME){ return caches.delete(name); }
      }));
    }).then(function(){ return self.clients.claim(); })
  );
});

self.addEventListener("fetch", function(event){
  if(event.request.method !== "GET"){ return; }
  var isSameOrigin = event.request.url.indexOf(self.location.origin) === 0;
  if(!isSameOrigin){ return; } // let map tiles / geocoding / shared-map sync pass through untouched

  // The HTML shell (the page itself) always tries the network first, so a new
  // deploy shows up the moment you reload — falling back to the cached copy
  // only when there's no signal. Other shell assets (icons, manifest) keep the
  // old cache-first-with-background-refresh behavior since they rarely change.
  var isPageRequest = event.request.mode === "navigate" ||
    event.request.url.indexOf("index.html") !== -1;

  if(isPageRequest){
    event.respondWith(
      fetch(event.request).then(function(response){
        if(response && response.ok){
          var copy = response.clone();
          caches.open(CACHE_NAME).then(function(cache){ cache.put(event.request, copy); });
        }
        return response;
      }).catch(function(){ return caches.match(event.request); })
    );
    return;
  }

  event.respondWith(
    caches.match(event.request).then(function(cached){
      var networkFetch = fetch(event.request).then(function(response){
        if(response && response.ok){
          var copy = response.clone();
          caches.open(CACHE_NAME).then(function(cache){ cache.put(event.request, copy); });
        }
        return response;
      }).catch(function(){ return cached; });
      return cached || networkFetch;
    })
  );
});
