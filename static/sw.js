// Service Worker for BhashaAI PWA with Keep-Alive
const CACHE_NAME = 'bhashaai-v1';
const STATIC_CACHE_URLS = [
  '/',
  '/static/manifest.json',
  '/static/icon-192.png',
  '/static/icon-512.png',
  '/static/pwa-guide/android-guide.html',
  '/static/pwa-guide/ios-guide.html',
  '/static/pwa-guide/desktop-guide.html'
];

// Keep-alive configuration
const KEEP_ALIVE_INTERVAL = 20 * 60 * 1000; // 20 minutes
let keepAliveTimer;

// Install Service Worker
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('BhashaAI: Caching static assets');
        return cache.addAll(STATIC_CACHE_URLS);
      })
      .catch((error) => {
        console.log('BhashaAI: Cache installation failed:', error);
      })
  );
  
  // Start keep-alive mechanism
  startKeepAlive();
});

// Keep-alive function
function startKeepAlive() {
  if (keepAliveTimer) {
    clearInterval(keepAliveTimer);
  }
  
  keepAliveTimer = setInterval(() => {
    // Send a lightweight request to keep the app alive
    fetch('/', {
      method: 'HEAD',
      cache: 'no-cache'
    }).then(() => {
      console.log('SW: Keep-alive ping sent');
    }).catch(err => {
      console.log('SW: Keep-alive failed:', err);
    });
  }, KEEP_ALIVE_INTERVAL);
  
  console.log('SW: Keep-alive mechanism started');
}

// Activate Service Worker
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('BhashaAI: Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Fetch Strategy: Network First, then Cache
self.addEventListener('fetch', (event) => {
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // If successful, clone and cache the response
        if (response.status === 200) {
          const responseClone = response.clone();
          caches.open(CACHE_NAME)
            .then((cache) => {
              cache.put(event.request, responseClone);
            });
        }
        return response;
      })
      .catch(() => {
        // If network fails, try to serve from cache
        return caches.match(event.request)
          .then((response) => {
            if (response) {
              return response;
            }
            // If not in cache, return offline page
            if (event.request.destination === 'document') {
              return caches.match('/');
            }
          });
      })
  );
});

// Background Sync (for future use)
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    console.log('BhashaAI: Background sync event triggered');
    // Handle background sync here
  }
});

// Push Notifications (for future use)
self.addEventListener('push', (event) => {
  const options = {
    body: event.data ? event.data.text() : 'New update from BhashaAI!',
    icon: '/static/icon-192.png',
    badge: '/static/icon-192.png',
    vibrate: [200, 100, 200],
    tag: 'bhashaai-notification',
    actions: [
      {
        action: 'open',
        title: 'Open BhashaAI',
        icon: '/static/icon-192.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('BhashaAI', options)
  );
});

// Notification Click Handler
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  if (event.action === 'open') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});
