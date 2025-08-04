#!/usr/bin/env python3
"""
📱 BraveBot Telegram Bot Module
===============================
وحدة بوت التليجرام (بدون تضارب أسماء)
"""

__version__ = "2.0.0"

# استيراد آمن من مكتبة python-telegram-bot
try:
    from telegram import Update, Bot
    from telegram.ext import Application, CommandHandler, MessageHandler, filters
    
    TELEGRAM_LIBRARY_AVAILABLE = True
    print("📱 python-telegram-bot library loaded successfully!")
    
except ImportError as e:
    print(f"❌ python-telegram-bot not available: {e}")
    TELEGRAM_LIBRARY_AVAILABLE = False

def create_bot_application():
    """إنشاء تطبيق البوت"""
    import os
    
    if not TELEGRAM_LIBRARY_AVAILABLE:
        raise ImportError("python-telegram-bot library not available")
    
    token = os.getenv('TELEGRAM_TOKEN')
    if not token:
        raise ValueError("TELEGRAM_TOKEN not found in environment")
    
    # إنشاء التطبيق
    application = Application.builder().token(token).build()
    
    # معالج أمر /start
    async def start_command(update: Update, context):
        """معالج أمر /start"""
        await update.message.reply_text(
            "🤖 **BraveBot AI Commerce Empire v2.0**\n\n"
            "مرحباً بك في عالم التجارة الذكية! 🚀\n\n"
            "**🔥 الأوامر المتاحة:**\n"
            "/start - بدء استخدام البوت\n"
            "/help - عرض المساعدة\n"
            "/trends <منتج> - تحليل ترندات منتج\n"
            "/viral - اكتشاف المنتجات الفيروسية\n"
            "/dashboard - رابط لوحة التحكم\n\n"
            "**📊 Dashboard:** http://localhost:8501\n\n"
            "تطوير: BraveBot Team 🎯",
            parse_mode='Markdown'
        )
        print(f"✅ /start command used by {update.effective_user.first_name}")
    
    # معالج أمر /help
    async def help_command(update: Update, context):
        """معالج أمر /help"""
        help_text = """
🤖 **BraveBot - دليل الاستخدام**

**🔥 أوامر التحليل:**
• `/trends <منتج>` - تحليل ترندات منتج محدد
• `/viral` - اكتشاف أهم المنتجات الفيروسية
• `/market` - تحليل السوق العام

**💰 أوامر التسعير:**
• `/price` - حاسبة التسعير الذكي
• `/profit` - حساب هامش الربح

**📊 أوامر المعلومات:**
• `/stats` - إحصائياتك الشخصية
• `/dashboard` - رابط لوحة التحكم
• `/about` - حول البوت

**🎯 مثال على الاستخدام:**
`/trends gaming mouse`
`/viral`

للمزيد من المميزات، استخدم Dashboard: http://localhost:8501
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    # معالج أمر /trends
    async def trends_command(update: Update, context):
        """معالج أمر /trends"""
        if not context.args:
            await update.message.reply_text(
                "🔍 **تحليل الترندات**\n\n"
                "الاستخدام: `/trends <اسم المنتج>`\n"
                "مثال: `/trends wireless headphones`",
                parse_mode='Markdown'
            )
            return
        
        keyword = ' '.join(context.args)
        loading_msg = await update.message.reply_text("🔄 جاري تحليل الترندات...")
        
        try:
            # استيراد محرك الترندات
            from ai.trends_engine import fetch_viral_trends
            
            # تحليل الترندات
            result = fetch_viral_trends(keyword, 3)
            
            if result and result.get('top_keywords'):
                response = f"🔥 **تحليل ترندات: {keyword}**\n\n"
                
                for i, trend in enumerate(result['top_keywords'][:3]):
                    emoji = ["🥇", "🥈", "🥉"][i]
                    response += f"{emoji} **{trend['keyword']}**\n"
                    response += f"🔥 النتيجة الفيروسية: {trend['viral_score']}%\n"
                    response += f"📊 المنافسة: {trend.get('competition', 'متوسطة')}\n"
                    response += f"💰 إمكانية الربح: {trend.get('profit_potential', 75)}%\n\n"
                
                # التوصية
                avg_score = result.get('avg_viral_score', 0)
                if avg_score > 70:
                    response += "✅ **التوصية:** ممتاز للاستثمار! 🎯"
                elif avg_score > 50:
                    response += "🟡 **التوصية:** جيد مع مراقبة السوق 👍"
                else:
                    response += "🔴 **التوصية:** يحتاج المزيد من البحث ⚠️"
                
            else:
                response = f"⚠️ لم يتم العثور على ترندات قوية لـ '{keyword}'\n\nجرب كلمات مختلفة أو أكثر تحديداً."
            
            await loading_msg.edit_text(response, parse_mode='Markdown')
            print(f"✅ Trends analysis for '{keyword}' completed")
            
        except Exception as e:
            await loading_msg.edit_text(
                f"❌ خطأ في تحليل الترندات: {str(e)}\n\n"
                "💡 تأكد من الاتصال بالإنترنت وجرب مرة أخرى."
            )
            print(f"❌ Trends analysis error: {e}")
    
    # معالج أمر /viral
    async def viral_command(update: Update, context):
        """معالج أمر /viral"""
        loading_msg = await update.message.reply_text("🔄 جاري البحث عن المنتجات الفيروسية...")
        
        try:
            from ai.trends_engine import fetch_viral_trends
            
            # البحث عن منتجات فيروسية
            viral_categories = ["electronics", "fashion", "home", "gaming", "fitness"]
            all_results = []
            
            for category in viral_categories:
                result = fetch_viral_trends(category, 1)
                if result and result.get('top_keywords'):
                    all_results.extend(result['top_keywords'])
            
            # ترتيب النتائج
            all_results.sort(key=lambda x: x['viral_score'], reverse=True)
            top_viral = all_results[:5]
            
            if top_viral:
                response = "🔥 **أهم المنتجات الفيروسية الآن:**\n\n"
                
                emojis = ["🥇", "🥈", "🥉", "🏅", "⭐"]
                for i, item in enumerate(top_viral):
                    response += f"{emojis[i]} **{item['keyword']}**\n"
                    response += f"🔥 النتيجة: {item['viral_score']}%\n"
                    response += f"💰 الربح المحتمل: {item.get('profit_potential', 75)}%\n\n"
                
                response += "💡 **نصيحة:** ركز على المنتجات ذات النتيجة +75%!"
                
            else:
                response = "⚠️ لا توجد منتجات فيروسية قوية حالياً.\n\nجرب مرة أخرى لاحقاً."
            
            await loading_msg.edit_text(response, parse_mode='Markdown')
            print("✅ Viral products analysis completed")
            
        except Exception as e:
            await loading_msg.edit_text(
                f"❌ خطأ في البحث عن المنتجات الفيروسية: {str(e)}"
            )
            print(f"❌ Viral analysis error: {e}")
    
    # معالج أمر /dashboard
    async def dashboard_command(update: Update, context):
        """معالج أمر /dashboard"""
        dashboard_text = """
