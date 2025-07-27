#!/usr/bin/env python3
"""
🤖 BraveBot - Telegram Bot Core
===============================
البوت الرئيسي مع دعم الذكاء الاصطناعي والتحليلات المتقدمة
"""

import logging
import asyncio
import os
from telegram.ext import Application
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# استيراد معالجات البوت
from handlers import register_handlers

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class BraveBot:
    """الكلاس الرئيسي للبوت"""
    
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("❌ TELEGRAM_BOT_TOKEN غير موجود في متغيرات البيئة")
        
        self.application = None
    
    async def initialize(self):
        """تهيئة البوت"""
        logger.info("🚀 بدء تهيئة BraveBot...")
        
        # إنشاء تطبيق البوت
        self.application = Application.builder().token(self.token).build()
        
        # تسجيل المعالجات
        register_handlers(self.application)
        
        logger.info("✅ تم تهيئة البوت بنجاح")
    
    async def start_bot(self):
        """بدء تشغيل البوت"""
        if not self.application:
            await self.initialize()
        
        logger.info("🤖 بدء تشغيل BraveBot...")
        
        try:
            # بدء البوت
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling(
                allowed_updates=["message", "callback_query"],
                drop_pending_updates=True
            )
            
            logger.info("✅ BraveBot يعمل الآن!")
            
            # انتظار إيقاف البوت
            await self.application.updater.idle()
            
        except Exception as e:
            logger.error(f"❌ خطأ في تشغيل البوت: {e}")
            raise
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """إيقاف البوت بأمان"""
        if self.application:
            logger.info("🛑 إيقاف البوت...")
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            logger.info("✅ تم إيقاف البوت بنجاح")

async def main():
    """الدالة الرئيسية"""
    bot = BraveBot()
    
    try:
        await bot.start_bot()
    except KeyboardInterrupt:
        logger.info("🛑 تم إيقاف البوت بواسطة المستخدم")
    except Exception as e:
        logger.error(f"❌ خطأ عام: {e}")

def start_bot():
    """
    Start the Telegram bot.
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 تم إيقاف البوت")

if __name__ == "__main__":
    start_bot()
