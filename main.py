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
    get_user_stats, update_user_stats, add_log, get_leaderboard,
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
user_requests = {}

# ===== Rate Limit =====
def check_rate_limit(user_id):
    now = datetime.now()

    if user_id not in user_requests:
        user_requests[user_id] = {"hour": [], "day": []}

    user_requests[user_id]["hour"] = [
        req for req in user_requests[user_id]["hour"] if now - req < timedelta(hours=1)
    ]
    user_requests[user_id]["day"] = [
        req for req in user_requests[user_id]["day"] if now - req < timedelta(days=1)
    ]

    hourly_limit = config["rate_limit"]["checks_per_hour"]
    daily_limit = config["rate_limit"]["checks_per_day"]

    if len(user_requests[user_id]["hour"]) >= hourly_limit:
        return False, "hour"
    if len(user_requests[user_id]["day"]) >= daily_limit:
        return False, "day"

    user_requests[user_id]["hour"].append(now)
    user_requests[user_id]["day"].append(now)

    return True, None

# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name or "مستخدم"
    welcome_msg = (
        f"🎉 أهلاً وسهلاً {user_name}!\n\n"
        f"🤖 **BraveBot** - فاحص المنتجات الذكي\n\n"
        f"🔍 /compliance - فحص منتج جديد\n"
        f"📊 /stats - إحصائياتك الشخصية\n"
        f"🏆 /leaderboard - أفضل المستخدمين\n"
        f"ℹ️ /help - المساعدة الكاملة\n"
        f"⚙️ /settings - إعدادات الحساب\n"
        f"📤 /export - تصدير بياناتك\n"
        f"🗑️ /reset - إعادة تعيين الإحصائيات\n\n"
        f"✨ **جديد:** نظام حماية من الإفراط في الاستخدام!"
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
        "• /leaderboard - أفضل المستخدمين\n\n"
        "⚙️ **الإعدادات:**\n"
        "• /settings - إعدادات حسابك\n"
        "• /export - تصدير بياناتك\n"
        "• /reset - إعادة تعيين الإحصائيات\n\n"
        "📋 **حدود الاستخدام:**\n"
        f"• {config['rate_limit']['checks_per_hour']} فحص/ساعة\n"
        f"• {config['rate_limit']['checks_per_day']} فحص/يوم\n\n"
        f"💡 **نصيحة:** استخدم أسماء واضحة للمنتجات!"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# ===== /stats =====
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        stats = get_user_stats(user_id)

        total = stats["total_checks"]
        passed = stats["passed_checks"]
        failed = stats["failed_checks"]

        success_rate = (passed / total * 100) if total > 0 else 0

        if total < 10:
            level = "🥉 مبتدئ"
        elif total < 50:
            level = "🥈 متوسط"
        elif total < 100:
            level = "🥇 خبير"
        else:
            level = "💎 أسطورة"

        message = (
            f"📊 **إحصائيات {update.effective_user.first_name}**\n"
            f"━━━━━━━━━━━━━━━━━━━\n\n"
            f"🏆 **مستواك:** {level}\n\n"
            f"📈 **الأرقام:**\n"
            f"🔍 إجمالي الفحوصات: {total:,}\n"
            f"✅ المقبولة: {passed:,}\n"
            f"❌ المرفوضة: {failed:,}\n"
            f"📊 معدل النجاح: {success_rate:.1f}%\n\n"
            f"🕒 **التوقيت:**\n"
            f"📅 آخر فحص: {stats['last_check']}\n"
            f"📈 انضممت: {stats.get('joined_date', 'غير محدد')}\n"
        )

        await update.message.reply_text(message, parse_mode="Markdown")
        add_log(f"User {user_id} استعرض الإحصائيات - المستوى: {level}", user_id=user_id)

    except Exception as e:
        add_log(f"Database error in /stats: {str(e)}", level="ERROR", user_id=user_id)
        await update.message.reply_text("⚠️ حصل خطأ أثناء جلب الإحصائيات. حاول مرة أخرى.")

# ===== /leaderboard =====
async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        top_users = get_leaderboard(limit=5)

        if not top_users:
            await update.message.reply_text("⚠️ لا يوجد بيانات للعرض حالياً.")
            return

        message = "🏆 **أفضل المستخدمين:**\n━━━━━━━━━━━━━━━\n"
        for i, user in enumerate(top_users, start=1):
            message += f"{i}. {user['name']} - {user['total_checks']} فحص\n"

        await update.message.reply_text(message, parse_mode="Markdown")
    except Exception as e:
        add_log(f"Database error in /leaderboard: {str(e)}", level="ERROR")
        await update.message.reply_text("⚠️ حصل خطأ أثناء جلب لوحة الصدارة.")

# ===== /settings =====
async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    remaining_hour = config["rate_limit"]["checks_per_hour"] - len(
        user_requests.get(user_id, {}).get("hour", [])
    )
    remaining_day = config["rate_limit"]["checks_per_day"] - len(
        user_requests.get(user_id, {}).get("day", [])
    )

    settings_msg = (
        f"⚙️ **إعدادات حسابك:**\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 **معلومات الحساب:**\n"
        f"🆔 معرف المستخدم: {user_id}\n"
        f"👨‍💼 الاسم: {update.effective_user.first_name}\n\n"
        f"📊 **حدود الاستخدام المتبقية:**\n"
        f"⏰ هذه الساعة: {remaining_hour} فحص\n"
        f"📅 اليوم: {remaining_day} فحص\n\n"
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
    user_id = update.effective_user.id

    allowed, limit_type = check_rate_limit(user_id)
    if not allowed:
        limit_msg = "ساعة" if limit_type == "hour" else "يوم"
        await update.message.reply_text(
            f"⏳ **وصلت للحد الأقصى!**\n\n"
            f"🚫 استنفدت عدد الفحوصات المسموحة لهذه ال{limit_msg}.\n"
            f"⏰ حاول مرة أخرى لاحقاً.\n\n"
            f"💡 استخدم /settings لمعرفة الحدود المتبقية."
        )
        add_log(f"User {user_id} وصل للحد الأقصى - {limit_type}")
        return ConversationHandler.END

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
            BotCommand("leaderboard", "أفضل المستخدمين"),
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

    add_log("🚀 BraveBot v2.0 starting with enhanced features...")

    init_database()

    app = Application.builder().token(TOKEN).build()

    # أوامر منفصلة
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("leaderboard", leaderboard_command))
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
        app.run_polling(drop_pending_updates=True, close_loop=False)
    except Exception as e:
        print(f"❌ Bot startup error: {e}")
        add_log(f"Bot startup failed: {str(e)}", level="ERROR")