📊 **BraveBot Dashboard**

🌐 **رابط لوحة التحكم:**
http://localhost:8501

**🎯 المميزات المتاحة:**
• 🔍 تحليل الترندات المتقدم
• 💰 حاسبة التسعير الذكي
• 📈 تحليلات السوق التفاعلية
• 🏆 نظام الإنجازات
• 📊 إحصائيات مفصلة

**💡 تأكد من تشغيل Dashboard قبل فتح الرابط!**
        """
        
        await update.message.reply_text(dashboard_text, parse_mode='Markdown')
    
    # إضافة المعالجات
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("trends", trends_command))
    application.add_handler(CommandHandler("viral", viral_command))
    application.add_handler(CommandHandler("dashboard", dashboard_command))
    
    print("🤖 Bot application created with all handlers!")
    return application

# معلومات الوحدة
MODULE_INFO = {
    "name": "BraveBot Telegram Bot Interface",
    "version": __version__,
    "library_available": TELEGRAM_LIBRARY_AVAILABLE
}

if __name__ == "__main__":
    print("📱 Testing Telegram Bot Module...")
    
    if TELEGRAM_LIBRARY_AVAILABLE:
        print("✅ Module ready for bot creation!")
        
        try:
            app = create_bot_application()
            print("✅ Bot application created successfully!")
        except Exception as e:
            print(f"❌ Bot creation failed: {e}")
    else:
        print("❌ Module not ready - install python-telegram-bot")