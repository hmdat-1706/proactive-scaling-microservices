import http from 'k6/http';
import { check } from 'k6';
import { randomItem } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

const TARGET_RPS = __ENV.TARGET_RPS ? parseInt(__ENV.TARGET_RPS) : 80;

export const options = {
    scenarios: {
        proactive_test: {
            executor: 'ramping-arrival-rate',
            startRate: 10,       // Start at 10 RPS
            timeUnit: '1s',
            preAllocatedVUs: 50, // Pre-allocate VUs to ensure accurate RPS
            maxVUs: 2000,        // Increased maxVUs in case TARGET_RPS is very high (like 300+)
            stages: [
                { target: 30, duration: '2m' },          // Baseline normal traffic
                { target: TARGET_RPS, duration: '2m' },  // SUDDEN SPIKE (Flash sale/Event) in 2 minute
                { target: TARGET_RPS, duration: '5m' },  // Hold steady at peak traffic for 5 minutes
                { target: 10, duration: '1m' },          // Ramp down quickly
            ],
        },
    },
    thresholds: {
        http_req_duration: ['p(95)<500'], // Alert if 95% of requests are slower than 500ms
    },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost';

const PRODUCT_IDS = [
    "0PUK6V6EV0", "1YMWWN1N4O", "2ZYFJ3GM2N", "66VCHSJNUP", "9SIQT8TOJO"
];

export default function () {
    const rand = Math.random();
    let res;

    if (rand < 0.4) {
        // 40% Traffic: View home page
        res = http.get(`${BASE_URL}/`);
    } else if (rand < 0.8) {
        // 40% Traffic: View specific product
        res = http.get(`${BASE_URL}/product/${randomItem(PRODUCT_IDS)}`);
    } else {
        // 20% Traffic: Add to cart (triggers DB/Redis load)
        const payload = JSON.stringify({ product_id: randomItem(PRODUCT_IDS), quantity: 1 });
        res = http.post(`${BASE_URL}/cart`, payload, { headers: { 'Content-Type': 'application/json' } });
    }

    check(res, {
        'status is 200 or 302': (r) => r.status === 200 || r.status === 302,
    });
}
