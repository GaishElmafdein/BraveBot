#!/usr/bin/env python3
"""
BraveBot Telegram Bot
====================
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر البدء"""
    
    welcome_message = """🤖 أهلاً بك في BraveBot AI Commerce Empire!

🎯 الأوامر المتاحة:
/trends - تحليل الترندات
/price - اقتراح الأسعار  
/insights - رؤى السوق
/help - المساعدة

💡 أرسل أي كلمة مفتاحية لتحليلها!"""
    
    await update.message.reply_text(welcome_message)

async def trends_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر تحليل الترندات"""
    
    try:
        keyword = " ".join(context.args) if context.args else "gaming"
        
        await update.message.reply_text(f"🔍 جاري تحليل '{keyword}'...")
        
        from ai.trends_engine import fetch_viral_trends
        result = fetch_viral_trends(keyword, 5)
        
        response = f"📊 تحليل الترندات لـ: {keyword}\n\n"
        
        for i, trend in enumerate(result.get('top_keywords', [])[:3], 1):
            response += f"{i}. 🎯 {trend['keyword']}\n"
            response += f"   📈 النقاط: {trend['viral_score']}%\n"
            response += f"   🔗 المصدر: {trend.get('source', 'AI Analysis')}\n\n"
        
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Trends command error: {e}")
        await update.message.reply_text("❌ حدث خطأ في تحليل الترندات")

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر اقتراح الأسعار"""
    
    try:
        if context.args:
            base_price = float(context.args[0])
        else:
            base_price = 19.99
        
        await update.message.reply_text("💰 جاري حساب السعر المقترح...")
        
        from ai.trends_engine import dynamic_pricing_suggestion
        pricing = dynamic_pricing_suggestion(base_price, 75)
        
        response = f"💰 اقتراح التسعير:\n\n"
        response += f"💵 السعر الأساسي: ${pricing['base_price']:.2f}\n"
        response += f"🚀 السعر المقترح: ${pricing['suggested_price']:.2f}\n"
        response += f"📈 هامش الربح: {pricing['profit_margin']:.1f}%\n"
        response += f"⭐ التقييم: {pricing.get('recommendation', 'جيد')}"
        
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Price command error: {e}")
        await update.message.reply_text("❌ حدث خطأ في اقتراح السعر")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الرسائل النصية"""
    
    try:
        keyword = update.message.text.strip()
        
        if len(keyword) > 50:
            await update.message.reply_text("❌ الكلمة المفتاحية طويلة جداً")
            return
        
        await update.message.reply_text(f"🔍 جاري تحليل '{keyword}'...")
        
        from ai.trends_engine import fetch_viral_trends
        result = fetch_viral_trends(keyword, 3)
        
        if result.get('top_keywords'):
            trend = result['top_keywords'][0]
            
            response = f"📊 تحليل سريع لـ: {keyword}\n\n"
            response += f"🎯 أفضل نتيجة: {trend['keyword']}\n"
            response += f"📈 النقاط الفيروسية: {trend['viral_score']}%\n"
            
            from ai.trends_engine import dynamic_pricing_suggestion
            pricing = dynamic_pricing_suggestion(19.99, trend['viral_score'])
            
            response += f"\n💰 سعر مقترح: ${pricing['suggested_price']:.2f}\n"
            response += f"📊 التوصية: {pricing.get('recommendation', 'متابعة')}"
            
        else:
            response = f"❌ لم أجد بيانات كافية عن '{keyword}'"
        
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Message handler error: {e}")
        await update.message.reply_text("❌ حدث خطأ في المعالجة")

async def create_bot_application():
    """إنشاء تطبيق البوت"""
    
    token = os.getenv('TELEGRAM_TOKEN')
    if not token:
        raise ValueError("TELEGRAM_TOKEN not found in environment variables")
    
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("trends", trends_command))
    application.add_handler(CommandHandler("price", price_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    return application

if __name__ == "__main__":
    import asyncio
    
    async def main():
        app = await create_bot_application()
        await app.run_polling()
    
    asyncio.run(main())