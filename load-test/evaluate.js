import http from 'k6/http';
import { check, sleep } from 'k6';
import { randomItem } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';
import { Counter } from 'k6/metrics';

const error500 = new Counter('error_500');
const error502 = new Counter('error_502');
const error503 = new Counter('error_503');
const error504 = new Counter('error_504');
const error_timeout = new Counter('error_timeout');


export const options = {
    scenarios: {
        proactive_test: {
            executor: 'ramping-vus',
            startVUs: 10,
            stages: [
                { target: 100, duration: '10s' },         // Baseline
                { target: 2000, duration: '15s' },        // Ramp up to peak
                { target: 2000, duration: '3m' },         // Hold at peak
                { target: 10, duration: '30s' },          // Ramp down
            ],
        },
    },
    thresholds: {
        http_req_duration: ['p(95)<2000'],
    },
};

const BASE_URL = __ENV.BASE_URL || 'http://web.local';

const PRODUCT_IDS = [
    "0PUK6V6EV0", "1YMWWN1N4O", "2ZYFJ3GM2N", "66VCHSJNUP", "9SIQT8TOJO"
];

export default function () {
    const rand = Math.random();
    let res;

    const params = { timeout: '30s' };

    if (rand < 0.4) {
        // 40% Traffic: View home page
        res = http.get(`${BASE_URL}/`, params);
    } else if (rand < 0.8) {
        // 40% Traffic: View specific product
        res = http.get(`${BASE_URL}/product/${randomItem(PRODUCT_IDS)}`, params);
    } else {
        // 20% Traffic: Add to cart (triggers DB/Redis load)
        const payload = { product_id: randomItem(PRODUCT_IDS), quantity: 1 };
        res = http.post(`${BASE_URL}/cart`, payload, params);

    if (res.status === 0) error_timeout.add(1);
    else if (res.status === 500) error500.add(1);
    else if (res.status === 502) error502.add(1);
    else if (res.status === 503) error503.add(1);
    else if (res.status === 504) error504.add(1);

    check(res, {
        'status is 200 or 302': (r) => r.status === 200 || r.status === 302,
    });

    sleep(7.5);
}
