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
        f"🎉 أهلاً وسهلاً {user_name}!\n\n"
        f"🤖 **BraveBot** - فاحص المنتجات الذكي\n\n"
        f"🔍 /compliance - فحص منتج جديد\n"
        f"📊 /stats - إحصائياتك الشخصية\n"
        f"🏅 /achievements - جميع إنجازاتك\n"
        f"ℹ️ /help - المساعدة الكاملة\n"
        f"⚙️ /settings - إعدادات الحساب\n"
        f"📤 /export - تصدير بياناتك\n"
        f"🗑️ /reset - إعادة تعيين الإحصائيات\n\n"
        f"✨ **مصمم خصيصاً لاستخدامك الشخصي!**"
    )
    await update.message.reply_text(welcome_msg, parse_mode="Markdown")
    add_log(f"User {update.effective_user.id} ({user_name}) بدأ استخدام البوت", user_id=update.effective_user.id)

# ===== /help =====
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🆘 **دليل الاستخدام الكامل:**\n\n"
        "🔍 **فحص المنتجات:**\n"
        "• /compliance - بدء فحص منتج جديد\n"
        "• /cancel - إلغاء العملية الحالية\n\n"
        "📊 **الإحصائيات:**\n"
        "• /stats - إحصائياتك الشخصية\n"
        "• /achievements - جميع إنجازاتك\n\n"
        "⚙️ **الإعدادات:**\n"
        "• /settings - إعدادات حسابك\n"
        "• /export - تصدير بياناتك\n"
        "• /reset - إعادة تعيين الإحصائيات\n\n"
        "📋 **ملاحظة:**\n"
        f"💡 **نصيحة:** استخدم أسماء واضحة للمنتجات!"
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
            f"━━━━━━━━━━━━━━━━━━━\n\n"
            f"🏆 **مستواك:** {level_display}\n\n"
            f"📈 **الأرقام:**\n"
            f"🔍 إجمالي الفحوصات: {total:,}\n"
            f"✅ المقبولة: {passed:,}\n"
            f"❌ المرفوضة: {failed:,}\n"
            f"📊 معدل النجاح: {success_rate:.1f}%\n\n"
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

        message += (
            f"🕒 **التوقيت:**\n"
            f"📅 آخر فحص: {stats['last_check']}\n"
            f"📈 انضممت: {stats.get('joined_date', 'غير محدد')}\n"
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
            f"━━━━━━━━━━━━━━━━━━━\n\n"
        )

        if earned_achievements:
            message += f"✅ **مكتملة ({len(earned_achievements)}):**\n"
            for achievement in earned_achievements:
                message += f"{achievement['icon']} **{achievement['title']}** - {achievement['desc']} ({achievement['count']} فحص)\n"
            message += "\n"

        if next_milestone:
            remaining = next_milestone['count'] - total
            progress = get_progress_bar(total, next_milestone['count'])
            message += (
                f"🎯 **التالي:**\n"
                f"{next_milestone['icon']} **{next_milestone['title']}** - {next_milestone['desc']}\n"
                f"📊 {progress}\n"
                f"🔄 باقي {remaining:,} فحص\n\n"
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
    stats = get_user_stats(user_id)

    settings_msg = (
        f"⚙️ **إعدادات حسابك:**\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 **معلومات الحساب:**\n"
        f"🆔 معرف المستخدم: {user_id}\n"
        f"👨‍💼 الاسم: {update.effective_user.first_name}\n\n"
        f"📊 **إحصائيات سريعة:**\n"
        f"🔍 إجمالي الفحوصات: {stats['total_checks']:,}\n"
        f"✅ المقبولة: {stats['passed_checks']:,}\n"
        f"❌ المرفوضة: {stats['failed_checks']:,}\n\n"
        f"🔧 **خيارات متقدمة:**\n"
        f"📤 /export - تصدير بياناتك\n"
        f"🗑️ /reset - إعادة تعيين الإحصائيات\n"
    )

    await update.message.reply_text(settings_msg, parse_mode="Markdown")

# ===== /export =====
async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = export_user_stats(user_id)

    if not data:
        await update.message.reply_text("⚠️ لا يوجد بيانات لتصديرها.")
        return

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["User ID", "Total Checks", "Passed", "Failed", "Last Check", "Joined Date"])
    writer.writerow([
        data["user_id"], data["total_checks"], data["passed_checks"],
        data["failed_checks"], data["last_check"], data["joined_date"]
    ])
    output.seek(0)

    await update.message.reply_document(
        document=io.BytesIO(output.getvalue().encode()),
        filename="user_stats.csv",
        caption="📊 تم تصدير بياناتك بنجاح"
    )
    add_log(f"User {user_id} صدّر بياناته", user_id=user_id)

