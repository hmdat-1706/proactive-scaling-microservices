import http from 'k6/http';
import { check, sleep } from 'k6';
import { randomItem } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

const TARGET_RPS = __ENV.TARGET_RPS ? parseInt(__ENV.TARGET_RPS) : 80;

export const options = {
    scenarios: {
        proactive_test: {
            executor: 'ramping-vus',
            startVUs: 10,
            stages: [
                { target: 100, duration: '1m' },          // Baseline normal traffic
                { target: 1000, duration: '2m' },         // Spike to 1000 Concurrent Users
                { target: 1000, duration: '3m' },         // Hold at peak
                { target: 10, duration: '1m' },           // Ramp down
            ],
        },
    },
    thresholds: {
        http_req_duration: ['p(95)<2000'], // Nới lỏng timeout vì 1000 user sẽ tạo hàng đợi
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
    
    // YẾU TỐ QUYẾT ĐỊNH: Think Time (Thời gian user đọc trang web)
    // 1000 users / 10s = ~100 RPS thực tế. Không làm sập máy ảo 8-Core.
    sleep(10);
}
