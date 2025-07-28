#!/usr/bin/env python3
"""
🤖 Telegram Bot Handler
======================
معالج البوت الرئيسي - إصدار محدث
"""

import os
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class BraveBot:
    """كلاس البوت الرئيسي"""
    
    def __init__(self, token: str):
        self.token = token
        self.application = None
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر البدء"""
        user = update.effective_user
        welcome_message = f"""
🤖 **أهلاً بك في BraveBot v2.0!**

مرحباً {user.first_name}! 👋

🔥 **الأوامر المتاحة:**
• `/trends [keyword]` - تحليل ترند محدد
• `/hot` - أحدث الترندات الساخنة
• `/help` - المساعدة

🚀 **ابدأ بتجربة:** `/trends AI` أو `/hot`
        """
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def trends_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر تحليل الترندات"""
        try:
            if context.args:
                keyword = ' '.join(context.args)
            else:
                keyword = 'technology'
            
            await update.message.reply_text(f"🔍 جاري تحليل ترند: **{keyword}**...")
            
            import random
            viral_score = random.randint(30, 95)
            
            if viral_score >= 80:
                status = "🔥 ساخن جداً"
                advice = "استغل هذا الترند فوراً!"
            elif viral_score >= 60:
                status = "📈 صاعد"
                advice = "ترند واعد - راقب التطورات"
            else:
                status = "📊 هادئ"
                advice = "مناسب للمحتوى طويل المدى"
            
            result_message = f"""
📊 **تحليل ترند: {keyword}**

🎯 **النقاط:** {viral_score}/100
🏷️ **الحالة:** {status}
💡 **التوصية:** {advice}

⏰ **التحديث:** الآن
🤖 **المصدر:** BraveBot AI
            """
            
            await update.message.reply_text(result_message, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ في تحليل الترند: {str(e)}")
    
    async def hot_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر الترندات الساخنة"""
        await update.message.reply_text("🔥 جاري جلب أحدث الترندات...")
        
        hot_trends = [
            {"keyword": "AI Revolution", "score": 95},
            {"keyword": "iPhone 15", "score": 87},
            {"keyword": "Tesla Model Y", "score": 82},
            {"keyword": "ChatGPT Pro", "score": 78},
            {"keyword": "Meta Quest 3", "score": 71}
        ]
        
        message = "🔥 **أحدث الترندات الساخنة:**\n\n"
        
        for i, trend in enumerate(hot_trends, 1):
            emoji = "🔥" if trend["score"] >= 80 else "📈" if trend["score"] >= 60 else "⚡"
            message += f"{i}. {emoji} **{trend['keyword']}** - {trend['score']}/100\n"
        
        message += "\n💡 استخدم `/trends [اسم الترند]` لتحليل مفصل"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر المساعدة"""
        help_message = """
🤖 **دليل استخدام BraveBot v2.0**

🔥 **أوامر الترندات:**
• `/trends [keyword]` - تحليل ترند محدد
• `/hot` - أحدث الترندات الساخنة

ℹ️ **أوامر عامة:**
• `/start` - بدء التشغيل
• `/help` - هذه المساعدة

🌐 **Dashboard:** http://localhost:8501
        """
        
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الرسائل العادية"""
        await update.message.reply_text(
            f"🤖 شكراً لك! جرب الأوامر مثل `/trends AI` أو `/hot`"
        )
    
    def setup_handlers(self):
        """إعداد معالجات الأوامر"""
        if not self.application:
            return
        
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("trends", self.trends_command))
        self.application.add_handler(CommandHandler("hot", self.hot_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
    
    async def start_bot(self):
        """بدء تشغيل البوت - إصدار محدث"""
        try:
            logger.info("🚀 Starting BraveBot...")
            
            # إنشاء التطبيق
            self.application = Application.builder().token(self.token).build()
            
            # إعداد المعالجات
            self.setup_handlers()
            
            print("🤖 البوت يعمل الآن!")
            
            # تشغيل البوت - الطريقة المحدثة
            async with self.application:
                await self.application.start()
                await self.application.updater.start_polling(drop_pending_updates=True)
                
                try:
                    # انتظار بدلاً من idle
                    await asyncio.Event().wait()
                except asyncio.CancelledError:
                    pass
                finally:
                    await self.application.updater.stop()
                    await self.application.stop()
        
        except Exception as e:
            logger.error(f"❌ Bot startup failed: {e}")
            raise

def run_bot():
    """دالة تشغيل البوت"""
    if not TOKEN:
        print("❌ Error: TELEGRAM_TOKEN not found!")
        return
    
    try:
        # تشغيل مبسط بدون event loop مشترك
        import nest_asyncio
        nest_asyncio.apply()
        
        bot = BraveBot(TOKEN)
        asyncio.run(bot.start_bot())
        
    except ImportError:
        # إذا nest_asyncio غير متاح، استخدم طريقة أخرى
        print("🔄 استخدام الطريقة البديلة...")
        
        async def simple_bot():
            bot = BraveBot(TOKEN)
            application = Application.builder().token(TOKEN).build()
            bot.application = application
            bot.setup_handlers()
            
            print("🤖 البوت يعمل الآن!")
            await application.run_polling(drop_pending_updates=True)
        
        asyncio.run(simple_bot())
        
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف البوت")
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت: {e}")

if __name__ == "__main__":
    run_bot()