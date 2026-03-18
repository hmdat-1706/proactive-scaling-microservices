import random
from locust import HttpUser, task, between

class BoutiqueShopper(HttpUser):
    # Giữ nguyên thời gian "suy nghĩ" của user như kịch bản gốc
    wait_time = between(0.5, 2)

    # Tỷ lệ hành vi giống hệt kịch bản thật để đảm bảo tính chính xác khi debug
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
