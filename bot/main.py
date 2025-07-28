import logging
import os
from telegram.ext import Application
from handlers import register_handlers

# إعداد Logging للوضع الحقيقي
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

def main():
    """تشغيل البوت - Real Data Only Mode"""
    
    logger.info("🔥 Starting BraveBot - REAL DATA ONLY MODE")
    
    # التحقق من الـ Token
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        logger.error("❌ BOT_TOKEN not found in environment variables")
        return
    
    # إنشاء التطبيق
    application = Application.builder().token(bot_token).build()
    
    # تسجيل المعالجات
    register_handlers(application)
    
    logger.info("✅ BraveBot started successfully - NO MOCK DATA")
    logger.info("🌐 Real APIs: Google Trends + Reddit")
    logger.info("⚠️ Will show errors if APIs fail - NO FALLBACK")
    
    # تشغيل البوت
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()