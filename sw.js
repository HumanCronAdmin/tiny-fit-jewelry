const CACHE = 'tinyfit-v1';
const ASSETS = ['/', '/index.html', '/rings.html', '/bracelets.html', '/database.html', '/css/style.css', '/js/database.js', '/data/brands.json', '/favicon.svg'];
self.addEventListener('install', e => e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS.map(a => new URL(a, self.location).href)))));
self.addEventListener('fetch', e => e.respondWith(caches.match(e.request).then(r => r || fetch(e.request))));