# ===== /reset =====
async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    reset_user_stats(user_id)
    await update.message.reply_text(
        "🗑️ **تمت إعادة تعيين إحصائياتك بنجاح**\n\n"
        "يمكنك البدء من جديد الآن!"
    )
    add_log(f"User {user_id} أعاد تعيين إحصائياته", user_id=user_id)

# ===== /compliance =====
ASK_NAME, ASK_PRICE = range(2)

async def compliance_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛒 **بدء فحص منتج جديد**\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        "📝 **الخطوة 1/2:** اكتب اسم المنتج\n\n"
        "💡 **نصيحة:** كن دقيقاً في الوصف للحصول على أفضل نتيجة!"
    )
    return ASK_NAME

async def compliance_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_name = update.message.text.strip()

    if len(product_name) < 3:
        await update.message.reply_text("⚠️ اسم المنتج قصير جداً. اكتب اسماً أكثر تفصيلاً (3 أحرف على الأقل).")
        return ASK_NAME

    if len(product_name) > 100:
        await update.message.reply_text("⚠️ اسم المنتج طويل جداً. اكتب اسماً أقصر (100 حرف كحد أقصى).")
        return ASK_NAME

    context.user_data["product_name"] = product_name
    await update.message.reply_text(
        f"📦 **المنتج:** {product_name}\n\n"
        f"💰 **الخطوة 2/2:** اكتب سعر المنتج بالدولار\n\n"
        f"💡 **نطاق السعر المقبول:** ${config['min_price']} - ${config['max_price']:,}"
    )
    return ASK_PRICE

async def compliance_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    product_name = context.user_data.get("product_name")
    price_text = update.message.text.strip()

    try:
        price = float(price_text)
        if price < config["min_price"] or price > config["max_price"]:
            await update.message.reply_text(
                f"⚠️ **سعر خارج النطاق المسموح!**\n\n"
                f"📊 النطاق المقبول: ${config['min_price']} - ${config['max_price']:,}\n"
                f"💰 السعر المدخل: ${price:,}\n\n"
                f"🔄 أعد إدخال السعر:"
            )
            return ASK_PRICE
    except ValueError:
        await update.message.reply_text(
            "⚠️ **خطأ في تنسيق السعر!**\n\n"
            "💡 أمثلة صحيحة:\n"
            "• 29.99\n"
            "• 150\n"
            "• 1250.5\n\n"
            "🔄 أعد إدخال السعر:"
        )
        return ASK_PRICE

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    processing_msg = await update.message.reply_text(
        "🔄 **جارٍ فحص المنتج...**\n"
        "⏳ يرجى الانتظار..."
    )

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

    await processing_msg.delete()

    result_icon = "✅" if is_compliant else "❌"
    result_text = "مطابق للشروط" if is_compliant else "غير مطابق للشروط"
    result_color = "🟢" if is_compliant else "🔴"

    message = (
        f"🔍 **نتيجة فحص المنتج**\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"📦 **المنتج:** {product_name}\n"
        f"💰 **السعر:** ${price:,.2f}\n"
        f"{result_color} **النتيجة:** {result_icon} {result_text}\n"
    )

    if reason:
        message += f"📝 **السبب:** {reason}\n"

    message += (
        f"\n🕒 **وقت الفحص:** {timestamp}\n"
        f"📊 استخدم /stats لرؤية إحصائياتك"
    )

    await update.message.reply_text(message, parse_mode="Markdown")

    return ConversationHandler.END

# ===== /cancel =====
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ **تم إلغاء العملية بنجاح**\n\n"
        "🔄 يمكنك بدء فحص جديد باستخدام /compliance"
    )
    add_log(f"User {update.effective_user.id} ألغى عملية الفحص", user_id=update.effective_user.id)
    return ConversationHandler.END

# ===== معالج الأخطاء =====
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأخطاء العام للبوت"""
    try:
        error_msg = f"❌ خطأ غير متوقع: {str(context.error)}"
        
        # معالجة خاصة لأخطاء التضارب
        if "Conflict" in str(context.error):
            print("⚠️ Bot conflict detected - another instance is running")
            return
            
        add_log(f"Unhandled error: {str(context.error)}", level="ERROR", 
                user_id=update.effective_user.id if update and update.effective_user else None)
        
        if update and update.effective_chat:
            await update.effective_message.reply_text(
                "⚠️ حدث خطأ مؤقت. يرجى المحاولة مرة أخرى.\n\n"
                "إذا استمر الخطأ، استخدم /help للمساعدة."
            )
    except Exception as e:
        print(f"Error in error handler: {e}")

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