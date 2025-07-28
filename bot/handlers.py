from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from datetime import datetime
import logging
import sys
import os

# إضافة المسار للوصول لمجلد الترندات
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# استيراد محرك الترندات الحقيقي
try:
    from trends.trend_fetcher import TrendsFetcher
    from trends.viral_scanner import ViralScanner
    REAL_TRENDS_AVAILABLE = True
except ImportError as e:
    logging.error(f"❌ خطأ في استيراد محرك الترندات: {e}")
    REAL_TRENDS_AVAILABLE = False

# إعداد السجل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

async def handle_trends_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أوامر الترندات - بيانات حقيقية فقط"""
    
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    keyword = ' '.join(context.args) if context.args else 'technology'
    
    logger.info(f"🔍 Real trends request from {username} (ID: {user_id}) - Keyword: {keyword}")
    
    # رسالة البحث
    search_message = await update.message.reply_text(
        f"🔍 **جاري البحث عن ترندات حقيقية:** {keyword}\n⏳ جاري الاتصال بـ APIs...",
        parse_mode='Markdown'
    )
    
    try:
        # التحقق من توفر محرك الترندات
        if not REAL_TRENDS_AVAILABLE:
            await search_message.edit_text(
                "❌ **خطأ في النظام**\n\n"
                "محرك الترندات غير متاح حالياً.\n"
                "تأكد من تثبيت جميع المتطلبات وإعادة تشغيل البوت.\n\n"
                f"🕒 {datetime.now().strftime('%H:%M - %d/%m/%Y')}",
                parse_mode='Markdown'
            )
            return
        
        # إنشاء محركات البحث
        trends_fetcher = TrendsFetcher()
        viral_scanner = ViralScanner()
        
        # محاولة جلب البيانات الحقيقية
        logger.info(f"📡 Fetching real data for: {keyword}")
        
        try:
            # Google Trends
            await search_message.edit_text(
                f"🔍 **جاري البحث:** {keyword}\n📊 جاري الاتصال بـ Google Trends...",
                parse_mode='Markdown'
            )
            
            google_data = await get_google_trends_real(trends_fetcher, keyword)
            
            # Reddit Trends
            await search_message.edit_text(
                f"🔍 **جاري البحث:** {keyword}\n🗨️ جاري الاتصال بـ Reddit...",
                parse_mode='Markdown'
            )
            
            reddit_data = await get_reddit_trends_real(viral_scanner, keyword)
            
            # التحقق من وجود بيانات حقيقية
            if not google_data and not reddit_data:
                await search_message.edit_text(
                    f"❌ **لا توجد بيانات حقيقية**\n\n"
                    f"لم يتم العثور على أي ترندات حقيقية للكلمة: **{keyword}**\n\n"
                    "💡 **اقتراحات:**\n"
                    "• جرب كلمة مفتاحية باللغة الإنجليزية\n"
                    "• استخدم كلمات أكثر شيوعاً\n"
                    "• تأكد من الاتصال بالإنترنت\n\n"
                    f"🕒 {datetime.now().strftime('%H:%M - %d/%m/%Y')}",
                    parse_mode='Markdown'
                )
                return
            
            # تكوين الرد النهائي
            response = format_real_trends_response(google_data, reddit_data, keyword)
            
            # إرسال النتائج
            await search_message.edit_text(response, parse_mode='Markdown')
            
            logger.info(f"✅ Successfully sent REAL trends to {username}")
            
        except Exception as api_error:
            logger.error(f"❌ API Error for {username}: {api_error}")
            
            await search_message.edit_text(
                f"❌ **خطأ في الاتصال بـ APIs**\n\n"
                f"فشل في جلب البيانات الحقيقية للكلمة: **{keyword}**\n\n"
                f"**تفاصيل الخطأ:** {str(api_error)[:100]}...\n\n"
                "🔄 **حلول مقترحة:**\n"
                "• جرب مرة أخرى بعد دقائق\n"
                "• استخدم كلمة مفتاحية مختلفة\n"
                "• تحقق من حالة APIs\n\n"
                f"🕒 {datetime.now().strftime('%H:%M - %d/%m/%Y')}",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"❌ Critical error in trends handler for {username}: {e}")
        
        await update.message.reply_text(
            "❌ **خطأ حرج في النظام**\n\n"
            "حدث خطأ غير متوقع في معالج الترندات.\n"
            "يرجى إبلاغ المطور وإعادة المحاولة لاحقاً.\n\n"
            f"🆔 معرف الخطأ: {str(e)[:50]}\n"
            f"🕒 {datetime.now().strftime('%H:%M - %d/%m/%Y')}",
            parse_mode='Markdown'
        )

async def get_google_trends_real(trends_fetcher, keyword: str) -> list:
    """جلب البيانات الحقيقية من Google Trends فقط"""
    
    try:
        # استخدام محرك الترندات الحقيقي
        result = trends_fetcher.get_trending_keywords(keyword, timeframe='today 3-m')
        
        if result and isinstance(result, list) and len(result) > 0:
            logger.info(f"✅ Got {len(result)} real Google trends")
            return result
        else:
            logger.warning("⚠️ Google Trends returned empty results")
            return []
            
    except Exception as e:
        logger.error(f"❌ Google Trends API failed: {e}")
        return []

async def get_reddit_trends_real(viral_scanner, keyword: str) -> list:
    """جلب البيانات الحقيقية من Reddit فقط"""
    
    try:
        # استخدام ماسح Reddit الحقيقي
        result = viral_scanner.scan_reddit_trends(keyword, limit=5)
        
        if result and isinstance(result, list) and len(result) > 0:
            logger.info(f"✅ Got {len(result)} real Reddit trends")
            return result
        else:
            logger.warning("⚠️ Reddit API returned empty results")
            return []
            
    except Exception as e:
        logger.error(f"❌ Reddit API failed: {e}")
        return []

def format_real_trends_response(google_data: list, reddit_data: list, keyword: str) -> str:
    """تنسيق رد الترندات الحقيقية فقط"""
    
    response = f"🔥 **ترندات {keyword}** - بيانات حقيقية 100%\n\n"
    
    # إحصائيات المصادر
    response += f"📊 **مصادر البيانات:**\n"
    response += f"• Google Trends: {len(google_data)} نتيجة\n"
    response += f"• Reddit: {len(reddit_data)} نتيجة\n\n"
    
    # Google Trends الحقيقية
    if google_data:
        response += "🌐 **Google Trends (حقيقية):**\n"
        for i, trend in enumerate(google_data[:5], 1):
            if isinstance(trend, dict):
                title = trend.get('title', trend.get('keyword', 'غير محدد'))
                interest = trend.get('interest_score', trend.get('value', 0))
                response += f"{i}. **{title}**\n"
                response += f"   📈 درجة الاهتمام: {interest}\n"
            else:
                response += f"{i}. **{str(trend)}**\n"
        response += "\n"
    
    # Reddit Trends الحقيقية
    if reddit_data:
        response += "🗨️ **Reddit Trends (حقيقية):**\n"
        for i, trend in enumerate(reddit_data[:3], 1):
            if isinstance(trend, dict):
                title = trend.get('title', 'غير محدد')[:60]
                score = trend.get('score', trend.get('ups', 0))
                comments = trend.get('num_comments', trend.get('comments', 0))
                response += f"{i}. **{title}...**\n"
                response += f"   👍 {score} | 💬 {comments}\n"
            else:
                response += f"{i}. **{str(trend)[:60]}...**\n"
        response += "\n"
    
    # تحليل الانتشار الحقيقي
    total_engagement = sum([
        len(google_data) * 10,  # وزن Google Trends
        sum(t.get('score', 0) if isinstance(t, dict) else 0 for t in reddit_data) // 100  # وزن Reddit
    ])
    
    if total_engagement > 50:
        viral_status = "🔥 ساخن جداً"
        recommendations = [
            "استغل هذا الترند فوراً!",
            "انشر محتوى متعلق بهذا الموضوع",
            "راقب المنافسين في هذا المجال"
        ]
    elif total_engagement > 20:
        viral_status = "📈 صاعد"
        recommendations = [
            "ترند واعد - راقب التطورات",
            "فكر في استراتيجية متوسطة المدى",
            "ابحث عن زوايا إبداعية"
        ]
    else:
        viral_status = "📊 هادئ"
        recommendations = [
            "مناسب للمحتوى طويل المدى",
            "ابحث عن틈새 markets",
            "ابني خبرة في هذا المجال"
        ]
    
    response += f"🎯 **تقييم الانتشار:** {viral_status}\n"
    response += f"⚡ **درجة التفاعل:** {total_engagement}/100\n\n"
    
    response += "💡 **توصيات حقيقية:**\n"
    for rec in recommendations:
        response += f"• {rec}\n"
    
    response += f"\n---\n"
    response += f"✅ **بيانات حقيقية 100%** - لا mock data\n"
    response += f"🕒 {datetime.now().strftime('%H:%M - %d/%m/%Y')}\n"
    response += f"🤖 **BraveBot** - Real Data Only"
    
    return response

async def handle_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر البداية"""
    
    welcome_message = """
🤖 **مرحباً بك في BraveBot!**

🔥 **محلل الترندات الحقيقية**

✅ **المميزات:**
• بيانات حقيقية 100% من Google Trends و Reddit
• لا توجد بيانات وهمية أو تجريبية
• تحليل متقدم للترندات الساخنة
• توصيات استراتيجية دقيقة

🎯 **الأوامر المتاحة:**
• `/trends [كلمة مفتاحية]` - تحليل الترندات
• `/test` - اختبار البوت
• `/help` - المساعدة

💡 **مثال:** `/trends iPhone 15`

---
⚠️ **ملاحظة:** يعتمد البوت على البيانات الحقيقية فقط
"""
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def handle_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر المساعدة"""
    
    help_message = """
