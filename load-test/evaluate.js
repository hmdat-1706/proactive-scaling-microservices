import http from 'k6/http';
import { check } from 'k6';
import { randomItem } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

export const options = {
    scenarios: {
        proactive_test: {
            executor: 'ramping-arrival-rate',
            startRate: 10,       // Bắt đầu với 10 RPS
            timeUnit: '1s',
            preAllocatedVUs: 50, // Chuẩn bị sẵn VU để đảm bảo bơm đủ RPS
            maxVUs: 500,
            stages: [
                { target: 80, duration: '15m' }, // Ramp up từ 10 lên 80 RPS trong đúng 15 phút
                { target: 80, duration: '5m' },  // Giữ vững ở mức 80 RPS trong 5 phút
                { target: 10, duration: '5m' },  // Ramp down trở về 10 RPS trong 5 phút
            ],
        },
    },
    thresholds: {
        http_req_duration: ['p(95)<500'], // Cảnh báo nếu 95% requests chậm hơn 500ms
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
        // 40% Traffic: User vào trang chủ
        res = http.get(`${BASE_URL}/`);
    } else if (rand < 0.8) {
        // 40% Traffic: User vào xem sản phẩm cụ thể
        res = http.get(`${BASE_URL}/product/${randomItem(PRODUCT_IDS)}`);
    } else {
        // 20% Traffic: User thêm hàng vào giỏ (gây tải DB/Redis)
        const payload = { product_id: randomItem(PRODUCT_IDS), quantity: 1 };
        res = http.post(`${BASE_URL}/cart`, payload);
    }

    check(res, {
        'status is 200 or 302': (r) => r.status === 200 || r.status === 302,
    });
}
