#!/usr/bin/env python3
"""
🤖 BraveBot Telegram Handlers
=============================
معالجات أوامر البوت مع دعم الذكاء الاصطناعي
"""

import logging
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# استيراد وحدات البوت المحلية
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database_manager import update_user_stats, get_user_stats
from core.compliance_checker import ComplianceChecker
from ai.trends_engine import RealTrendsFetcher, ViralTrendScanner

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# تهيئة محركات الترندات الحقيقية
real_trends_fetcher = RealTrendsFetcher()
real_viral_scanner = ViralTrendScanner()

class BraveBotHandlers:
    """كلاس معالجات البوت"""
    
    def __init__(self):
        self.compliance_checker = ComplianceChecker()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر البدء /start"""
        user = update.effective_user
        welcome_message = f"""
🤖 **مرحباً {user.first_name} في BraveBot!**

أنا بوت ذكي متخصص في فحص التوافق والتحليلات المتقدمة.

**📋 الأوامر المتاحة:**
• `/start` - رسالة الترحيب
• `/check` - فحص التوافق
• `/stats` - إحصائياتك الشخصية
• `/insights` - تحليلات ذكية أسبوعية ✨
• `/trends` - الترندات الفيروسية الحالية 🔥
• `/help` - المساعدة والدعم

**🚀 الجديد:** تم إضافة نظام الذكاء الاصطناعي للتحليلات المتقدمة!

أرسل أي رسالة لبدء الفحص 📝
        """
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
        
        # تحديث إحصائيات المستخدم
        await update_user_stats(user.id, user.username or "Unknown")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر المساعدة /help"""
        help_text = """
🆘 **مساعدة BraveBot**

**🔍 فحص التوافق:**
أرسل أي نص وسأقوم بفحصه للتأكد من توافقه مع المعايير المطلوبة.

**📊 الإحصائيات:**
استخدم `/stats` لعرض إحصائياتك الشخصية وإنجازاتك.

**🤖 الذكاء الاصطناعي:**
• `/insights` - تحليلات أسبوعية ذكية
• `/trends` - أحدث الترندات الفيروسية

**🏆 نظام الإنجازات:**
احصل على نقاط ومستويات جديدة مع كل فحص ناجح!

**🆘 تحتاج مساعدة؟**
تواصل مع فريق الدعم: @BraveBotSupport
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر الإحصائيات /stats"""
        user_id = update.effective_user.id
        
        try:
            # جلب إحصائيات المستخدم
            stats = await get_user_stats(user_id)
            
            if stats:
                total_checks, passed_checks = stats
                compliance_rate = (passed_checks / max(total_checks, 1)) * 100
                
                # تحديد مستوى الإنجاز
                if total_checks >= 500:
                    level = "🏅 بطل التوافق"
                elif total_checks >= 250:
                    level = "👑 أسطورة"
                elif total_checks >= 100:
                    level = "🚀 ماهر"
                elif total_checks >= 50:
                    level = "💎 خبير"
                elif total_checks >= 25:
                    level = "🏆 محترف"
                elif total_checks >= 10:
                    level = "⭐ خبير مبتدئ"
                elif total_checks >= 5:
                    level = "🔍 مبتدئ"
                else:
                    level = "🌱 أول خطوة"
                
                stats_message = f"""
📊 **إحصائياتك الشخصية**

**🔢 الأرقام:**
• إجمالي الفحوص: `{total_checks:,}`
• الفحوص الناجحة: `{passed_checks:,}`
• معدل التوافق: `{compliance_rate:.1f}%`

**🏆 مستوى الإنجاز:**
{level}

**📈 تقدمك:**
{"🟩" * min(10, max(1, int(compliance_rate/10)))}{"⬜" * max(0, 10-int(compliance_rate/10))} {compliance_rate:.1f}%

**💡 نصيحة:** استمر في إجراء الفحوص لتحسين مستواك!
                """
                
            else:
                stats_message = """
📊 **إحصائياتك الشخصية**

🌱 **مرحباً بك!**
لم تقم بإجراء أي فحوص بعد.

أرسل أي رسالة لبدء أول فحص لك! 🚀
                """
            
            await update.message.reply_text(stats_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"خطأ في جلب الإحصائيات: {e}")
            await update.message.reply_text("❌ حدث خطأ في جلب الإحصائيات، حاول مرة أخرى.")
    
    async def insights_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر التحليلات الذكية /insights"""
        await update.message.reply_text("🤖 **جاري تحليل البيانات...**\n⏳ يرجى الانتظار...")
        
        try:
            # جلب التحليلات الأسبوعية
            insights = await generate_weekly_insights()
            
            insights_message = f"""
