import asyncio
import aiohttp
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional
import logging
from .trend_analyzer import TrendAnalyzer
from .profit_calculator import ProfitCalculator
from .risk_manager import RiskManager

@dataclass
class ViralProduct:
    name: str
    category: str
    trend_score: float
    amazon_price: float
    ebay_avg_price: float
    profit_margin: float
    confidence: float
    viral_signals: List[str]
    risk_level: str
    seasonality: Dict[str, float]

class ViralProductDetector:
    """🔥 AI-Powered Viral Product Detection Engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # تهيئة المكونات
        self.trend_analyzer = TrendAnalyzer()
        self.profit_calculator = ProfitCalculator()
        self.risk_manager = RiskManager()
        
        # High-profit niches 2025
        self.golden_niches = {
            'eco_fashion': {'weight': 35.6, 'keywords': ['sustainable', 'eco', 'organic']},
            'health_tech': {'weight': 42.3, 'keywords': ['wellness', 'fitness', 'health']},
            'beauty_care': {'weight': 28.9, 'keywords': ['skincare', 'beauty', 'cosmetic']},
            'gaming': {'weight': 31.2, 'keywords': ['gaming', 'controller', 'headset']},
            'outdoor': {'weight': 25.7, 'keywords': ['outdoor', 'camping', 'hiking']},
            'smart_home': {'weight': 38.4, 'keywords': ['smart', 'home', 'automation']},
            'phone_accessories': {'weight': 45.1, 'keywords': ['phone case', 'charger', 'wireless']},
            'pet_supplies': {'weight': 33.8, 'keywords': ['pet', 'dog', 'cat', 'toy']}
        }
    
    async def detect_viral_products(self, limit: int = 20) -> List[ViralProduct]:
        """🎯 اكتشاف المنتجات الفيروسية المربحة"""
        viral_products = []
        
        try:
            # تحليل الترندات من مصادر متعددة
            trends_data = await self.trend_analyzer.analyze_trending_products()
            
            # تطبيق الذكاء الاصطناعي للتنبؤ
            ai_predictions = await self._ai_profit_prediction(trends_data)
            
            # فلترة المنتجات عالية الربح
            high_profit = self._filter_high_profit_products(ai_predictions)
            
            # تحليل المخاطر والموسمية
            for product_data in high_profit[:limit]:
                viral_product = await self._create_viral_product(product_data)
                if viral_product.profit_margin > 40:  # 40%+ profit margin
                    viral_products.append(viral_product)
            
            return sorted(viral_products, key=lambda x: x.confidence, reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error detecting viral products: {e}")
            return []
    
    async def _ai_profit_prediction(self, trends_data: Dict) -> List[Dict]:
        """🤖 التنبؤ بالربحية باستخدام الذكاء الاصطناعي"""
        predictions = []
        
        for category, products in trends_data.items():
            for product in products:
                # حساب نقاط الربحية
                profit_score = self._calculate_profit_score(product)
                
                # تحليل الموسمية
                seasonality = product.get('seasonality', {})
                
                # تقييم المخاطر
                risk_assessment = self._assess_risk(product)
                
                predictions.append({
                    'keyword': product['keyword'],
                    'category': product['category'],
                    'trend_score': product.get('trend_score', 0),
                    'profit_score': profit_score,
                    'seasonality': seasonality,
                    'risk': risk_assessment,
                    'profit_potential': product.get('profit_potential', 0)
                })
        
        return predictions
    
    def _calculate_profit_score(self, product: Dict) -> float:
        """💰 حساب نقاط الربحية"""
        base_score = product.get('trend_score', 0)
        
        # تعزيز النقاط للفئات عالية الربح
        keyword = product['keyword'].lower()
        for niche, info in self.golden_niches.items():
            if any(kw in keyword for kw in info['keywords']):
                base_score *= (1 + info['weight'] / 100)
                break
        
        # تحليل الطلب مقابل العرض
        demand_supply_ratio = self._estimate_demand_supply(keyword)
        
        return min(base_score * demand_supply_ratio, 100)
    
    def _estimate_demand_supply(self, keyword: str) -> float:
        """📊 تقدير نسبة الطلب للعرض"""
        # محاكاة ذكية لنسبة الطلب للعرض
        base_ratio = 1.0
        
        # كلمات عالية الطلب
        if any(word in keyword.lower() for word in ['wireless', 'smart', 'portable', 'bluetooth']):
            base_ratio += 0.3
        
        # كلمات متوسطة الطلب
        if any(word in keyword.lower() for word in ['gaming', 'fitness', 'kitchen']):
            base_ratio += 0.2
        
        # إضافة تقلب واقعي
        random_factor = np.random.uniform(0.8, 1.4)
        
        return base_ratio * random_factor
    
    def _assess_risk(self, product: Dict) -> Dict:
        """⚠️ تقييم المخاطر"""
        keyword = product['keyword']
        trend_score = product.get('trend_score', 50)
        
        # مخاطر المنافسة
        competition_risk = 'High' if any(word in keyword.lower() for word in ['phone case', 'charger']) else 'Medium'
        
        # مخاطر الطلب
        demand_risk = 'Low' if trend_score > 70 else 'Medium' if trend_score > 40 else 'High'
        
        return {
            'competition': competition_risk,
            'demand': demand_risk,
            'overall': 'Low' if trend_score > 70 and competition_risk != 'High' else 'Medium'
        }
    
    def _filter_high_profit_products(self, predictions: List[Dict]) -> List[Dict]:
        """🎯 فلترة المنتجات عالية الربح"""
        # ترتيب حسب نقاط الربح
        sorted_predictions = sorted(predictions, key=lambda x: x['profit_score'], reverse=True)
        
        # فلترة المنتجات الجيدة
        high_profit = []
        for product in sorted_predictions:
            if (product['profit_score'] > 60 and 
                product['trend_score'] > 40 and
                product['risk']['overall'] != 'High'):
                high_profit.append(product)
        
        return high_profit
    
    async def _create_viral_product(self, product_data: Dict) -> ViralProduct:
        """🎯 إنشاء كائن المنتج الفيروسي"""
        keyword = product_data['keyword']
        
        # حساب الأسعار باستخدام ProfitCalculator
        amazon_price = np.random.uniform(10, 100)  # محاكاة سعر Amazon
        
        profit_analysis = self.profit_calculator.calculate_comprehensive_profit(
            product_name=keyword,
            amazon_price=amazon_price,
            trend_data=product_data
        )
        
        # تقييم المخاطر
        risk_assessment = self.risk_manager.assess_product_risk(
            product_name=keyword,
            amazon_price=amazon_price,
            ebay_price=profit_analysis.ebay_price,
            trend_data=product_data
        )
        
        # إشارات الانتشار الفيروسي
        viral_signals = []
        if product_data['trend_score'] > 80:
            viral_signals.append('🔥 Trending on Google')
        if profit_analysis.profit_margin > 70:
            viral_signals.append('💰 High Profit Potential')
        if product_data['seasonality']:
            viral_signals.append('📅 Seasonal Opportunity')
        if risk_assessment.risk_level == 'Low':
            viral_signals.append('🛡️ Low Risk Investment')
        
        return ViralProduct(
            name=keyword,
            category=product_data['category'],
            trend_score=product_data['trend_score'],
            amazon_price=amazon_price,
            ebay_avg_price=profit_analysis.ebay_price,
            profit_margin=profit_analysis.profit_margin,
            confidence=profit_analysis.confidence_level,
            viral_signals=viral_signals,
            risk_level=risk_assessment.risk_level,
            seasonality=product_data['seasonality']
        )
    
    def get_detection_summary(self, viral_products: List[ViralProduct]) -> Dict:
        """📋 ملخص الاكتشاف"""
        if not viral_products:
            return {"message": "No viral products detected"}
        
        return {
            'total_detected': len(viral_products),
            'average_profit_margin': np.mean([p.profit_margin for p in viral_products]),
            'average_confidence': np.mean([p.confidence for p in viral_products]),
            'risk_distribution': {
                'low': sum(1 for p in viral_products if p.risk_level == 'Low'),
                'medium': sum(1 for p in viral_products if p.risk_level == 'Medium'),
                'high': sum(1 for p in viral_products if p.risk_level == 'High')
            },
            'top_categories': self._get_top_categories(viral_products),
            'best_opportunity': viral_products[0].name if viral_products else None
        }
    
    def _get_top_categories(self, viral_products: List[ViralProduct]) -> Dict[str, int]:
        """📊 أفضل الفئات"""
        category_counts = {}
        for product in viral_products:
            category_counts[product.category] = category_counts.get(product.category, 0) + 1
        
        return dict(sorted(category_counts.items(), key=lambda x: x[1], reverse=True))