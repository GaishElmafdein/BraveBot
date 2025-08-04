"""
🏗️ BraveBot Ultimate - Core Infrastructure
==========================================
"""

from .config import config, BraveBotConfig

__all__ = ['config', 'BraveBotConfig']

"""
🏗️ BraveBot Core Module
======================
النواة الأساسية لنظام BraveBot AI Commerce Empire
"""

__version__ = "2.0.0"
__author__ = "BraveBot Team"
__description__ = "AI-Powered E-commerce Trends Analysis System"

# محاولة استيراد المحرك الأساسي
try:
    from .ai_engine import get_ai_engine, get_engine_status
    from .ai_engine.ai_engine import BraveBotAIEngine
    
    CORE_AVAILABLE = True
    
    __all__ = [
        'get_ai_engine', 
        'get_engine_status', 
        'BraveBotAIEngine',
        'CORE_AVAILABLE'
    ]
    
except ImportError as e:
    print(f"⚠️ Core AI Engine import warning: {e}")
    CORE_AVAILABLE = False
    
    __all__ = ['CORE_AVAILABLE']

def get_core_info():
    """معلومات النواة الأساسية"""
    return {
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "core_available": CORE_AVAILABLE,
        "components": [
            "AI Engine",
            "Risk Manager", 
            "Cache System",
            "Configuration Manager"
        ] if CORE_AVAILABLE else ["Limited Mode"]
    }

# رسالة الترحيب
if CORE_AVAILABLE:
    print("✅ BraveBot Core Module loaded successfully!")
else:
    print("⚠️ BraveBot Core Module in limited mode")