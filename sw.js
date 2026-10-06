// Keep the installable cheat sheet usable offline by caching its page and static assets.
// Navigations try the network first for fresh content; fonts and icons use the cache first.
// Bump this cache name, and an icon's query version when needed, to refresh existing installs.
const CACHE_NAME = 'ep133-cheatsheet-v12';
const APP_SHELL = [
  '/index.html',
  '/manifest.webmanifest',
  '/assets/fonts/inter-latin.woff2',
  '/assets/fonts/space-mono-regular-latin.woff2',
  '/assets/fonts/space-mono-bold-latin.woff2',
  '/assets/fonts/tensegteen/TenSegTeen-Regular.woff2',
  '/assets/fonts/tensegteen/specimen.html',
  '/assets/icons/app-icon.svg?v=4',
  '/assets/icons/app-icon-180.png?v=4',
  '/assets/icons/app-icon-192.png?v=4',
  '/assets/icons/app-icon-512.png?v=4'
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
  const url = new URL(request.url);
  const homePage = url.pathname === '/' || url.pathname === '/index.html';
  const cacheKey = homePage ? '/index.html' : request;
  try {
    const response = await fetch(request);
    if (response.ok) await cache.put(cacheKey, response.clone());
    return response;
  } catch {
    return (await cache.match(cacheKey)) || (await cache.match('/index.html')) || Response.error();
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
