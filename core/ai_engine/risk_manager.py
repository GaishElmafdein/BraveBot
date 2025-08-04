import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

@dataclass
class RiskAssessment:
    """⚠️ تقييم المخاطر"""
    product_name: str
    overall_risk_score: float
    risk_level: str
    risk_factors: List[str]
    mitigation_strategies: List[str]
    max_investment: float
    stop_loss_price: float
    confidence_interval: Tuple[float, float]

class RiskManager:
    """🛡️ مدير المخاطر المتقدم"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # أوزان عوامل المخاطر
        self.risk_weights = {
            'price_volatility': 0.25,
            'competition_level': 0.20,
            'market_demand': 0.20,
            'seasonality': 0.15,
            'supplier_reliability': 0.10,
            'regulatory_risk': 0.10
        }
        
        # حدود المخاطر
        self.risk_thresholds = {
            'low': 30,
            'medium': 60,
            'high': 100
        }
    
    def assess_product_risk(self, 
                           product_name: str,
                           amazon_price: float,
                           ebay_price: float,
                           trend_data: Dict = None,
                           market_data: Dict = None) -> RiskAssessment:
        """🎯 تقييم مخاطر المنتج الشامل"""
        
        risk_factors = []
        risk_scores = {}
        
        # تحليل تقلبات الأسعار
        price_volatility = self._assess_price_volatility(amazon_price, ebay_price)
        risk_scores['price_volatility'] = price_volatility
        if price_volatility > 70:
            risk_factors.append(f"⚠️ High price volatility ({price_volatility:.1f}%)")
        
        # تحليل مستوى المنافسة
        competition_risk = self._assess_competition_risk(product_name, market_data)
        risk_scores['competition_level'] = competition_risk
        if competition_risk > 60:
            risk_factors.append(f"🥊 High competition level ({competition_risk:.1f}%)")
        
        # تحليل طلب السوق
        demand_risk = self._assess_demand_risk(trend_data)
        risk_scores['market_demand'] = demand_risk
        if demand_risk > 50:
            risk_factors.append(f"📉 Market demand concerns ({demand_risk:.1f}%)")
        
        # تحليل المخاطر الموسمية
        seasonal_risk = self._assess_seasonal_risk(product_name)
        risk_scores['seasonality'] = seasonal_risk
        if seasonal_risk > 40:
            risk_factors.append(f"📅 Seasonal dependency ({seasonal_risk:.1f}%)")
        
        # تحليل موثوقية المورد
        supplier_risk = self._assess_supplier_risk(amazon_price)
        risk_scores['supplier_reliability'] = supplier_risk
        if supplier_risk > 30:
            risk_factors.append(f"🏪 Supplier reliability concerns ({supplier_risk:.1f}%)")
        
        # المخاطر التنظيمية
        regulatory_risk = self._assess_regulatory_risk(product_name)
        risk_scores['regulatory_risk'] = regulatory_risk
        if regulatory_risk > 25:
            risk_factors.append(f"📋 Regulatory compliance risk ({regulatory_risk:.1f}%)")
        
        # حساب النقاط الإجمالية للمخاطر
        overall_risk = sum(score * self.risk_weights[factor] 
                          for factor, score in risk_scores.items())
        
        # تحديد مستوى المخاطر
        risk_level = self._determine_risk_level(overall_risk)
        
        # استراتيجيات التخفيف
        mitigation_strategies = self._generate_mitigation_strategies(risk_factors, risk_level)
        
        # حساب الحد الأقصى للاستثمار
        max_investment = self._calculate_max_investment(amazon_price, overall_risk)
        
        # حساب سعر وقف الخسارة
        stop_loss = self._calculate_stop_loss(ebay_price, overall_risk)
        
        # فترة الثقة
        confidence_interval = self._calculate_confidence_interval(ebay_price, overall_risk)
        
        return RiskAssessment(
            product_name=product_name,
            overall_risk_score=overall_risk,
            risk_level=risk_level,
            risk_factors=risk_factors,
            mitigation_strategies=mitigation_strategies,
            max_investment=max_investment,
            stop_loss_price=stop_loss,
            confidence_interval=confidence_interval
        )
    
    def _assess_price_volatility(self, amazon_price: float, ebay_price: float) -> float:
        """💹 تقييم تقلبات الأسعار"""
        price_difference = abs(ebay_price - amazon_price)
        volatility_ratio = price_difference / amazon_price
        
        # تحويل إلى نقاط مخاطر (0-100)
        volatility_score = min(volatility_ratio * 50, 100)
        
        return volatility_score
    
    def _assess_competition_risk(self, product_name: str, market_data: Dict = None) -> float:
        """🥊 تقييم مخاطر المنافسة"""
        product_lower = product_name.lower()
        base_risk = 30  # مخاطر أساسية
        
        # منتجات عالية المنافسة
        high_competition_products = [
            'phone case', 'charger', 'cable', 'earbuds', 
            'bluetooth speaker', 'power bank'
        ]
        
        if any(product in product_lower for product in high_competition_products):
            base_risk += 40
        
        # منتجات متوسطة المنافسة
        medium_competition_products = [
            'gaming', 'fitness', 'home decor', 'kitchen'
        ]
        
        if any(product in product_lower for product in medium_competition_products):
            base_risk += 20
        
        # تعديل حسب بيانات السوق
        if market_data and 'competition_level' in market_data:
            competition_level = market_data['competition_level']
            if competition_level == 'High':
                base_risk += 25
            elif competition_level == 'Medium':
                base_risk += 10
        
        return min(base_risk, 100)
    
    def _assess_demand_risk(self, trend_data: Dict = None) -> float:
        """📈 تقييم مخاطر الطلب"""
        if not trend_data:
            return 50  # مخاطر متوسطة إذا لم تتوفر البيانات
        
        trend_score = trend_data.get('trend_score', 50)
        growth_rate = trend_data.get('growth_rate', 0)
        
        # حساب مخاطر الطلب عكسياً (ترند عالي = مخاطر أقل)
        demand_risk = max(0, 100 - trend_score)
        
        # تعديل حسب معدل النمو
        if growth_rate < -20:  # نمو سلبي قوي
            demand_risk += 30
        elif growth_rate < 0:  # نمو سلبي
            demand_risk += 15
        elif growth_rate > 50:  # نمو قوي جداً قد يكون غير مستدام
            demand_risk += 10
        
        return min(demand_risk, 100)
    
    def _assess_seasonal_risk(self, product_name: str) -> float:
        """📅 تقييم المخاطر الموسمية"""
        current_month = datetime.now().month
        product_lower = product_name.lower()
        
        seasonal_risk = 10  # مخاطر أساسية منخفضة
        
        # منتجات موسمية قوية
        seasonal_products = {
            'christmas': (['gift', 'decoration', 'tree', 'lights'], [11, 12]),
            'summer': (['outdoor', 'swimming', 'beach', 'camping'], [5, 6, 7, 8]),
            'winter': (['heating', 'warm', 'coat', 'blanket'], [12, 1, 2]),
            'back_to_school': (['school', 'student', 'backpack', 'laptop'], [7, 8, 9])
        }
        
        for season, (keywords, peak_months) in seasonal_products.items():
            if any(keyword in product_lower for keyword in keywords):
                if current_month in peak_months:
                    seasonal_risk += 5  # في الموسم = مخاطر أقل
                else:
                    seasonal_risk += 50  # خارج الموسم = مخاطر عالية
                break
        
        return min(seasonal_risk, 100)
    
    def _assess_supplier_risk(self, amazon_price: float) -> float:
        """🏪 تقييم مخاطر المورد"""
        base_risk = 15
        
        # المنتجات الرخيصة جداً مشبوهة
        if amazon_price < 5:
            base_risk += 40
        elif amazon_price < 10:
            base_risk += 20
        
        # المنتجات الغالية جداً قد تكون مخاطرة
        elif amazon_price > 200:
            base_risk += 25
        elif amazon_price > 100:
            base_risk += 10
        
        return min(base_risk, 100)
    
    def _assess_regulatory_risk(self, product_name: str) -> float:
        """📋 تقييم المخاطر التنظيمية"""
        product_lower = product_name.lower()
        base_risk = 5
        
        # منتجات عالية المخاطر التنظيمية
        high_risk_categories = [
            'electronics', 'battery', 'charger', 'medical', 
            'health', 'food', 'cosmetic', 'toy'
        ]
        
        if any(category in product_lower for category in high_risk_categories):
            base_risk += 25
        
        # منتجات متوسطة المخاطر
        medium_risk_categories = [
            'automotive', 'jewelry', 'clothing'
        ]
        
        if any(category in product_lower for category in medium_risk_categories):
            base_risk += 15
        
        return min(base_risk, 100)
    
    def _determine_risk_level(self, overall_risk: float) -> str:
        """🎯 تحديد مستوى المخاطر"""
        if overall_risk <= self.risk_thresholds['low']:
            return 'Low'
        elif overall_risk <= self.risk_thresholds['medium']:
            return 'Medium'
        else:
            return 'High'
    
    def _generate_mitigation_strategies(self, risk_factors: List[str], risk_level: str) -> List[str]:
        """💡 توليد استراتيجيات التخفيف"""
        strategies = []
        
        # استراتيجيات عامة حسب مستوى المخاطر
        if risk_level == 'High':
            strategies.extend([
                "🚨 Consider avoiding this product due to high risk",
                "💰 If proceeding, limit investment to minimum amount",
                "⏰ Set strict stop-loss limits",
                "📊 Monitor daily for 1-2 weeks before scaling"
            ])
        elif risk_level == 'Medium':
            strategies.extend([
                "⚠️ Proceed with caution and close monitoring",
                "💵 Start with small test quantity (1-3 units)",
                "📈 Scale gradually based on performance",
                "🎯 Set clear profit targets and exit strategy"
            ])
        else:  # Low risk
            strategies.extend([
                "✅ Good opportunity with manageable risk",
                "📦 Can invest standard amounts",
                "📊 Monitor weekly performance",
                "🚀 Consider scaling if performance is good"
            ])
        
        # استراتيجيات محددة حسب عوامل المخاطر
        for factor in risk_factors:
            if "competition" in factor.lower():
                strategies.append("🎯 Focus on unique value proposition and better customer service")
            
            if "seasonal" in factor.lower():
                strategies.append("📅 Time purchases carefully and consider off-season storage costs")
            
            if "volatility" in factor.lower():
                strategies.append("💹 Use dynamic pricing and quick inventory turnover")
            
            if "demand" in factor.lower():
                strategies.append("📢 Invest in marketing and product differentiation")
            
            if "supplier" in factor.lower():
                strategies.append("🔍 Verify supplier reliability and have backup options")
            
            if "regulatory" in factor.lower():
                strategies.append("📋 Ensure compliance with all relevant regulations and policies")
        
        return list(set(strategies))  # إزالة التكرار
    
    def _calculate_max_investment(self, amazon_price: float, risk_score: float) -> float:
        """💰 حساب الحد الأقصى للاستثمار"""
        base_investment = amazon_price * 10  # 10 وحدات كأساس
        
        # تقليل الاستثمار حسب المخاطر
        risk_multiplier = max(0.1, 1 - (risk_score / 100))
        
        max_investment = base_investment * risk_multiplier
        
        # حدود منطقية
        return max(amazon_price, min(max_investment, amazon_price * 50))
    
    def _calculate_stop_loss(self, ebay_price: float, risk_score: float) -> float:
        """🛑 حساب سعر وقف الخسارة"""
        # نسبة وقف الخسارة حسب المخاطر
        stop_loss_percentage = 0.1 + (risk_score / 1000)  # 10-20%
        
        stop_loss_price = ebay_price * (1 - stop_loss_percentage)
        
        return round(stop_loss_price, 2)
    
    def _calculate_confidence_interval(self, ebay_price: float, risk_score: float) -> Tuple[float, float]:
        """📊 حساب فترة الثقة للسعر"""
        # حساب التقلب المتوقع حسب المخاطر
        volatility = 0.05 + (risk_score / 2000)  # 5-10% تقلب
        
        lower_bound = ebay_price * (1 - volatility)
        upper_bound = ebay_price * (1 + volatility)
        
        return (round(lower_bound, 2), round(upper_bound, 2))
    
    def portfolio_risk_analysis(self, products: List[Dict]) -> Dict:
        """📊 تحليل مخاطر المحفظة"""
        if not products:
            return {"error": "No products provided"}
        
        total_investment = sum(p.get('investment', 0) for p in products)
        risk_scores = [p.get('risk_score', 50) for p in products]
        
        portfolio_risk = {
            'total_products': len(products),
            'total_investment': total_investment,
            'average_risk_score': np.mean(risk_scores),
            'risk_distribution': {
                'low_risk': sum(1 for score in risk_scores if score <= 30),
                'medium_risk': sum(1 for score in risk_scores if 30 < score <= 60),
                'high_risk': sum(1 for score in risk_scores if score > 60)
            },
            'diversification_score': self._calculate_diversification_score(products),
            'recommendations': self._get_portfolio_recommendations(risk_scores, total_investment)
        }
        
        return portfolio_risk
    
    def _calculate_diversification_score(self, products: List[Dict]) -> float:
        """🎯 حساب نقاط التنويع"""
        if len(products) <= 1:
            return 0
        
        # تنويع الفئات
        categories = [p.get('category', 'unknown') for p in products]
        unique_categories = len(set(categories))
        category_score = min(unique_categories / len(products), 1.0) * 50
        
        # تنويع الأسعار
        prices = [p.get('price', 0) for p in products if p.get('price', 0) > 0]
        if prices:
            price_variance = np.var(prices) / (np.mean(prices) ** 2) if np.mean(prices) > 0 else 0
            price_score = min(price_variance * 100, 50)
        else:
            price_score = 0
        
        return category_score + price_score
    
    def _get_portfolio_recommendations(self, risk_scores: List[float], total_investment: float) -> List[str]:
        """💡 توصيات المحفظة"""
        recommendations = []
        
        avg_risk = np.mean(risk_scores)
        high_risk_count = sum(1 for score in risk_scores if score > 60)
        
        if avg_risk > 70:
            recommendations.append("🚨 Portfolio has high average risk - Consider rebalancing")
        elif avg_risk < 30:
            recommendations.append("✅ Well-balanced low-risk portfolio")
        
        if high_risk_count > len(risk_scores) * 0.3:
            recommendations.append("⚠️ Too many high-risk products - Diversify with safer options")
        
        if total_investment > 10000:
            recommendations.append("💰 Large investment detected - Ensure proper risk management")
        
        if len(risk_scores) < 5:
            recommendations.append("📊 Consider adding more products for better diversification")
        
        return recommendations