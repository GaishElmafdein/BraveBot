import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import logging

@dataclass
class ProfitAnalysis:
    """📊 تحليل الربحية"""
    product_name: str
    amazon_price: float
    ebay_price: float
    profit_amount: float
    profit_margin: float
    roi: float
    break_even_quantity: int
    risk_score: float
    confidence_level: float
    market_demand: str
    competition_level: str
    seasonal_factor: float

class ProfitCalculator:
    """💰 حاسبة الأرباح المتقدمة"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # تكاليف إضافية نموذجية
        self.additional_costs = {
            'ebay_fees': 0.1,  # 10% رسوم eBay
            'paypal_fees': 0.029,  # 2.9% رسوم PayPal
            'shipping_cost': 3.50,  # متوسط تكلفة الشحن
            'packaging_cost': 0.50,  # تكلفة التغليف
            'return_rate': 0.05,  # 5% معدل الإرجاع
            'currency_fluctuation': 0.02  # 2% تقلبات العملة
        }
        
        # عوامل المخاطر
        self.risk_factors = {
            'high_competition': 0.3,
            'seasonal_product': 0.2,
            'low_demand': 0.4,
            'price_volatility': 0.25,
            'shipping_issues': 0.15
        }
    
    def calculate_comprehensive_profit(self, 
                                     product_name: str,
                                     amazon_price: float,
                                     estimated_ebay_price: float = None,
                                     trend_data: Dict = None) -> ProfitAnalysis:
        """🎯 حساب الربح الشامل"""
        
        # تقدير سعر eBay إذا لم يُقدم
        if estimated_ebay_price is None:
            estimated_ebay_price = self._estimate_ebay_price(amazon_price, product_name, trend_data)
        
        # حساب التكاليف الإجمالية
        total_cost = self._calculate_total_cost(amazon_price)
        
        # حساب الربح الصافي
        net_profit = estimated_ebay_price - total_cost
        profit_margin = (net_profit / total_cost) * 100 if total_cost > 0 else 0
        roi = (net_profit / amazon_price) * 100 if amazon_price > 0 else 0
        
        # تحليل المخاطر
        risk_score = self._calculate_risk_score(product_name, amazon_price, estimated_ebay_price, trend_data)
        
        # مستوى الثقة
        confidence_level = self._calculate_confidence(trend_data, risk_score)
        
        # تحليل السوق
        market_analysis = self._analyze_market_conditions(product_name, trend_data)
        
        # العامل الموسمي
        seasonal_factor = self._calculate_seasonal_factor(product_name)
        
        # نقطة التعادل
        break_even_qty = max(1, int(50 / max(net_profit, 0.01)))  # 50$ هدف الربح الأدنى
        
        return ProfitAnalysis(
            product_name=product_name,
            amazon_price=amazon_price,
            ebay_price=estimated_ebay_price,
            profit_amount=net_profit,
            profit_margin=profit_margin,
            roi=roi,
            break_even_quantity=break_even_qty,
            risk_score=risk_score,
            confidence_level=confidence_level,
            market_demand=market_analysis['demand'],
            competition_level=market_analysis['competition'],
            seasonal_factor=seasonal_factor
        )
    
    def _estimate_ebay_price(self, amazon_price: float, product_name: str, trend_data: Dict = None) -> float:
        """💡 تقدير سعر eBay الذكي"""
        
        # عامل الضرب الأساسي (عادة 1.4 - 2.5)
        base_multiplier = 1.6
        
        # تعديل حسب نوع المنتج
        product_lower = product_name.lower()
        
        if any(word in product_lower for word in ['gaming', 'tech', 'electronics']):
            base_multiplier += 0.3  # منتجات تقنية أغلى
        
        if any(word in product_lower for word in ['luxury', 'premium', 'pro']):
            base_multiplier += 0.4  # منتجات راقية
        
        if any(word in product_lower for word in ['generic', 'basic', 'simple']):
            base_multiplier -= 0.2  # منتجات بسيطة أرخص
        
        # تعديل حسب بيانات الاتجاه
        if trend_data:
            trend_score = trend_data.get('trend_score', 50)
            if trend_score > 80:
                base_multiplier += 0.5  # ترند عالي = سعر أعلى
            elif trend_score < 30:
                base_multiplier -= 0.3  # ترند منخفض = سعر أقل
        
        # تعديل حسب السعر الأساسي
        if amazon_price < 10:
            base_multiplier += 0.8  # منتجات رخيصة هامش ربح أكبر
        elif amazon_price > 100:
            base_multiplier -= 0.2  # منتجات غالية هامش أقل
        
        # ضمان حدود منطقية
        base_multiplier = max(1.2, min(3.0, base_multiplier))
        
        # إضافة تقلب عشوائي واقعي (±10%)
        random_factor = np.random.uniform(0.9, 1.1)
        
        estimated_price = amazon_price * base_multiplier * random_factor
        
        # تقريب لأقرب سنت
        return round(estimated_price, 2)
    
    def _calculate_total_cost(self, amazon_price: float) -> float:
        """💸 حساب التكلفة الإجمالية"""
        total_cost = amazon_price
        
        # رسوم eBay
        ebay_fee = amazon_price * self.additional_costs['ebay_fees']
        
        # رسوم PayPal
        paypal_fee = amazon_price * self.additional_costs['paypal_fees']
        
        # تكاليف الشحن والتغليف
        shipping_packaging = (self.additional_costs['shipping_cost'] + 
                            self.additional_costs['packaging_cost'])
        
        # تكلفة الإرجاعات (نسبة من السعر)
        return_cost = amazon_price * self.additional_costs['return_rate']
        
        # تقلبات العملة
        currency_risk = amazon_price * self.additional_costs['currency_fluctuation']
        
        total_cost += ebay_fee + paypal_fee + shipping_packaging + return_cost + currency_risk
        
        return round(total_cost, 2)
    
    def _calculate_risk_score(self, product_name: str, amazon_price: float, 
                            ebay_price: float, trend_data: Dict = None) -> float:
        """⚠️ حساب نقاط المخاطر"""
        risk_score = 0
        
        # مخاطر هامش الربح
        profit_margin = ((ebay_price - amazon_price) / amazon_price) * 100
        if profit_margin < 20:
            risk_score += 40
        elif profit_margin < 40:
            risk_score += 20
        
        # مخاطر السعر
        if amazon_price > 200:
            risk_score += 25  # منتجات غالية أكثر مخاطرة
        elif amazon_price < 5:
            risk_score += 15  # منتجات رخيصة جداً قد تكون مشبوهة
        
        # مخاطر المنافسة (حسب نوع المنتج)
        product_lower = product_name.lower()
        if any(word in product_lower for word in ['phone case', 'charger', 'cable']):
            risk_score += self.risk_factors['high_competition'] * 100
        
        # مخاطر الموسمية
        if any(word in product_lower for word in ['christmas', 'halloween', 'valentine']):
            risk_score += self.risk_factors['seasonal_product'] * 100
        
        # مخاطر الطلب (حسب بيانات الاتجاه)
        if trend_data:
            trend_score = trend_data.get('trend_score', 50)
            if trend_score < 30:
                risk_score += self.risk_factors['low_demand'] * 100
        
        return min(risk_score, 100)  # الحد الأقصى 100
    
    def _calculate_confidence(self, trend_data: Dict = None, risk_score: float = 50) -> float:
        """🎯 حساب مستوى الثقة"""
        base_confidence = 70
        
        # تعديل حسب المخاطر
        confidence = base_confidence - (risk_score * 0.5)
        
        # تعديل حسب بيانات الاتجاه
        if trend_data:
            trend_score = trend_data.get('trend_score', 50)
            growth_rate = trend_data.get('growth_rate', 0)
            
            # ترند قوي = ثقة أعلى
            if trend_score > 70:
                confidence += 15
            elif trend_score < 30:
                confidence -= 20
            
            # نمو إيجابي = ثقة أعلى
            if growth_rate > 20:
                confidence += 10
            elif growth_rate < -10:
                confidence -= 15
        
        return max(10, min(95, confidence))
    
    def _analyze_market_conditions(self, product_name: str, trend_data: Dict = None) -> Dict:
        """📊 تحليل ظروف السوق"""
        product_lower = product_name.lower()
        
        # تحليل الطلب
        demand = 'Medium'  # افتراضي
        if trend_data:
            trend_score = trend_data.get('trend_score', 50)
            if trend_score > 70:
                demand = 'High'
            elif trend_score < 30:
                demand = 'Low'
        
        # تحليل المنافسة
        competition = 'Medium'  # افتراضي
        
        # منتجات عالية المنافسة
        if any(word in product_lower for word in ['phone case', 'charger', 'earbuds', 'cable']):
            competition = 'High'
        
        # منتجات متخصصة أقل منافسة
        elif any(word in product_lower for word in ['professional', 'specialized', 'niche']):
            competition = 'Low'
        
        return {
            'demand': demand,
            'competition': competition
        }
    
    def _calculate_seasonal_factor(self, product_name: str) -> float:
        """📅 حساب العامل الموسمي"""
        current_month = datetime.now().month
        product_lower = product_name.lower()
        
        seasonal_boost = 1.0  # عامل افتراضي
        
        # منتجات الكريسماس (نوفمبر - ديسمبر)
        if any(word in product_lower for word in ['gift', 'decoration', 'christmas']):
            if current_month in [11, 12]:
                seasonal_boost = 1.8
            elif current_month in [9, 10]:
                seasonal_boost = 1.3
            else:
                seasonal_boost = 0.7
        
        # منتجات الصيف (مايو - أغسطس)
        elif any(word in product_lower for word in ['outdoor', 'swimming', 'travel', 'beach']):
            if current_month in [5, 6, 7, 8]:
                seasonal_boost = 1.6
            elif current_month in [3, 4, 9]:
                seasonal_boost = 1.2
            else:
                seasonal_boost = 0.8
        
        # منتجات العودة للمدرسة (يوليو - سبتمبر)
        elif any(word in product_lower for word in ['laptop', 'backpack', 'stationery', 'desk']):
            if current_month in [7, 8, 9]:
                seasonal_boost = 1.7
            elif current_month in [6, 10]:
                seasonal_boost = 1.3
            else:
                seasonal_boost = 0.9
        
        # منتجات الفتنس (يناير - مارس)
        elif any(word in product_lower for word in ['fitness', 'yoga', 'protein', 'gym']):
            if current_month in [1, 2, 3]:
                seasonal_boost = 1.5
            elif current_month in [4, 12]:
                seasonal_boost = 1.2
            else:
                seasonal_boost = 0.9
        
        return seasonal_boost
    
    def batch_analyze_products(self, products: List[Dict]) -> List[ProfitAnalysis]:
        """📦 تحليل دفعي للمنتجات"""
        analyses = []
        
        for product in products:
            try:
                analysis = self.calculate_comprehensive_profit(
                    product_name=product.get('name', 'Unknown Product'),
                    amazon_price=product.get('amazon_price', 0),
                    estimated_ebay_price=product.get('ebay_price'),
                    trend_data=product.get('trend_data')
                )
                analyses.append(analysis)
            except Exception as e:
                self.logger.error(f"Error analyzing {product.get('name', 'Unknown')}: {e}")
                continue
        
        # ترتيب حسب هامش الربح
        analyses.sort(key=lambda x: x.profit_margin, reverse=True)
        return analyses
    
    def get_profit_recommendations(self, analysis: ProfitAnalysis) -> List[str]:
        """💡 توصيات الربح"""
        recommendations = []
        
        if analysis.profit_margin > 60:
            recommendations.append("🚀 EXCELLENT profit margin - Strong Buy!")
        elif analysis.profit_margin > 40:
            recommendations.append("✅ Good profit potential - Recommended")
        elif analysis.profit_margin > 20:
            recommendations.append("⚠️ Moderate profit - Consider market conditions")
        else:
            recommendations.append("❌ Low profit margin - Not recommended")
        
        if analysis.risk_score < 30:
            recommendations.append("🛡️ Low risk investment")
        elif analysis.risk_score > 70:
            recommendations.append("⚠️ High risk - Proceed with caution")
        
        if analysis.seasonal_factor > 1.3:
            recommendations.append("📅 Perfect seasonal timing - Act fast!")
        elif analysis.seasonal_factor < 0.8:
            recommendations.append("📅 Off-season - Consider waiting")
        
        if analysis.confidence_level > 80:
            recommendations.append("🎯 High confidence prediction")
        elif analysis.confidence_level < 50:
            recommendations.append("❓ Low confidence - Need more data")
        
        return recommendations