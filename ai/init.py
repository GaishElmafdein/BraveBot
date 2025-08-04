"""
🤖 BraveBot AI Engines Collection
=================================
مجموعة محركات الذكاء الاصطناعي المتخصصة
"""

import logging

# إعداد التسجيل
logger = logging.getLogger(__name__)

# متغيرات الحالة
TRENDS_ENGINE_AVAILABLE = False
ENGINES_LOADED = []

# محاولة استيراد محرك الترندات
try:
    from .trends_engine import (
        TrendsFetcher,
        ViralTrendScanner, 
        fetch_viral_trends,
        dynamic_pricing_suggestion,
        generate_weekly_insights
    )
    TRENDS_ENGINE_AVAILABLE = True
    ENGINES_LOADED.append("trends_engine")
    logger.info("📈 Trends Engine loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Trends Engine import failed: {e}")
    # إنشاء دوال وهمية للتوافق
    TrendsFetcher = None
    ViralTrendScanner = None
    
    def fetch_viral_trends(*args, **kwargs):
        return {"error": "Trends engine not available"}
    
    def dynamic_pricing_suggestion(*args, **kwargs):
        return {"error": "Pricing engine not available"}
    
    def generate_weekly_insights(*args, **kwargs):
        return {"error": "Insights engine not available"}

# محاولة استيراد محركات إضافية (مستقبلية)
try:
    from .viral_scanner import ViralScanner
    ENGINES_LOADED.append("viral_scanner")
    logger.info("🔥 Viral Scanner loaded")
except ImportError:
    ViralScanner = None

try:
    from .pricing_optimizer import PricingOptimizer  
    ENGINES_LOADED.append("pricing_optimizer")
    logger.info("💰 Pricing Optimizer loaded")
except ImportError:
    PricingOptimizer = None

try:
    from .insights_generator import InsightsGenerator
    ENGINES_LOADED.append("insights_generator") 
    logger.info("📊 Insights Generator loaded")
except ImportError:
    InsightsGenerator = None

def get_available_engines():
    """الحصول على قائمة المحركات المتاحة"""
    return {
        "total_engines": len(ENGINES_LOADED),
        "available_engines": ENGINES_LOADED,
        "trends_engine": TRENDS_ENGINE_AVAILABLE,
        "status": "healthy" if ENGINES_LOADED else "limited"
    }

def get_engine_info():
    """معلومات تفصيلية عن المحركات"""
    return {
        "engines": {
            "trends_engine": {
                "available": TRENDS_ENGINE_AVAILABLE,
                "features": ["trend_analysis", "viral_detection", "pricing_suggestion"] if TRENDS_ENGINE_AVAILABLE else []
            },
            "viral_scanner": {
                "available": ViralScanner is not None,
                "features": ["social_scanning"] if ViralScanner else []
            },
            "pricing_optimizer": {
                "available": PricingOptimizer is not None,
                "features": ["dynamic_pricing"] if PricingOptimizer else []
            },
            "insights_generator": {
                "available": InsightsGenerator is not None,
                "features": ["market_insights"] if InsightsGenerator else []
            }
        },
        "overall_status": "operational" if ENGINES_LOADED else "minimal"
    }

# تصدير جميع الوظائف المتاحة
__all__ = [
    'TRENDS_ENGINE_AVAILABLE',
    'ENGINES_LOADED',
    'TrendsFetcher',
    'ViralTrendScanner',
    'fetch_viral_trends', 
    'dynamic_pricing_suggestion',
    'generate_weekly_insights',
    'ViralScanner',
    'PricingOptimizer', 
    'InsightsGenerator',
    'get_available_engines',
    'get_engine_info'
]

# رسالة حالة التحميل
if ENGINES_LOADED:
    print(f"🤖 AI Engines loaded: {', '.join(ENGINES_LOADED)}")
else:
    print("⚠️ AI Engines in minimal mode")