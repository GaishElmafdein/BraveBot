"""
🧠 BraveBot AI Engine Module
============================
محرك الذكاء الاصطناعي المتقدم لتحليل الترندات والتسعير
"""

import logging
from typing import Dict, Any, Optional

# إعداد التسجيل
logger = logging.getLogger(__name__)

# متغيرات الحالة العامة
AI_ENGINE_AVAILABLE = False
_ai_engine_instance = None

# محاولة استيراد المحرك الرئيسي
try:
    from .ai_engine import BraveBotAIEngine
    AI_ENGINE_AVAILABLE = True
    logger.info("🧠 AI Engine core imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ AI Engine import failed: {e}")
    BraveBotAIEngine = None

def get_ai_engine() -> Optional[Any]:
    """
    الحصول على مثيل المحرك الذكي
    
    Returns:
        BraveBotAIEngine instance أو None إذا لم يكن متاحاً
    """
    global _ai_engine_instance
    
    if not AI_ENGINE_AVAILABLE:
        logger.warning("⚠️ AI Engine not available - returning None")
        return None
    
    if _ai_engine_instance is None:
        try:
            _ai_engine_instance = BraveBotAIEngine()
            logger.info("✅ AI Engine instance created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create AI Engine instance: {e}")
            return None
    
    return _ai_engine_instance

def get_engine_status() -> Dict[str, Any]:
    """
    الحصول على حالة المحرك الذكي
    
    Returns:
        Dict مع معلومات الحالة
    """
    if not AI_ENGINE_AVAILABLE:
        return {
            "status": "unavailable",
            "message": "AI Engine not imported",
            "active_engines": [],
            "cache_size": 0,
            "uptime_minutes": 0,
            "last_error": "Import failed"
        }
    
    engine = get_ai_engine()
    if not engine:
        return {
            "status": "failed", 
            "message": "AI Engine creation failed",
            "active_engines": [],
            "cache_size": 0,
            "uptime_minutes": 0,
            "last_error": "Instance creation failed"
        }
    
    try:
        # استدعاء دالة الحالة من المحرك
        return engine.get_status()
    except Exception as e:
        logger.error(f"❌ Error getting engine status: {e}")
        return {
            "status": "error",
            "message": f"Status check failed: {e}",
            "active_engines": [],
            "cache_size": 0,
            "uptime_minutes": 0,
            "last_error": str(e)
        }

async def analyze_trends(keyword: str) -> Dict[str, Any]:
    """
    تحليل ترند محدد
    
    Args:
        keyword: الكلمة المفتاحية للتحليل
        
    Returns:
        Dict مع نتائج التحليل
    """
    engine = get_ai_engine()
    if not engine:
        return {
            "keyword": keyword,
            "overall_viral_score": 50,
            "trend_category": "📊 غير محدد",
            "recommendations": ["المحرك الذكي غير متاح"],
            "confidence": 0,
            "data_source": "fallback_mode",
            "error": "AI Engine not available"
        }
    
    try:
        return await engine.analyze_trends(keyword)
    except Exception as e:
        logger.error(f"❌ Trends analysis failed: {e}")
        return {
            "keyword": keyword,
            "overall_viral_score": 45,
            "trend_category": "📊 خطأ في التحليل",
            "recommendations": [f"حدث خطأ: {str(e)[:50]}..."],
            "confidence": 0,
            "data_source": "error_fallback",
            "error": str(e)
        }

async def get_viral_trends(category: str = "technology", limit: int = 10) -> Dict[str, Any]:
    """
    الحصول على الترندات الفيروسية
    
    Args:
        category: فئة الترندات
        limit: عدد النتائج المطلوب
        
    Returns:
        Dict مع قائمة الترندات
    """
    engine = get_ai_engine()
    if not engine:
        return {
            "category": category,
            "top_keywords": [],
            "total_found": 0,
            "error": "AI Engine not available"
        }
    
    try:
        return await engine.get_viral_trends(category, limit)
    except Exception as e:
        logger.error(f"❌ Viral trends fetch failed: {e}")
        return {
            "category": category,
            "top_keywords": [],
            "total_found": 0,
            "error": str(e)
        }

async def suggest_pricing(base_price: float, viral_score: int, category: str = "general") -> Dict[str, Any]:
    """
    اقتراح التسعير الذكي
    
    Args:
        base_price: السعر الأساسي
        viral_score: نقاط الفيروسية
        category: الفئة
        
    Returns:
        Dict مع اقتراح التسعير
    """
    engine = get_ai_engine()
    if not engine:
        # حساب أساسي
        multiplier = 1.2 + (viral_score - 50) / 200
        suggested_price = round(base_price * multiplier, 2)
        
        return {
            "base_price": base_price,
            "suggested_price": suggested_price,
            "viral_score": viral_score,
            "category": category,
            "confidence": 50,
            "source": "basic_fallback",
            "error": "AI Engine not available"
        }
    
    try:
        return await engine.suggest_pricing(base_price, viral_score, category)
    except Exception as e:
        logger.error(f"❌ Pricing suggestion failed: {e}")
        return {
            "base_price": base_price,
            "suggested_price": base_price * 1.1,
            "viral_score": viral_score,
            "category": category,
            "confidence": 0,
            "source": "error_fallback",
            "error": str(e)
        }

async def generate_insights(time_period: str = "week", categories: list = None) -> Dict[str, Any]:
    """
    توليد الرؤى والتحليلات
    
    Args:
        time_period: الفترة الزمنية
        categories: قائمة الفئات
        
    Returns:
        Dict مع الرؤى المُولدة
    """
    engine = get_ai_engine()
    if not engine:
        return {
            "time_period": time_period,
            "top_trends": categories or ["Technology", "Gaming"],
            "market_outlook": "غير متاح - المحرك الذكي غير نشط",
            "recommendations": ["قم بتفعيل المحرك الذكي للحصول على رؤى دقيقة"],
            "confidence": 0,
            "error": "AI Engine not available"
        }
    
    try:
        return await engine.generate_insights(time_period, categories)
    except Exception as e:
        logger.error(f"❌ Insights generation failed: {e}")
        return {
            "time_period": time_period,
            "top_trends": categories or ["Error"],
            "market_outlook": f"خطأ في التحليل: {str(e)[:50]}...",
            "recommendations": ["تحقق من حالة المحرك الذكي"],
            "confidence": 0,
            "error": str(e)
        }

# تصدير الوظائف والكلاسات
__all__ = [
    'AI_ENGINE_AVAILABLE',
    'BraveBotAIEngine',
    'get_ai_engine', 
    'get_engine_status',
    'analyze_trends',
    'get_viral_trends',
    'suggest_pricing',
    'generate_insights'
]

# رسالة حالة التحميل
if AI_ENGINE_AVAILABLE:
    print("🧠 AI Engine module loaded successfully!")
else:
    print("⚠️ AI Engine module in fallback mode")