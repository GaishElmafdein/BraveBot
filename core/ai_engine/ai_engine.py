#!/usr/bin/env python3
"""
🧠 BraveBot AI Core Engine
=========================
المحرك الأساسي للذكاء الاصطناعي - يجمع جميع وظائف AI
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import random

# استيراد المحركات المختلفة
try:
    from ai.trends_engine import TrendsFetcher, ViralTrendScanner, fetch_viral_trends
    from ai.trends_engine import dynamic_pricing_suggestion, generate_weekly_insights
    AI_ENGINES_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ AI engines not available: {e}")
    AI_ENGINES_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BraveBotAIEngine:
    """
    🎯 المحرك الأساسي للذكاء الاصطناعي
    ================================
    يجمع جميع وظائف الـ AI في واجهة موحدة
    """
    
    def __init__(self):
        """تهيئة محرك الذكاء الاصطناعي"""
        self.status = "initializing"
        self.last_update = datetime.now()
        self.engines = {}
        self.cache = {}
        self.config = self._load_config()
        
        logger.info("🚀 Initializing BraveBot AI Engine...")
        self._initialize_engines()
        
    def _load_config(self) -> Dict[str, Any]:
        """تحميل إعدادات المحرك"""
        default_config = {
            "cache_duration": 300,  # 5 دقائق
            "max_requests_per_minute": 30,
            "fallback_mode": True,
            "debug_mode": False,
            "engines": {
                "trends": True,
                "pricing": True,
                "insights": True
            }
        }
        
        config_path = Path("config/ai_config.json")
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"⚠️ Config load failed: {e}")
        
        return default_config
    
    def _initialize_engines(self):
        """تهيئة جميع محركات الـ AI"""
        try:
            if AI_ENGINES_AVAILABLE:
                # تهيئة محرك الترندات
                if self.config["engines"]["trends"]:
                    self.engines["trends_fetcher"] = TrendsFetcher()
                    self.engines["viral_scanner"] = ViralTrendScanner()
                    logger.info("✅ Trends engines initialized")
                
                self.status = "ready"
                logger.info("🎉 All AI engines initialized successfully")
            else:
                self.status = "limited"
                logger.warning("⚠️ AI engines in limited mode")
                
        except Exception as e:
            logger.error(f"❌ Engine initialization failed: {e}")
            self.status = "error"
    
    def get_status(self) -> Dict[str, Any]:
        """الحصول على حالة المحرك"""
        return {
            "status": self.status,
            "last_update": self.last_update.isoformat(),
            "engines_available": AI_ENGINES_AVAILABLE,
            "active_engines": list(self.engines.keys()),
            "cache_size": len(self.cache),
            "uptime_minutes": int((datetime.now() - self.last_update).total_seconds() / 60)
        }
    
    async def analyze_trends(self, keyword: str, **kwargs) -> Dict[str, Any]:
        """
        🔍 تحليل الترندات - الواجهة الموحدة
        """
        try:
            cache_key = f"trends_{keyword}_{hash(str(kwargs))}"
            
            # فحص الكاش
            if self._is_cached(cache_key):
                logger.info(f"📋 Using cached data for: {keyword}")
                return self.cache[cache_key]["data"]
            
            # تحليل حقيقي
            if self.status == "ready" and "trends_fetcher" in self.engines:
                trends_fetcher = self.engines["trends_fetcher"]
                result = trends_fetcher.analyze_combined_trends(
                    keyword=keyword,
                    **kwargs
                )
                
                # حفظ في الكاش
                self._cache_result(cache_key, result)
                
                logger.info(f"✅ Trends analysis completed for: {keyword}")
                return result
            
            # Fallback mode
            return self._fallback_trends_analysis(keyword)
            
        except Exception as e:
            logger.error(f"❌ Trends analysis failed: {e}")
            return self._fallback_trends_analysis(keyword, error=str(e))
    
    async def get_viral_trends(self, category: str = "technology", limit: int = 10) -> Dict[str, Any]:
        """
        🔥 الحصول على الترندات الفيروسية
        """
        try:
            cache_key = f"viral_{category}_{limit}"
            
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            if self.status == "ready" and "viral_scanner" in self.engines:
                viral_scanner = self.engines["viral_scanner"]
                result = viral_scanner.get_category_trends(
                    category=category,
                    limit=limit
                )
                
                self._cache_result(cache_key, result)
                return result
            
            # استخدام الدالة المستقلة كـ fallback
            return fetch_viral_trends(keyword=category, limit=limit)
            
        except Exception as e:
            logger.error(f"❌ Viral trends failed: {e}")
            return self._fallback_viral_trends(category, limit)
    
    async def suggest_pricing(self, base_price: float, viral_score: int, category: str = "general") -> Dict[str, Any]:
        """
        💰 اقتراح التسعير الذكي
        """
        try:
            # استخدام محرك التسعير المستقل
            result = dynamic_pricing_suggestion(
                base_price=base_price,
                viral_score=viral_score,
                category=category
            )
            
            logger.info(f"💰 Pricing suggestion: {base_price} -> {result.get('suggested_price')}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Pricing suggestion failed: {e}")
            return self._fallback_pricing(base_price, viral_score, category)
    
    async def generate_insights(self, time_period: str = "week", categories: List[str] = None) -> Dict[str, Any]:
        """
        📊 توليد الرؤى الأسبوعية
        """
        try:
            result = generate_weekly_insights(
                time_period=time_period,
                categories=categories
            )
            
            logger.info(f"📊 Weekly insights generated for: {time_period}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Insights generation failed: {e}")
            return self._fallback_insights(time_period)
    
    def _is_cached(self, cache_key: str) -> bool:
        """فحص وجود البيانات في الكاش"""
        if cache_key not in self.cache:
            return False
        
        cache_entry = self.cache[cache_key]
        cache_age = (datetime.now() - cache_entry["timestamp"]).total_seconds()
        
        return cache_age < self.config["cache_duration"]
    
    def _cache_result(self, cache_key: str, data: Any):
        """حفظ النتيجة في الكاش"""
        self.cache[cache_key] = {
            "data": data,
            "timestamp": datetime.now()
        }
        
        # تنظيف الكاش القديم
        self._cleanup_cache()
    
    def _cleanup_cache(self):
        """تنظيف الكاش القديم"""
        current_time = datetime.now()
        expired_keys = []
        
        for key, entry in self.cache.items():
            age = (current_time - entry["timestamp"]).total_seconds()
            if age > self.config["cache_duration"]:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
    
    def _fallback_trends_analysis(self, keyword: str, error: str = None) -> Dict[str, Any]:
        """تحليل ترندات احتياطي"""
        viral_score = random.randint(25, 85)
        
        return {
            "keyword": keyword,
            "timestamp": datetime.now().isoformat(),
            "overall_viral_score": viral_score,
            "trend_category": self._categorize_score(viral_score),
            "recommendations": self._generate_recommendations(viral_score),
            "data_source": "fallback",
            "status": "limited_data",
            "error": error
        }
    
    def _fallback_viral_trends(self, category: str, limit: int) -> Dict[str, Any]:
        """ترندات فيروسية احتياطية"""
        mock_trends = []
        base_keywords = ["AI", "Technology", "Innovation", "Digital", "Future"]
        
        for i in range(min(limit, 5)):
            keyword = f"{random.choice(base_keywords)} {category.title()}"
            viral_score = random.randint(30, 95)
            
            mock_trends.append({
                "keyword": keyword,
                "viral_score": viral_score,
                "category": self._categorize_score(viral_score),
                "source": "fallback"
            })
        
        return {
            "category": category,
            "top_keywords": mock_trends,
            "total_found": len(mock_trends),
            "timestamp": datetime.now().isoformat(),
            "source": "fallback_data"
        }
    
    def _fallback_pricing(self, base_price: float, viral_score: int, category: str) -> Dict[str, Any]:
        """تسعير احتياطي"""
        multiplier = 1.0 + (viral_score - 50) / 200  # تعديل بسيط حسب النقاط
        suggested_price = base_price * multiplier
        
        return {
            "base_price": base_price,
            "suggested_price": round(suggested_price, 2),
            "viral_score": viral_score,
            "category": category,
            "confidence": 60,  # ثقة منخفضة للبيانات الاحتياطية
            "source": "fallback",
            "timestamp": datetime.now().isoformat()
        }
    
    def _fallback_insights(self, time_period: str) -> Dict[str, Any]:
        """رؤى احتياطية"""
        return {
            "time_period": time_period,
            "top_trends": ["Technology", "AI", "Innovation"],
            "market_outlook": "متفائل بحذر",
            "recommendations": [
                "📊 تابع الترندات التقنية",
                "💡 استثمر في الابتكار"
            ],
            "confidence": 50,
            "source": "fallback",
            "timestamp": datetime.now().isoformat()
        }
    
    def _categorize_score(self, score: int) -> str:
        """تصنيف النقاط"""
        if score >= 80:
            return "🔥 ساخن جداً"
        elif score >= 60:
            return "📈 صاعد"
        elif score >= 40:
            return "⚡ متوسط"
        else:
            return "📊 هادئ"
    
    def _generate_recommendations(self, score: int) -> List[str]:
        """توليد التوصيات"""
        if score >= 80:
            return [
                "🎯 استغل هذا الترند فوراً",
                "📱 انشر محتوى متعلق الآن"
            ]
        elif score >= 60:
            return [
                "📈 ترند واعد - راقب التطورات",
                "💡 فكر في محتوى إبداعي"
            ]
        else:
            return [
                "📊 ترند هادئ - للمحتوى طويل المدى",
                "🔍 ابحث عن فرص أخرى"
            ]

# إنشاء instance عالمي
_ai_engine_instance = None

def get_ai_engine() -> BraveBotAIEngine:
    """الحصول على instance المحرك الرئيسي"""
    global _ai_engine_instance
    
    if _ai_engine_instance is None:
        _ai_engine_instance = BraveBotAIEngine()
    
    return _ai_engine_instance

# دوال مساعدة للاستيراد السهل
async def analyze_trends(keyword: str, **kwargs) -> Dict[str, Any]:
    """دالة سريعة لتحليل الترندات"""
    engine = get_ai_engine()
    return await engine.analyze_trends(keyword, **kwargs)

async def get_viral_trends(category: str = "technology", limit: int = 10) -> Dict[str, Any]:
    """دالة سريعة للترندات الفيروسية"""
    engine = get_ai_engine()
    return await engine.get_viral_trends(category, limit)

async def suggest_pricing(base_price: float, viral_score: int, category: str = "general") -> Dict[str, Any]:
    """دالة سريعة لاقتراح التسعير"""
    engine = get_ai_engine()
    return await engine.suggest_pricing(base_price, viral_score, category)

async def generate_insights(time_period: str = "week", categories: List[str] = None) -> Dict[str, Any]:
    """دالة سريعة لتوليد الرؤى"""
    engine = get_ai_engine()
    return await engine.generate_insights(time_period, categories)

def get_engine_status() -> Dict[str, Any]:
    """الحصول على حالة المحرك"""
    engine = get_ai_engine()
    return engine.get_status()

# للتوافق مع النظام القديم
ai_engine = get_ai_engine

__all__ = [
    'BraveBotAIEngine',
    'get_ai_engine',
    'analyze_trends',
    'get_viral_trends', 
    'suggest_pricing',
    'generate_insights',
    'get_engine_status',
    'ai_engine'
]

if __name__ == "__main__":
    # اختبار سريع للمحرك
    async def test_engine():
        print("🧠 Testing BraveBot AI Engine...")
        
        engine = get_ai_engine()
        status = engine.get_status()
        print(f"📊 Engine Status: {status}")
        
        # اختبار تحليل الترندات
        result = await analyze_trends("AI Technology")
        print(f"🔍 Trends Analysis: {result.get('overall_viral_score', 'N/A')}")
        
        # اختبار التسعير
        pricing = await suggest_pricing(100.0, 75)
        print(f"💰 Pricing: ${pricing.get('suggested_price', 'N/A')}")
        
        print("✅ AI Engine test completed!")
    
    asyncio.run(test_engine())