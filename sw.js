// Bump this and the asset query version when changing a cached icon in place.
const CACHE_NAME = 'ep133-cheatsheet-v3';
const APP_SHELL = [
  '/index.html',
  '/manifest.webmanifest',
  '/assets/fonts/inter-latin.woff2',
  '/assets/fonts/space-mono-regular-latin.woff2',
  '/assets/fonts/space-mono-bold-latin.woff2',
  '/assets/icons/app-icon.svg?v=3',
  '/assets/icons/app-icon-180.png?v=3',
  '/assets/icons/app-icon-192.png?v=3',
  '/assets/icons/app-icon-512.png?v=3'
];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(APP_SHELL)));
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    Promise.all([
      caches.keys().then(names => Promise.all(
        names.filter(name => name !== CACHE_NAME).map(name => caches.delete(name))
      )),
      self.clients.claim()
    ])
  );
});

async function networkFirstPage(request) {
  const cache = await caches.open(CACHE_NAME);
  try {
    const response = await fetch(request);
    if (response.ok) await cache.put('/index.html', response.clone());
    return response;
  } catch {
    return (await cache.match('/index.html')) || Response.error();
  }
}

async function cachedAsset(request) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);
  if (cached) return cached;
  const response = await fetch(request);
  if (response.ok) await cache.put(request, response.clone());
  return response;
}

self.addEventListener('fetch', event => {
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== 'GET' || url.origin !== self.location.origin) return;
  event.respondWith(
    request.mode === 'navigate' ? networkFirstPage(request) : cachedAsset(request)
  );
});
