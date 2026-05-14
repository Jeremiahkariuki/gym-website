const CACHE_NAME = 'gymflow-v1';
const ASSETS_TO_CACHE = [
    '/',
    '/portal/',
    '/portal/id-card/',
    '/static/manifest.json',
    '/static/icons/icon-512.png',
    '/static/js/qrcode.min.js',
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS_TO_CACHE);
        })
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request).then((fetchResponse) => {
                // Optionally cache new successful requests
                if (event.request.url.includes('/static/') || event.request.url.includes('/portal/id-card/')) {
                    return caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, fetchResponse.clone());
                        return fetchResponse;
                    });
                }
                return fetchResponse;
            });
        }).catch(() => {
            // Fallback if offline and not in cache
            if (event.request.mode === 'navigate') {
                return caches.match('/portal/id-card/');
            }
        })
    );
});