📚 **دليل استخدام BraveBot**

🔍 **أمر الترندات:**
`/trends [كلمة مفتاحية]`

**أمثلة:**
• `/trends iPhone 15` - ترندات الآيفون
• `/trends cryptocurrency` - العملات الرقمية
• `/trends artificial intelligence` - الذكاء الاصطناعي

⚠️ **مهم:**
• استخدم كلمات باللغة الإنجليزية للحصول على أفضل النتائج
• البوت يجلب بيانات حقيقية فقط
• قد يستغرق البحث 10-30 ثانية

🔧 **أوامر أخرى:**
• `/test` - اختبار حالة البوت
• `/start` - رسالة الترحيب

❌ **في حالة عدم وجود نتائج:**
• جرب كلمة مفتاحية أخرى
• تأكد من الاتصال بالإنترنت
• انتظر قليلاً ثم حاول مرة أخرى
"""
    
    await update.message.reply_text(help_message, parse_mode='Markdown')

async def handle_test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر اختبار البوت"""
    
    test_message = f"""
🧪 **اختبار البوت - Real Data Only**

✅ **حالة البوت:** نشط
📡 **الاتصال:** مستقر  
🔄 **معالجة الأوامر:** تعمل
🌐 **محرك الترندات:** {'✅ متاح' if REAL_TRENDS_AVAILABLE else '❌ غير متاح'}
📊 **وضع البيانات:** حقيقية فقط (No Mock)

🎯 **جرب الآن:**
• `/trends Bitcoin`
• `/trends Tesla`
• `/trends ChatGPT`

⏰ **الوقت:** {datetime.now().strftime('%H:%M:%S - %d/%m/%Y')}
🔥 **الإصدار:** Real Data Only v2.0
"""
    
    await update.message.reply_text(test_message, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الرسائل النصية"""
    
    text = update.message.text.lower()
    
    if 'trends' in text or 'ترند' in text:
        await update.message.reply_text(
            "🔍 لتحليل الترندات، استخدم:\n`/trends [كلمة مفتاحية]`\n\n"
            "مثال: `/trends iPhone 15`",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "👋 مرحباً! استخدم `/help` لمعرفة الأوامر المتاحة"
        )

def register_handlers(application):
    """تسجيل جميع المعالجات"""
    
    # الأوامر الأساسية
    application.add_handler(CommandHandler("start", handle_start_command))
    application.add_handler(CommandHandler("help", handle_help_command))
    application.add_handler(CommandHandler("test", handle_test_command))
    
    # أمر الترندات الحقيقية
    application.add_handler(CommandHandler("trends", handle_trends_command))
    
    # معالج الرسائل النصية
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("✅ تم تسجيل جميع المعالجات - Real Data Only Mode")