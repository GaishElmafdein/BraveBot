from tkinter import Canvas
from datetime import datetime
from sklearn.linear_model import LinearRegression
import random

class NicheTrendTracker:
    def __init__(self, mode="mock"):
        """
        mode: "mock" أو "live"
        """
        self.mode = mode

    # =============================
    # 1. سحب الترندات
    # =============================
    def track_trends(self, niche):
        """
        سحب بيانات تريندات الـ niche (Mock أو Live)
        """
        if self.mode == "mock":
            # بيانات تجريبية
            data = {
                "niche": niche,
                "predicted_demand": round(random.uniform(50, 100), 2),
                "social_mentions": random.randint(500, 5000),
                "growth_rate": round(random.uniform(10, 80), 2),
                "last_updated": datetime.now().isoformat()
            }
            return data
        else:
            # هنا هنضيف الكود الحقيقي لاحقاً
            # مثلاً ربط Google Trends API أو TikTok API
            return self._fetch_live_data(niche)

    # =============================
    # 2. تحليل الموسمية
    # =============================
    def analyze_seasonality(self, niche):
        """
        تحديد أشهر الذروة للـ niche
        """
        seasonal_data = {
            "seasonality_score": round(random.uniform(50, 90), 2),
            "peak_months": ["June", "July", "August"],
            "current_month": datetime.now().strftime("%B")
        }
        return seasonal_data

    # =============================
    # 3. التنبؤ المستقبلي
    # =============================
    def predict_future_trend(self, historical_data, days_ahead=7):
        """
        توقع تريندات مستقبلية بناءً على بيانات تاريخية
        """
        model = LinearRegression()
        model.fit(historical_data.index.values.reshape(-1, 1), historical_data["search_volume"])
        future_index = len(historical_data) + days_ahead
        predicted_volume = model.predict([[future_index]])[0]

        return {
            "predicted_search_volume": round(predicted_volume, 2),
            "predicted_sales_volume": round(predicted_volume * 0.6, 2),
            "confidence_score": round(random.uniform(70, 95), 2)
        }

    # =============================
    # 4. حساب الـ Viral Potential
    # =============================
    def calculate_viral_potential(self, product_data):
        """
        حساب نقاط الـ Viral Potential للمنتج
        """
        base_score = product_data.get("current_trend_score", 50)
        social_boost = min(product_data.get("social_mentions", 0) / 100, 30)
        price_factor = 10 if 20 <= product_data.get("price_point", 0) <= 50 else 5
        competition_penalty = -10 if product_data.get("competitor_count", 0) > 5 else 5

        viral_score = base_score + social_boost + price_factor + competition_penalty
        return min(max(viral_score, 0), 100)

    # =============================
    # 5. Placeholder لـ Live Mode
    # =============================
    def _fetch_live_data(self, niche):
        """
        هنا هتحط API حقيقية زي Google Trends أو TikTok
        """
        # مؤقتًا نرجع بيانات شبه حقيقية
        return {
            "niche": niche,
            "predicted_demand": 75.5,
            "social_mentions": 3200,
            "growth_rate": 42.3,
            "last_updated": datetime.now().isoformat()
        }
