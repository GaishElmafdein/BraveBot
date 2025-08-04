#!/usr/bin/env python3
"""
🧠 BraveBot AI Module
=====================
وحدة الذكاء الاصطناعي المتقدمة
"""

__version__ = "2.1.0"
__author__ = "BraveBot Team"
__description__ = "Advanced AI Engine for BraveBot Commerce Empire"

# محاولة استيراد محركات AI
try:
    from .trends_engine import (
        fetch_viral_trends,
        dynamic_pricing_suggestion,
        TrendsEngine,
        TRENDS_ENGINE_AVAILABLE
    )
    
    AI_ENGINES_AVAILABLE = True
    
    __all__ = [
        'fetch_viral_trends',
        'dynamic_pricing_suggestion', 
        'TrendsEngine',
        'TRENDS_ENGINE_AVAILABLE',
        'AI_ENGINES_AVAILABLE'
    ]
    
    print("🧠 AI Engine module loaded successfully!")
    
except ImportError as e:
    print(f"⚠️ AI engines import warning: {e}")
    AI_ENGINES_AVAILABLE = False
    
    __all__ = ['AI_ENGINES_AVAILABLE']

# معلومات الوحدة
MODULE_INFO = {
    "name": "BraveBot AI Engine",
    "version": __version__,
    "features": [
        "🔥 Viral Trends Detection",
        "💰 Dynamic Pricing Engine", 
        "📊 Market Analysis",
        "🎯 Competitive Intelligence",
        "🌍 Global Trends Monitoring"
    ],
    "engines": [
        "Google Trends API",
        "Reddit Sentiment Analysis", 
        "YouTube Trends Scanner",
        "Amazon Best Sellers Tracker"
    ]
}

def get_module_info():
    """الحصول على معلومات وحدة AI"""
    return MODULE_INFO

def check_ai_health():
    """فحص صحة محركات AI"""
    
    if not AI_ENGINES_AVAILABLE:
        return {
            "status": "limited",
            "message": "AI engines not available"
        }
    
    try:
        # اختبار محرك الترندات
        from .trends_engine import fetch_viral_trends
        
        # اختبار سريع
        test_result = fetch_viral_trends("test", 1)
        
        return {
            "status": "ready",
            "message": "All AI engines operational",
            "engines_count": len(MODULE_INFO["engines"]),
            "test_successful": bool(test_result)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"AI engine error: {str(e)}"
        }

if __name__ == "__main__":
    # اختبار سريع للوحدة
    print("🧠 Testing AI Module...")
    
    info = get_module_info()
    print(f"📋 Module: {info['name']} v{info['version']}")
    
    health = check_ai_health()
    print(f"🏥 Health: {health['status']} - {health['message']}")
    
    if health['status'] == 'ready':
        print("✅ AI module ready for deployment!")
    else:
        print("⚠️ AI module needs attention")