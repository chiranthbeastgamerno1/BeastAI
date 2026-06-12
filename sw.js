self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('fetch', (event) => {
  // Simple pass-through fetch for the PWA requirement
  event.respondWith(fetch(event.request).catch(() => new Response("Offline")));
});