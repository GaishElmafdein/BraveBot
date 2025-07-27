import os
import yaml
import asyncio
import csv
import io
from datetime import datetime, timedelta
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

from dotenv import load_dotenv
load_dotenv()

# ===== تحميل الإعدادات =====
try:
    with open("config/config.yaml", "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
except FileNotFoundError:
    config = {}

# ===== إعدادات الإنجازات =====
ACHIEVEMENTS = [
    {"count": 1, "title": "أول خطوة", "desc": "أول فحص للمنتج", "icon": "🌱"},
    {"count": 5, "title": "مبتدئ", "desc": "5 فحوصات", "icon": "🔍"},
    {"count": 10, "title": "خبير مبتدئ", "desc": "10 فحوصات", "icon": "⭐"},
    {"count": 25, "title": "محترف", "desc": "25 فحص", "icon": "🏆"},
    {"count": 50, "title": "خبير", "desc": "50 فحص", "icon": "💎"},
    {"count": 100, "title": "ماهر", "desc": "100 فحص", "icon": "🚀"},
    {"count": 250, "title": "أسطورة", "desc": "250 فحص", "icon": "👑"},
    {"count": 500, "title": "بطل التوافق", "desc": "500 فحص", "icon": "🏅"}
]

# ===== استدعاءات من core =====
from core.database_manager import (
    get_user_stats, update_user_stats, add_log,
    export_user_stats, reset_user_stats
)
from core.compliance_checker import check_product_compliance

# ===== تحميل الإعدادات =====
try:
    with open("config/config.yaml", "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
except FileNotFoundError:
    config = {
        "max_price": 10000,
        "min_price": 0.01,
        "admin_ids": [],
        "rate_limit": {"checks_per_hour": 50, "checks_per_day": 200},
    }

TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_IDS = config.get("admin_ids", [])

ASK_NAME, ASK_PRICE = range(2)

# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name or "مستخدم"
    welcome_msg = (
        f"🎉 **أهلاً وسهلاً {user_name}!**\n\n"
        f"🤖 **BraveBot** - فاحص المنتجات الذكي\n"
        f"✨ **مصمم خصيصاً لاستخدامك الشخصي!**\n\n"
        f"� **الأوامر الأساسية:**\n"
        f"�🔍 /compliance - فحص منتج جديد\n"
        f"📊 /stats - إحصائياتك وإنجازاتك\n"
        f"🏅 /achievements - جميع الإنجازات\n\n"
        f"⚙️ **إدارة الحساب:**\n"
        f"🔧 /settings - إعدادات الحساب\n"
        f"📤 /export - تصدير بياناتك\n"
        f"🗑️ /reset - إعادة تعيين الإحصائيات\n\n"
        f"❓ /help - للحصول على مساعدة مفصلة"
    )
    await update.message.reply_text(welcome_msg, parse_mode="Markdown")
    add_log(f"User {update.effective_user.id} ({user_name}) بدأ استخدام البوت", user_id=update.effective_user.id)

# ===== /help =====
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🆘 **دليل الاستخدام الكامل - BraveBot**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔍 **فحص المنتجات:**\n"
        "• /compliance - بدء فحص منتج جديد (اسم + سعر)\n"
        "• /cancel - إلغاء العملية الحالية في أي وقت\n\n"
        "📊 **الإحصائيات والإنجازات:**\n"
        "• /stats - إحصائياتك الشخصية مع التقدم والإنجازات\n"
        "• /achievements - عرض جميع الإنجازات (مكتملة وقادمة)\n\n"
        "⚙️ **إدارة الحساب:**\n"
        "• /settings - معلوماتك وإحصائيات سريعة\n"
        "• /export - تصدير بياناتك كملف CSV\n"
        "• /reset - إعادة تعيين جميع الإحصائيات والبدء من جديد\n\n"
        "🏆 **نظام الإنجازات:**\n"
        "🎯 البداية (1) → 🥉 مبتدئ (10) → 🥈 متقدم (50) → 🥇 خبير (100)\n"
        "💎 ماسي (250) → 🏆 أسطوري (500) → 👑 ملكي (1000) → 🌟 نجم (2000)\n\n"
        "💡 **نصائح:**\n"
        "• استخدم أسماء واضحة ومفصلة للمنتجات\n"
        "• النطاق السعري المقبول: $0.01 - $10,000\n"
        "• تابع تقدمك نحو الإنجاز التالي في /stats"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# ===== نظام الإنجازات الشخصي =====
def get_achievements(total_checks):
    """حساب الإنجازات بناءً على عدد الفحوصات"""
    achievements = []
    
    # الإنجازات المتاحة
    milestones = [
        (1, "🎯", "البداية", "أول فحص لك!"),
        (10, "🥉", "مبتدئ", "أول 10 فحوصات"),
        (50, "🥈", "متقدم", "50 فحص مكتمل"),
        (100, "🥇", "خبير", "100 فحص محترف"),
        (250, "💎", "ماسي", "250 فحص متقن"),
        (500, "🏆", "أسطوري", "500 فحص رائع"),
        (1000, "👑", "ملكي", "1000 فحص مذهل"),
        (2000, "🌟", "نجم", "2000 فحص استثنائي"),
    ]
    
    # الإنجازات المكتسبة
    earned = []
    next_milestone = None
    
    for count, icon, title, desc in milestones:
        if total_checks >= count:
            earned.append({"icon": icon, "title": title, "desc": desc, "count": count})
        else:
            next_milestone = {"icon": icon, "title": title, "desc": desc, "count": count}
            break
    
    return earned, next_milestone

def get_progress_bar(current, target, length=10):
    """إنشاء شريط تقدم بصري"""
    if target == 0:
        return "█" * length
    
    progress = min(current / target, 1.0)
    filled = int(progress * length)
    empty = length - filled
    
    bar = "█" * filled + "░" * empty
    percentage = int(progress * 100)
    
    return f"{bar} {percentage}%"

# ===== /stats =====
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        stats = get_user_stats(user_id)

        total = stats["total_checks"]
        passed = stats["passed_checks"]
        failed = stats["failed_checks"]

        success_rate = (passed / total * 100) if total > 0 else 0

        # حساب الإنجازات
        earned_achievements, next_milestone = get_achievements(total)
        
        # تحديد المستوى الحالي
        if earned_achievements:
            current_level = earned_achievements[-1]  # آخر إنجاز مكتسب
            level_display = f"{current_level['icon']} {current_level['title']}"
        else:
            level_display = "🆕 جديد"

        message = (
            f"📊 **إحصائيات {update.effective_user.first_name}**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🏆 **مستواك الحالي:** {level_display}\n\n"
            f"📈 **الأرقام:**\n"
            f"� إجمالي الفحوصات: **{total:,}**\n"
            f"✅ المقبولة: **{passed:,}** ({(passed/total*100) if total > 0 else 0:.1f}%)\n"
            f"❌ المرفوضة: **{failed:,}** ({(failed/total*100) if total > 0 else 0:.1f}%)\n"
            f"📊 معدل النجاح الإجمالي: **{success_rate:.1f}%**\n\n"
        )

        # عرض الإنجازات المكتسبة
        if earned_achievements:
            message += f"🏅 **إنجازاتك ({len(earned_achievements)}):**\n"
            for achievement in earned_achievements:  # عرض جميع الإنجازات
                message += f"{achievement['icon']} **{achievement['title']}** - {achievement['desc']}\n"
            message += "\n"
        else:
            message += f"🌟 **الإنجازات:**\n"
            message += f"🚀 ابدأ أول فحص لتحصل على إنجازات!\n\n"

        # عرض الهدف التالي
        if next_milestone:
            remaining = next_milestone['count'] - total
            progress_bar = get_progress_bar(total, next_milestone['count'])
            message += (
                f"🎯 **الهدف التالي:** {next_milestone['icon']} {next_milestone['title']}\n"
                f"📋 {next_milestone['desc']}\n"
                f"📊 {progress_bar}\n"
                f"🔄 باقي {remaining:,} فحص للوصول\n\n"
            )

        # إضافة معلومات التوقيت مع معالجة البيانات الفارغة
        last_check = stats.get('last_check', 'لم يتم بعد')
        joined_date = stats.get('joined_date', 'غير محدد')
        
        # تنسيق التاريخ إذا كان متاحاً
        if last_check and last_check != 'لم يتم بعد' and last_check != 'NULL':
            try:
                # محاولة تحويل التاريخ لتنسيق أجمل
                from datetime import datetime
                if len(last_check) > 10:  # يحتوي على وقت
                    dt = datetime.strptime(last_check, "%Y-%m-%d %H:%M:%S")
                    last_check = dt.strftime("%d/%m/%Y في %H:%M")
            except:
                pass  # استخدام النص الأصلي في حالة فشل التحويل
        
        message += (
            f"🕒 **معلومات التوقيت:**\n"
            f"📅 آخر فحص: **{last_check}**\n"
            f"📈 تاريخ الانضمام: **{joined_date}**\n"
        )

        await update.message.reply_text(message, parse_mode="Markdown")
        add_log(f"User {user_id} استعرض الإحصائيات - المستوى: {level_display}", user_id=user_id)

    except Exception as e:
        add_log(f"Database error in /stats: {str(e)}", level="ERROR", user_id=user_id)
        await update.message.reply_text("⚠️ حصل خطأ أثناء جلب الإحصائيات. حاول مرة أخرى.")

# ===== /achievements =====
async def achievements_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        stats = get_user_stats(user_id)
        total = stats["total_checks"]
        
        earned_achievements, next_milestone = get_achievements(total)

        message = (
            f"🏅 **جميع إنجازاتك**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        )

        if earned_achievements:
            message += f"✅ **الإنجازات المكتملة ({len(earned_achievements)}):**\n"
            for achievement in earned_achievements:
                message += f"{achievement['icon']} **{achievement['title']}** - {achievement['desc']}\n"
                message += f"   🎯 تم عند: **{achievement['count']:,} فحص**\n"
            message += "\n"
        else:
            message += f"🌟 **الإنجازات:**\n"
            message += f"🚀 **ابدأ أول فحص لتحصل على إنجازات!**\n\n"

        if next_milestone:
            remaining = next_milestone['count'] - total
            progress = get_progress_bar(total, next_milestone['count'])
            message += (
                f"🎯 **الهدف التالي:**\n"
                f"{next_milestone['icon']} **{next_milestone['title']}** - {next_milestone['desc']}\n"
                f"📊 التقدم: {progress}\n"
                f"🔄 باقي **{remaining:,} فحص** للوصول\n\n"
            )

        # عرض باقي الإنجازات المستقبلية
        all_milestones = [
            (1, "🎯", "البداية", "أول فحص لك!"),
            (10, "🥉", "مبتدئ", "أول 10 فحوصات"),
            (50, "🥈", "متقدم", "50 فحص مكتمل"),
            (100, "🥇", "خبير", "100 فحص محترف"),
            (250, "💎", "ماسي", "250 فحص متقن"),
            (500, "🏆", "أسطوري", "500 فحص رائع"),
            (1000, "👑", "ملكي", "1000 فحص مذهل"),
            (2000, "🌟", "نجم", "2000 فحص استثنائي"),
        ]
        
        future_achievements = [m for m in all_milestones if m[0] > total]
        if future_achievements:
            message += f"🔮 **قادمة ({len(future_achievements)}):**\n"
            for count, icon, title, desc in future_achievements[:3]:  # أول 3 قادمة
                message += f"{icon} **{title}** - {desc} ({count:,} فحص)\n"
            if len(future_achievements) > 3:
                message += f"... +{len(future_achievements) - 3} إنجازات أخرى\n"

        await update.message.reply_text(message, parse_mode="Markdown")
        add_log(f"User {user_id} استعرض جميع الإنجازات", user_id=user_id)

    except Exception as e:
        add_log(f"Database error in /achievements: {str(e)}", level="ERROR", user_id=user_id)
        await update.message.reply_text("⚠️ حصل خطأ أثناء جلب الإنجازات. حاول مرة أخرى.")

# ===== /settings =====
async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "مستخدم"
    stats = get_user_stats(user_id)
    
    # تنسيق تاريخ التسجيل
    try:
        join_date = stats.get('joined_date', 'غير محدد')
        if join_date != 'غير محدد':
            from datetime import datetime
            join_dt = datetime.fromisoformat(join_date.replace('Z', '+00:00'))
            join_date = join_dt.strftime("%Y/%m/%d")
    except:
        join_date = 'غير محدد'
    
    # حساب الإنجازات المحققة
    earned_count = 0
    for milestone in ACHIEVEMENTS:
        if stats['total_checks'] >= milestone['count']:
            earned_count += 1

    settings_msg = (
        f"⚙️ **إعدادات {user_name}**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 **الاسم:** {user_name}\n"
        f"🆔 **معرف المستخدم:** `{user_id}`\n"
        f"� **تاريخ التسجيل:** {join_date}\n"
        f"📊 **إجمالي الفحوص:** {stats['total_checks']:,}\n"
        f"✅ **المنتجات المتوافقة:** {stats['passed_checks']:,}\n"
        f"❌ **المنتجات غير المتوافقة:** {stats['failed_checks']:,}\n"
        f"🏅 **الإنجازات:** {earned_count}/8\n\n"
        f"🔧 **خيارات متقدمة:**\n"
        f"📤 `/export` - تصدير بياناتك\n"
        f"🗑️ `/reset` - إعادة تعيين الإحصائيات\n\n"
        f"💡 **نصيحة:** استخدم `/help` لمعرفة جميع الأوامر المتاحة"
    )

    await update.message.reply_text(settings_msg, parse_mode="Markdown")

# ===== /export =====
async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "مستخدم"
    
    try:
        # إرسال رسالة انتظار
        loading_msg = await update.message.reply_text(
            "📥 **جاري تصدير بياناتك...**\n"
            "⏳ يرجى الانتظار قليلاً"
        , parse_mode="Markdown")
        
        data = export_user_stats(user_id)

        if not data:
            await loading_msg.edit_text(
                "⚠️ **لا يوجد بيانات للتصدير**\n"
                "🔍 قم بفحص بعض المنتجات أولاً", 
                parse_mode="Markdown"
            )
            return

        # إنشاء ملف CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["User ID", "Total Checks", "Passed", "Failed", "Last Check", "Joined Date"])
        writer.writerow([
            data["user_id"], data["total_checks"], data["passed_checks"],
            data["failed_checks"], data["last_check"], data["joined_date"]
        ])

        csv_content = output.getvalue().encode('utf-8')
        filename = f"bravebot_data_{user_id}_{datetime.now().strftime('%Y%m%d')}.csv"

        # إرسال الملف
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=io.BytesIO(csv_content),
            filename=filename,
            caption=(
                f"📊 **بيانات {user_name}**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📁 **اسم الملف:** `{filename}`\n"
                f"📅 **تاريخ التصدير:** {datetime.now().strftime('%Y/%m/%d - %H:%M')}\n"
                f"📈 **إجمالي الفحوص:** {data['total_checks']:,}\n\n"
                f"💡 **ملاحظة:** يمكنك فتح هذا الملف بأي برنامج جداول بيانات"
            ),
            parse_mode="Markdown"
        )
        
        # حذف رسالة الانتظار
        await loading_msg.delete()
        add_log(f"User {user_id} exported data successfully", user_id=user_id)

    except Exception as e:
        add_log(f"Export error for user {user_id}: {str(e)}", level="ERROR", user_id=user_id)
        try:
            await loading_msg.edit_text(
                "❌ **فشل في التصدير**\n"
                "🔧 حدث خطأ تقني. حاول مرة أخرى لاحقاً", 
                parse_mode="Markdown"
            )
        except:
            await update.message.reply_text(
                "❌ **فشل في التصدير**\n"
                "🔧 حدث خطأ تقني. حاول مرة أخرى لاحقاً", 
                parse_mode="Markdown"
            )

# ===== /reset =====
async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "مستخدم"
    
    try:
        # الحصول على الإحصائيات قبل الحذف
        stats = get_user_stats(user_id)
        
        # إعادة تعيين البيانات
        reset_user_stats(user_id)
        
        reset_msg = (
            f"🗑️ **تم إعادة تعيين بيانات {user_name}**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 **البيانات المحذوفة:**\n"
            f"🔍 إجمالي الفحوص: {stats['total_checks']:,}\n"
            f"✅ المتوافقة: {stats['passed_checks']:,}\n"
            f"❌ غير المتوافقة: {stats['failed_checks']:,}\n\n"
            f"🎯 **البداية الجديدة:**\n"
            f"🌱 يمكنك الآن البدء من جديد\n"
            f"� استخدم `/compliance` لفحص منتجك الأول\n\n"
            f"💡 **نصيحة:** الإنجازات ستبدأ من الصفر أيضاً"
        )
        
        await update.message.reply_text(reset_msg, parse_mode="Markdown")
        add_log(f"User {user_id} reset all stats successfully", user_id=user_id)

    except Exception as e:
        add_log(f"Reset error for user {user_id}: {str(e)}", level="ERROR", user_id=user_id)
        await update.message.reply_text(
            "❌ **فشل في إعادة التعيين**\n"
            "🔧 حدث خطأ تقني. حاول مرة أخرى", 
            parse_mode="Markdown"
        )

# ===== /compliance =====
ASK_NAME, ASK_PRICE = range(2)

async def compliance_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name or "مستخدم"
    await update.message.reply_text(
        f"🛒 **مرحباً {user_name}! فحص منتج جديد**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📝 **الخطوة 1/2:** اكتب اسم المنتج\n\n"
        f"✨ **أمثلة جيدة:**\n"
        f"• هاتف آيفون 15 برو\n"
        f"• سماعات أبل إيربودز\n"
        f"• ساعة سامسونج جالاكسي\n\n"
        f"💡 **نصيحة:** كن دقيقاً في الوصف للحصول على أفضل نتيجة!\n\n"
        f"❌ **للإلغاء:** `/cancel`"
    , parse_mode="Markdown")
    return ASK_NAME

async def compliance_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_name = update.message.text.strip()

    # التحقق من الطول
    if len(product_name) < 3:
        await update.message.reply_text(
            "⚠️ **اسم المنتج قصير جداً**\n"
            "📝 يرجى كتابة اسم أكثر تفصيلاً (3 أحرف على الأقل)\n\n"
            "💡 **مثال:** بدلاً من 'iPhone' اكتب 'هاتف آيفون 15'"
        , parse_mode="Markdown")
        return ASK_NAME

    if len(product_name) > 100:
        await update.message.reply_text(
            "⚠️ **اسم المنتج طويل جداً**\n"
            "📝 يرجى كتابة اسم أقصر (100 حرف كحد أقصى)"
        , parse_mode="Markdown")
        return ASK_NAME

    context.user_data["product_name"] = product_name
    await update.message.reply_text(
        f"✅ **تم حفظ اسم المنتج**\n"
        f"📦 **المنتج:** `{product_name}`\n\n"
        f"💰 **الخطوة 2/2:** اكتب سعر المنتج بالدولار\n\n"
        f"� **النطاق المقبول:** `${config.get('min_price', 1)}` - `${config.get('max_price', 10000):,}`\n\n"
        f"✨ **أمثلة صحيحة:**\n"
        f"• `299` (للمنتجات بـ $299)\n"
        f"• `1499.99` (للمنتجات بـ $1,499.99)\n\n"
        f"❌ **للإلغاء:** `/cancel`"
    , parse_mode="Markdown")
    return ASK_PRICE

async def compliance_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "مستخدم"
    product_name = context.user_data.get("product_name")
    price_text = update.message.text.strip()

    try:
        # تنظيف النص من الرموز الإضافية
        price_clean = price_text.replace('$', '').replace(',', '').replace(' ', '')
        price = float(price_clean)
        
        min_price = config.get("min_price", 1)
        max_price = config.get("max_price", 10000)
        
        if price < min_price or price > max_price:
            await update.message.reply_text(
                f"⚠️ **سعر خارج النطاق المسموح!**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📊 **النطاق المقبول:** `${min_price}` - `${max_price:,}`\n"
                f"💰 **السعر المُدخل:** `${price:,.2f}`\n\n"
                f"🔄 **يرجى إدخال سعر ضمن النطاق المسموح**\n"
                f"💡 **مثال:** `{(min_price + max_price) // 2}`"
            , parse_mode="Markdown")
            return ASK_PRICE
            
        if price <= 0:
            await update.message.reply_text(
                f"⚠️ **سعر غير صحيح!**\n"
                f"💰 يجب أن يكون السعر أكبر من صفر\n\n"
                f"🔄 **أعد إدخال السعر:**"
            , parse_mode="Markdown")
            return ASK_PRICE
            
    except ValueError:
        await update.message.reply_text(
            f"⚠️ **خطأ في تنسيق السعر!**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"💡 **أمثلة صحيحة:**\n"
            f"• `29.99` (للسعر $29.99)\n"
            f"• `150` (للسعر $150)\n"
            f"• `1250.5` (للسعر $1,250.50)\n\n"
            f"❌ **أمثلة خاطئة:**\n"
            f"• `abc` أو `twenty`\n"
            f"• `$29.99` (لا تضع رمز $)\n\n"
            f"🔄 **يرجى إدخال رقم صحيح فقط:**"
        , parse_mode="Markdown")
        return ASK_PRICE

    # بدء معالجة الفحص
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    processing_msg = await update.message.reply_text(
        f"🔄 **جارٍ فحص المنتج...**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📦 **المنتج:** `{product_name}`\n"
        f"💰 **السعر:** `${price:,.2f}`\n\n"
        f"⏳ **يرجى الانتظار لحظات...**"
    , parse_mode="Markdown")

    await asyncio.sleep(2)

    compliance_result = check_product_compliance({
        "name": product_name,
        "price": price,
        "user_id": user_id
    })

    is_compliant = compliance_result.get("compliant", True)
    reason = compliance_result.get("reason", "")

    try:
        update_user_stats(user_id, is_compliant, timestamp)
        
        # فحص الإنجازات الجديدة
        updated_stats = get_user_stats(user_id)
        earned_achievements, _ = get_achievements(updated_stats["total_checks"])
        old_earned_achievements, _ = get_achievements(updated_stats["total_checks"] - 1)
        
        # إذا تم تحقيق إنجاز جديد
        if len(earned_achievements) > len(old_earned_achievements):
            new_achievement = earned_achievements[-1]  # الإنجاز الجديد
            achievement_msg = (
                f"🎉 **إنجاز جديد مُحقق!** 🎉\n\n"
                f"{new_achievement['icon']} **{new_achievement['title']}**\n"
                f"📋 {new_achievement['desc']}\n\n"
                f"🔥 مبروك! استمر في التقدم!"
            )
            await update.message.reply_text(achievement_msg, parse_mode="Markdown")
        
        add_log(f"User {user_id} فحص '{product_name}' (${price}) - النتيجة: {'مطابق' if is_compliant else 'غير مطابق'}", user_id=user_id)
    except Exception as e:
        add_log(f"Database error in compliance: {str(e)}", level="ERROR", user_id=user_id)

    # حذف رسالة المعالجة
    await processing_msg.delete()

    # تحديد أيقونات ونصوص النتيجة
    result_icon = "✅" if is_compliant else "❌"
    result_text = "مطابق للشروط" if is_compliant else "غير مطابق للشروط"
    result_color = "🟢" if is_compliant else "🔴"
    result_emoji = "🎉" if is_compliant else "⚠️"

    # بناء رسالة النتيجة
    message = (
        f"{result_emoji} **نتيجة فحص المنتج**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📦 **المنتج:** `{product_name}`\n"
        f"💰 **السعر:** `${price:,.2f}`\n"
        f"{result_color} **النتيجة:** {result_icon} **{result_text}**\n"
    )

    if reason:
        message += f"📝 **السبب:** {reason}\n"

    # إضافة معلومات إضافية
    current_stats = get_user_stats(user_id)
    success_rate = (current_stats['passed_checks'] / max(current_stats['total_checks'], 1)) * 100
    
    message += (
        f"\n📊 **إحصائياتك الحديثة:**\n"
        f"🔍 إجمالي الفحوص: **{current_stats['total_checks']:,}**\n"
        f"✅ نسبة النجاح: **{success_rate:.1f}%**\n\n"
        f"🕒 **وقت الفحص:** `{timestamp}`\n\n"
        f"� **التالي:**\n"
        f"📈 `/stats` - عرض الإحصائيات المفصلة\n"
        f"🏅 `/achievements` - عرض إنجازاتك\n"
        f"🛒 `/compliance` - فحص منتج آخر"
    )

    await update.message.reply_text(message, parse_mode="Markdown")

    return ConversationHandler.END

# ===== /cancel =====
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name or "مستخدم"
    await update.message.reply_text(
        f"❌ **تم إلغاء العملية، {user_name}**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔄 **يمكنك:**\n"
        f"🛒 `/compliance` - بدء فحص جديد\n"
        f"📊 `/stats` - عرض إحصائياتك\n"
        f"❓ `/help` - عرض جميع الأوامر\n\n"
        f"💡 **نصيحة:** لا تتردد في المحاولة مرة أخرى!"
    , parse_mode="Markdown")
    add_log(f"User {update.effective_user.id} cancelled compliance check", user_id=update.effective_user.id)
    return ConversationHandler.END

# ===== معالج الأخطاء =====
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأخطاء العام للبوت"""
    try:
        error_msg = str(context.error)
        user_id = update.effective_user.id if update and update.effective_user else None
        
        # معالجة خاصة لأخطاء التضارب
        if "Conflict" in error_msg or "ConflictError" in error_msg:
            print("⚠️ Bot conflict detected - another instance is running")
            add_log("Bot conflict detected - shutting down gracefully", level="WARNING")
            return
            
        # تسجيل الخطأ مع تفاصيل أكثر
        add_log(f"Unhandled bot error: {error_msg}", level="ERROR", user_id=user_id)
        
        # رسالة خطأ محسنة للمستخدم
        if update and update.effective_chat:
            error_text = (
                "⚠️ **حدث خطأ مؤقت**\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "🔄 **يرجى المحاولة مرة أخرى**\n"
                "❓ إذا استمر الخطأ، استخدم `/help` للمساعدة\n\n"
                "💡 **أو جرب:**\n"
                "📊 `/stats` - عرض إحصائياتك\n"
                "🛒 `/compliance` - فحص منتج جديد"
            )
            await update.effective_message.reply_text(error_text, parse_mode="Markdown")
            
    except Exception as e:
        critical_error = f"Critical error in error handler: {str(e)}"
        print(f"⚠️ {critical_error}")
        add_log(critical_error, level="CRITICAL")

# ===== إعداد الأوامر في القائمة =====
async def setup_bot_commands(app):
    try:
        commands = [
            BotCommand("start", "بدء استخدام البوت"),
            BotCommand("compliance", "فحص منتج جديد"),
            BotCommand("stats", "عرض الإحصائيات"),
            BotCommand("achievements", "جميع الإنجازات"),
            BotCommand("settings", "إعدادات الحساب"),
            BotCommand("help", "المساعدة"),
            BotCommand("export", "تصدير بياناتك"),
            BotCommand("reset", "إعادة تعيين الإحصائيات"),
            BotCommand("cancel", "إلغاء العملية الحالية"),
        ]
        await app.bot.set_my_commands(commands)
        add_log("✅ Bot commands menu setup successfully")
    except Exception as e:
        add_log(f"⚠️ Failed to setup bot commands: {str(e)}", level="ERROR")

# ===== إعداد قاعدة البيانات =====
def init_database():
    try:
        from core.database_manager import init_db
        init_db()
        add_log("✅ Database initialized successfully")
    except Exception as e:
        add_log(f"⚠️ Database initialization failed: {str(e)}", level="ERROR")

# ===== تشغيل البوت =====
if __name__ == "__main__":
    if not TOKEN:
        print("❌ Error: TELEGRAM_TOKEN not found in environment variables!")
        exit(1)

    print("🔍 Checking for existing bot instances...")
    
    # التأكد من عدم وجود instances أخرى
    print("✅ Bot instance check completed")
    print("⚠️  تأكد من إيقاف البوت على Railway قبل التشغيل المحلي")

    add_log("🚀 BraveBot v2.0 starting with enhanced features...")

    init_database()

    app = Application.builder().token(TOKEN).build()

    # أوامر منفصلة
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("achievements", achievements_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("settings", settings_command))
    app.add_handler(CommandHandler("export", export_command))
    app.add_handler(CommandHandler("reset", reset_command))

    # ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("compliance", compliance_start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, compliance_name)],
            ASK_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, compliance_price)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    app.add_handler(conv_handler)

    # إضافة معالج الأخطاء
    app.add_error_handler(error_handler)

    print("🚀 BraveBot v2.0 is running with SUPERCHARGED features!")

    async def post_init(app):
        await setup_bot_commands(app)

    app.post_init = post_init
    
    # تشغيل البوت مع حماية من التشغيل المتعدد
    try:
        print("🚀 Starting bot polling... Press Ctrl+C to stop")
        app.run_polling(
            drop_pending_updates=True, 
            close_loop=False,
            poll_interval=2.0,  # زيادة فترة الاستعلام
            timeout=30  # مهلة زمنية أطول
        )
    except Exception as e:
        if "Conflict" in str(e):
            print("❌ Bot startup conflict: Another instance is running!")
            print("💡 Solution: Stop the bot on Railway or wait 30 seconds")
        else:
            print(f"❌ Bot startup error: {e}")
        add_log(f"Bot startup failed: {str(e)}", level="ERROR")