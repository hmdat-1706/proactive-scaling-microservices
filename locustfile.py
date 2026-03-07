import math
from locust import HttpUser, task, between, LoadTestShape

class BoutiqueShopper(HttpUser):
    wait_time = between(1, 3)

    @task(4)
    def browse_homepage(self):
        self.client.get("/")

    @task(3)
    def browse_product(self):
        # Xem chi tiết một sản phẩm ngẫu nhiên (dùng ID của kính râm)
        self.client.get("/product/0PUK6V6EV0") 

    @task(2)
    def add_to_cart(self):
        self.client.post("/cart", data={"product_id": "0PUK6V6EV0", "quantity": 1})

    @task(1)
    def checkout(self):
        self.client.get("/cart")

class SineWaveShape(LoadTestShape):
    min_users = 10
    max_users = 100 
    time_limit = 3600

    def tick(self):
        run_time = self.get_run_time()
        cycle_length = 300 
        amplitude = (self.max_users - self.min_users) / 2
        mid_point = self.min_users + amplitude
        user_count = int(mid_point + amplitude * math.sin(2 * math.pi * run_time / cycle_length))
        return (user_count, 10)
