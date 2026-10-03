// Rock Marker service worker — keeps the app usable with weak or no signal.
//  - The page: tries the network, but if the signal is weak and it takes
//    more than 4 seconds, opens the saved copy right away (and still saves
//    the new version in the background for next time).
//  - Map and Firebase program files (fixed version numbers): saved once, then
//    loaded from the phone.
//  - Satellite map tiles you have looked at: kept on the phone (up to about
//    2,000 tiles) so fields still show with no signal.
//  - Shared-farm data never goes through here — Firebase keeps its own copy.
var CACHE_NAME = "rock-marker-shell-v6";
var LIB_CACHE = "rock-marker-libs-v1";
var TILE_CACHE = "rock-marker-tiles-v1";
var TILE_MAX = 2000;
var KEEP = [CACHE_NAME, LIB_CACHE, TILE_CACHE];
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
        if(KEEP.indexOf(name) === -1){ return caches.delete(name); }
      }));
    }).then(function(){ return self.clients.claim(); })
  );
});

function isLib(url){
  return url.indexOf("https://cdnjs.cloudflare.com/ajax/libs/leaflet/") === 0 ||
    url.indexOf("https://www.gstatic.com/firebasejs/") === 0;
}
function isTile(url){
  return url.indexOf("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/") === 0;
}
var tilePuts = 0;
function trimTiles(){
  caches.open(TILE_CACHE).then(function(cache){
    cache.keys().then(function(keys){
      var extra = keys.length - TILE_MAX;
      for(var i = 0; i < extra; i++){ cache.delete(keys[i]); }
    });
  });
}

self.addEventListener("fetch", function(event){
  if(event.request.method !== "GET"){ return; }
  var url = event.request.url;

  if(isLib(url)){
    event.respondWith(
      caches.open(LIB_CACHE).then(function(cache){
        return cache.match(event.request).then(function(hit){
          if(hit){ return hit; }
          return fetch(event.request).then(function(response){
            if(response && (response.ok || response.type === "opaque")){ cache.put(event.request, response.clone()); }
            return response;
          });
        });
      })
    );
    return;
  }

  if(isTile(url)){
    event.respondWith(
      fetch(event.request).then(function(response){
        if(response && response.ok && response.type === "cors"){
          var copy = response.clone();
          caches.open(TILE_CACHE).then(function(cache){
            cache.put(event.request, copy);
            if(++tilePuts % 100 === 0){ trimTiles(); }
          });
        }
        return response;
      }).catch(function(){
        return caches.open(TILE_CACHE).then(function(cache){ return cache.match(event.request); });
      })
    );
    return;
  }

  var isSameOrigin = url.indexOf(self.location.origin) === 0;
  if(!isSameOrigin){ return; }

  var isPageRequest = event.request.mode === "navigate" || url.indexOf("index.html") !== -1;

  if(isPageRequest){
    event.respondWith(new Promise(function(resolve){
      var settled = false;
      var network = fetch(event.request).then(function(response){
        if(response && response.ok){
          var copy = response.clone();
          caches.open(CACHE_NAME).then(function(cache){ cache.put(event.request, copy); });
        }
        return response;
      });
      network.then(function(response){
        if(!settled){ settled = true; resolve(response); }
      }).catch(function(){
        caches.match(event.request).then(function(cached){
          if(!settled){ settled = true; resolve(cached || Response.error()); }
        });
      });
      setTimeout(function(){
        if(settled){ return; }
        caches.match(event.request).then(function(cached){
          if(cached && !settled){ settled = true; resolve(cached); }
        });
      }, 4000);
    }));
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
