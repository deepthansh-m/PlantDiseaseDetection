const CACHE_NAME = 'plant-disease-detection-cache';
const urlsToCache = [
    '/',
    '/static/css/styles.css',
    '/static/js/main.js',
    '/static/audio/output.mp3'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                return cache.addAll(urlsToCache);
            })
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                return response || fetch(event.request);
            })
    );
});