🧠 **التحليلات الذكية الأسبوعية**
📅 **التاريخ:** {datetime.now().strftime('%Y-%m-%d')}

**📊 ملخص الأداء:**
• إجمالي الفحوص: `{insights.get('total_checks', 0):,}`
• معدل النجاح: `{insights.get('success_rate', 0):.1f}%`
• المستخدمين النشطين: `{insights.get('active_users', 0)}`

**🔥 أهم النتائج:**
{insights.get('key_findings', 'لا توجد نتائج متاحة حالياً')}

**💡 التوصيات:**
{insights.get('recommendations', 'سيتم إضافة التوصيات قريباً')}

**📈 التوجهات:**
{insights.get('trends_summary', 'تحليل التوجهات قيد التطوير')}

**🎯 هدف الأسبوع المقبل:**
تحسين معدل التوافق بنسبة 5% إضافية!

---
🤖 *تم إنتاج هذا التقرير بواسطة الذكاء الاصطناعي*
            """
            
            await update.message.reply_text(insights_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"خطأ في جلب التحليلات: {e}")
            await update.message.reply_text("""
❌ **عذراً، حدث خطأ في جلب التحليلات**

🔧 يعمل فريقنا على حل المشكلة.
🔄 حاول مرة أخرى خلال بضع دقائق.

📱 للمساعدة السريعة: `/help`
            """, parse_mode='Markdown')
    
    async def trends_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر الترندات الفيروسية /trends"""
        await update.message.reply_text("🔥 **جاري البحث عن أحدث الترندات...**\n⏳ يرجى الانتظار...")
        
        try:
            # جلب الترندات الفيروسية
            trends = await fetch_viral_trends(5)
            
            if trends:
                trends_message = "🔥 **أحدث الترندات الفيروسية**\n\n"
                
                for i, trend in enumerate(trends, 1):
                    trends_message += f"""
**{i}. {trend['icon']} {trend['keyword']}**
📊 النقاط: `{trend['score']}`
📈 النمو: `{trend['growth']}`
🌐 المنصة: `{trend['platform']}`
💰 الفرصة: `{trend.get('opportunity', 'متوسطة')}`

---
                    """
                
                trends_message += """
💡 **نصائح للاستفادة من الترندات:**
• ابحث عن المنتجات ذات النقاط العالية
• راقب معدل النمو السريع
• استهدف منصات متعددة

🤖 *يتم تحديث الترندات كل ساعة*
                """
                
            else:
                trends_message = """
🔥 **الترندات الفيروسية** (بيانات تجريبية)

**1. 📱 iPhone 15 Pro**
📊 النقاط: `95`
📈 النمو: `+150%`
🌐 المنصة: `TikTok`

**2. 🎧 AirPods Pro 3**
📊 النقاط: `88`
📈 النمو: `+120%`
🌐 المنصة: `Reddit`

**3. 💻 MacBook Air M3**
📊 النقاط: `82`
📈 النمو: `+95%`
🌐 المنصة: `Google Trends`

💡 هذه بيانات تجريبية - قريباً ستكون حقيقية!
                """
            
            await update.message.reply_text(trends_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"خطأ في جلب الترندات: {e}")
            await update.message.reply_text("❌ حدث خطأ في جلب الترندات، حاول مرة أخرى.")
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الرسائل النصية"""
        user_id = update.effective_user.id
        message_text = update.message.text
        
        if not message_text:
            await update.message.reply_text("⚠️ يرجى إرسال رسالة نصية للفحص.")
            return
        
        # إظهار رسالة "جاري الفحص"
        status_msg = await update.message.reply_text("🔍 **جاري فحص المحتوى...**\n⏳ يرجى الانتظار...")
        
        try:
            # إجراء فحص التوافق
            is_compliant, score, violations = await self.compliance_checker.check_compliance(message_text)
            
            # تحديث إحصائيات المستخدم
            await update_user_stats(user_id, update.effective_user.username or "Unknown")
            
            if is_compliant:
                result_message = f"""
