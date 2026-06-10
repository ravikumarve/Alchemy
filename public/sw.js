// This service worker provides offline functionality for the ALCHEMY dashboard
const CACHE_NAME = 'alchemy-dashboard-v1'
const STATIC_CACHE_NAME = 'alchemy-static-v1'
const DYNAMIC_CACHE_NAME = 'alchemy-dynamic-v1'

// Assets to cache for offline functionality
const STATIC_ASSETS = [
  '/',
  '/dashboard',
  '/packages',
  '/api/v1/jobs',
  '/api/v1/packages',
  '/static/js/bundle.js',
  '/static/css/app.css',
]

// Install event - cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE_NAME)
      .then((cache) => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting())
  )
})

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((cacheName) => {
              return cacheName !== STATIC_CACHE_NAME &&
                     cacheName !== DYNAMIC_CACHE_NAME
            })
            .map((cacheName) => {
              return caches.delete(cacheName)
            })
        )
      })
      .then(() => self.clients.claim())
  )
})

// Fetch event - serve cached content when offline
self.addEventListener('fetch', (event) => {
  const request = event.request
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return
  }
  
  // Skip external requests
  if (!request.url.startsWith(self.location.origin)) {
    return
  }
  
  event.respondWith(
    caches.open(DYNAMIC_CACHE_NAME)
      .then((cache) => {
        return cache.match(request)
          .then((response) => {
            if (response) {
              return response
            }
            
            // If not in cache, fetch from network
            return fetch(request)
              .then((response) => {
                // Check if valid response
                if (!response || response.status !== 200 || response.type !== 'basic') {
                  return response
                }
                
                // Clone the response
                const responseClone = response.clone()
                
                // Cache the response for future use
                cache.put(request, responseClone)
                
                return response
              })
              .catch(() => {
                // If network fails, try to serve from static cache
                return caches.open(STATIC_CACHE_NAME)
                  .then((staticCache) => {
                    return staticCache.match('/')
                  })
              })
          })
      })
  )
})