from locust import HttpUser, task, between
import random


class StoxlyUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.access_token = None
        resp = self.client.post("/api/v1/auth/login", json={"email": "test@example.com", "password": "TestPass123!"})
        if resp.status_code == 200:
            self.access_token = resp.json().get("access_token")

    @task(3)
    def search_stocks(self):
        symbols = ["TCS", "RELIANCE", "INFY", "HDFCBANK", "ICICIBANK"]
        symbol = random.choice(symbols)
        self.client.get(f"/api/v1/stocks/search/{symbol}")

    @task(2)
    def get_stock_price(self):
        symbols = ["TCS", "RELIANCE", "INFY"]
        symbol = random.choice(symbols)
        self.client.get(f"/api/v1/stocks/{symbol}/price")

    @task(1)
    def market_movers(self):
        self.client.get("/api/v1/stocks/movers")

    @task(1)
    def health_check(self):
        self.client.get("/api/v1/health")

    @task(2)
    def get_sector_performance(self):
        self.client.get("/api/v1/sector-performance")

    @task(2)
    def get_holdings(self):
        if self.access_token:
            self.client.get("/api/v1/portfolio/holdings", headers={"Authorization": f"Bearer {self.access_token}"})

    @task(1)
    def get_chat_suggestions(self):
        self.client.get("/api/v2/suggestions")

    @task(1)
    def get_leaderboard(self):
        self.client.get("/api/v1/paper-trading/leaderboard")
