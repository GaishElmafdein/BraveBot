#!/usr/bin/env python3
"""
📱 BraveBot Telegram Module
===========================
وحدة التليجرام للبوت الذكي
"""

__version__ = "2.0.0"
__author__ = "BraveBot Team"
__description__ = "Telegram Bot Interface for BraveBot AI Commerce Empire"

# محاولة استيراد المعالجات
try:
    from .handlers import BraveBotHandlers
    
    TELEGRAM_HANDLERS_AVAILABLE = True
    
    __all__ = [
        'BraveBotHandlers',
        'TELEGRAM_HANDLERS_AVAILABLE'
    ]
    
    print("📱 Telegram handlers loaded successfully!")
    
except ImportError as e:
    print(f"⚠️ Telegram handlers import warning: {e}")
    TELEGRAM_HANDLERS_AVAILABLE = False
    
    __all__ = ['TELEGRAM_HANDLERS_AVAILABLE']

# محاولة استيراد بوت التليجرام
try:
    from .bot import TelegramBot
    from .main import create_application
    
    TELEGRAM_BOT_AVAILABLE = True
    
    __all__.extend(['TelegramBot', 'create_application', 'TELEGRAM_BOT_AVAILABLE'])
    
    print("📱 Telegram bot module loaded successfully!")
    
except ImportError as e:
    print(f"⚠️ Telegram bot import warning: {e}")
    TELEGRAM_BOT_AVAILABLE = False
    
    __all__.append('TELEGRAM_BOT_AVAILABLE')

# معلومات الوحدة
MODULE_INFO = {
    "name": "BraveBot Telegram Interface",
    "version": __version__,
    "features": [
        "🤖 Smart Bot Handlers",
        "📊 Real-time Analytics", 
        "🧠 AI Integration",
        "🏆 Achievement System",
        "📈 Trends Analysis"
    ],
    "commands": [
        "/start", "/help", "/stats", "/trends", 
        "/viral", "/insights", "/compliance", "/achievements"
    ]
}

def get_module_info():
    """الحصول على معلومات الوحدة"""
    return MODULE_INFO

def check_telegram_health():
    """فحص صحة وحدة التليجرام"""
    import os
    
    token = os.getenv('TELEGRAM_TOKEN')
    if not token:
        return {
            "status": "error",
            "message": "TELEGRAM_TOKEN not found"
        }
    
    if not TELEGRAM_HANDLERS_AVAILABLE:
        return {
            "status": "limited",
            "message": "Handlers not available"
        }
    
    return {
        "status": "ready",
        "message": "All systems operational",
        "token_length": len(token),
        "handlers_available": TELEGRAM_HANDLERS_AVAILABLE,
        "bot_available": TELEGRAM_BOT_AVAILABLE
    }

# تصدير الدوال المهمة
def get_telegram_status():
    """الحصول على حالة التليجرام"""
    return {
        "handlers_available": TELEGRAM_HANDLERS_AVAILABLE,
        "bot_available": TELEGRAM_BOT_AVAILABLE,
        "module_version": __version__
    }

if __name__ == "__main__":
    # اختبار سريع للوحدة
    print("📱 Testing Telegram Module...")
    
    info = get_module_info()
    print(f"📋 Module: {info['name']} v{info['version']}")
    
    health = check_telegram_health()
    print(f"🏥 Health: {health['status']} - {health['message']}")
    
    if health['status'] == 'ready':
        print("✅ Telegram module ready for deployment!")
    else:
        print("⚠️ Telegram module needs attention")