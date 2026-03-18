import math
import random
from locust import HttpUser, task, between, LoadTestShape

class BoutiqueShopper(HttpUser):
    wait_time = between(0.5, 2)

    @task(4)
    def view_home(self):
        self.client.get("/")

    @task(3)
    def browse_product(self):
        self.client.get(random.choice(["/product/0PUK6V6EV0", "/product/1YMWWN1N4O", "/product/2ZYFJ3GM2N", "/product/66VCHSJNUP"]))

    @task(2)
    def view_cart(self):
        self.client.get("/cart")

    @task(1)
    def add_to_cart(self):
        self.client.post("/cart", data={"product_id": "0PUK6V6EV0", "quantity": 1})

class RealisticBiMonthlySaleShape(LoadTestShape):
    PEAK_USERS = 750
    START_DAY = 20 

    def tick(self):
        run_time = self.get_run_time()
        
        # 120 giây thực tế = 1 ngày mô phỏng (24 giờ)
        simulated_day = int(((run_time / 120.0) + self.START_DAY - 1) % 30) + 1
        simulated_hour = (run_time % 120) / 120.0 * 24
        
        is_sale_day = (simulated_day == 1 or simulated_day == 15)

        if is_sale_day:
            # --- NGÀY SALE (1 & 15) ---
            if 0 <= simulated_hour < 8:
                # Đêm đến sáng: Khá vắng
                target_users = self.PEAK_USERS * 0.15
                spawn_rate = 15
            elif (8 <= simulated_hour < 11) or (13 <= simulated_hour < 17):
                # Trong giờ làm việc: Vắng (Lén lướt xem đồ)
                target_users = self.PEAK_USERS * 0.30
                spawn_rate = 20
            elif 11 <= simulated_hour < 13:
                # Giờ nghỉ trưa (Đạt đỉnh 750)
                target_users = self.PEAK_USERS * 1.0
                spawn_rate = 50 
            else: 
                # Cao điểm buổi tối
                target_users = self.PEAK_USERS * 0.85
                spawn_rate = 40
        else:
            # --- NGÀY BÌNH THƯỜNG ---
            if 0 <= simulated_hour < 8:
                # Đêm đến sáng: Khá vắng
                target_users = self.PEAK_USERS * 0.05
                spawn_rate = 5
            elif (8 <= simulated_hour < 11) or (13 <= simulated_hour < 17):
                # Trong giờ làm việc: Vắng
                target_users = self.PEAK_USERS * 0.15
                spawn_rate = 10
            elif 11 <= simulated_hour < 13:
                # Giờ nghỉ trưa: Có tăng nhẹ nhưng không đột biến
                target_users = self.PEAK_USERS * 0.40
                spawn_rate = 20
            else: 
                # Tan làm đến đêm: Cao điểm mua sắm thông thường
                target_users = self.PEAK_USERS * 0.60
                spawn_rate = 30

        # Thêm 10% nhiễu động ngẫu nhiên
        user_count = int(target_users * random.uniform(0.9, 1.1))
        
        return (user_count, spawn_rate)