✅ **فحص ناجح!**

📊 **النتيجة:** {score}/100
🎯 **الحالة:** متوافق مع المعايير
🏆 **النقاط المكتسبة:** +10

**📝 المحتوى المفحوص:**
"{message_text[:100]}{'...' if len(message_text) > 100 else ''}"

🎉 **تهانينا!** لقد اجتزت الفحص بنجاح.
                """
            else:
                violations_text = "\n".join([f"• {v}" for v in violations[:3]])
                result_message = f"""
❌ **فحص غير ناجح**

📊 **النتيجة:** {score}/100
⚠️ **المشاكل المكتشفة:**
{violations_text}

**💡 اقتراحات للتحسين:**
• راجع المحتوى وتأكد من خلوه من المخالفات
• استخدم لغة أكثر وضوحاً
• تجنب المصطلحات الحساسة

🔄 **حاول مرة أخرى بعد التعديل**
                """
            
            # حذف رسالة "جاري الفحص" وإرسال النتيجة
            await status_msg.delete()
            await update.message.reply_text(result_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"خطأ في فحص المحتوى: {e}")
            await status_msg.edit_text("❌ حدث خطأ أثناء الفحص، حاول مرة أخرى.")

    # تحديث دالة تحليل الترند المحددة
    async def analyze_specific_trend(update: Update, context: ContextTypes.DEFAULT_TYPE, keyword: str):
        """تحليل ترند محدد باستخدام البيانات الحقيقية"""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name or "صديقي"
        
        try:
            # رسالة انتظار محسنة
            processing_msg = await update.message.reply_text(
                f"🔍 **جاري تحليل الترند: `{keyword}`**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📊 **مصادر البيانات الحقيقية:**\n"
                f"• 🌐 Google Trends API\n"
                f"• 👥 Reddit Communities API\n"
                f"• 🔥 حساب نقاط الانتشار الذكية\n\n"
                f"⏳ **يرجى الانتظار... (15-30 ثانية)**"
            , parse_mode="Markdown")
            
            # تحليل الترند باستخدام البيانات الحقيقية
            analysis_report = real_trends_fetcher.analyze_combined_trends_real(keyword)
            
            # حذف رسالة الانتظار
            await processing_msg.delete()
            
            # بناء رسالة النتائج المحسنة
            await send_real_trend_analysis_result(update, analysis_report)
            
            # تسجيل العملية مع تفاصيل إضافية
            data_source = analysis_report.get('data_freshness', 'unknown')
            viral_score = analysis_report['overall_viral_score']
            add_log(f"User {user_id} analyzed REAL trend: '{keyword}' - Score: {viral_score} - Source: {data_source}", user_id=user_id)
            
        except Exception as e:
            add_log(f"Error in real trend analysis '{keyword}': {str(e)}", level="ERROR", user_id=user_id)
            try:
                await processing_msg.delete()
            except:
                pass
            
            await update.message.reply_text(
                f"❌ **فشل في تحليل الترند الحقيقي**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🔧 **أسباب محتملة:**\n"
                f"• انقطاع الاتصال بـ Google Trends\n"
                f"• مشكلة في Reddit API\n"
                f"• حد أقصى للطلبات اليومية\n"
                f"• كلمة مفتاحية غير مدعومة\n\n"
                f"💡 **الحلول:**\n"
                f"• جرب كلمة مفتاحية شائعة (مثل: iPhone, Tesla)\n"
                f"• انتظر بضع دقائق وأعد المحاولة\n"
                f"• تحقق من الإملاء باللغة الإنجليزية\n\n"
                f"🔄 **للمحاولة مرة أخرى:** `/trends {keyword}`\n"
                f"📊 **للترندات السريعة:** `/trends hot`"
            , parse_mode="Markdown")

    async def send_real_trend_analysis_result(update: Update, analysis_report: Dict[str, Any]):
        """إرسال نتائج تحليل الترند الحقيقي بتنسيق محسن"""
        
        keyword = analysis_report['keyword']
        viral_score = analysis_report['overall_viral_score']
        trend_category = analysis_report['trend_category']
        trend_direction = analysis_report.get('trend_direction', 'مستقر')
        data_freshness = analysis_report.get('data_freshness', 'unknown')
        google_trends = analysis_report['google_trends']
        reddit_trends = analysis_report['reddit_trends']
        recommendations = analysis_report['recommendations']
        api_status = analysis_report.get('api_status', {})
        
        # رموز الاتجاه
        direction_emoji = {
            "صاعد بقوة": "🚀", "صاعد": "📈", 
            "مستقر": "➡️", "هابط": "📉"
        }
        
        # رموز مصدر البيانات
        freshness_emoji = {
            "real-time": "🔴 مباشر", 
            "cached": "🟡 محفوظ", 
            "mock": "⚪ تجريبي"
        }
        
        # بناء الرسالة الرئيسية
        result_message = (
            f"🔥 **تحليل الترند الحقيقي – `{keyword}`**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🎯 **النتيجة الشاملة:**\n"
            f"⭐ **نقاط الانتشار:** `{viral_score}/100`\n"
            f"📊 **تصنيف الترند:** {trend_category}\n"
            f"📈 **الاتجاه:** {direction_emoji.get(trend_direction, '📊')} {trend_direction}\n"
            f"🕒 **تحديث البيانات:** {freshness_emoji.get(data_freshness, '⚪ تجريبي')}\n\n"
            f"📊 **تفاصيل الترند:**\n"
            f"• **Google Trends:** {google_trends.get('trend_line', 'لا توجد بيانات')}\n"
            f"• **Reddit Trends:** {reddit_trends.get('top_posts', 'لا توجد بيانات')}\n\n"
            f"💡 **التوصيات:**\n"
            f"{recommendations.get('actionable_insights', 'لا توجد توصيات متاحة')}\n\n"
            f"🔗 **المصادر:** {api_status.get('source_credits', 'غير محددة')}\n"
            f"📅 **تاريخ التحليل:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"---\n"
            f"🤖 *تم تحليل هذا الترند باستخدام الذكاء الاصطناعي المتقدم*\n"
            f"📈 *للحصول على تحليل أعمق، استخدم البيانات الحقيقية من Google وReddit*"
        )
        
        # إرسال الرسالة
        await update.message.reply_text(result_message, parse_mode='Markdown')

def register_handlers(application: Application):
    """تسجيل معالجات البوت"""
    handlers = BraveBotHandlers()
    
    # تسجيل الأوامر
    application.add_handler(CommandHandler("start", handlers.start_command))
    application.add_handler(CommandHandler("help", handlers.help_command))
    application.add_handler(CommandHandler("stats", handlers.stats_command))
    application.add_handler(CommandHandler("insights", handlers.insights_command))
    application.add_handler(CommandHandler("trends", handlers.trends_command))
    
    # تسجيل معالج الرسائل النصية
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.message_handler))
    
    logger.info("✅ تم تسجيل جميع معالجات البوت بنجاح")
