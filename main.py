import os
import yaml
import asyncio
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

# ===== استدعاءات من core =====
from core.database_manager import get_user_stats, update_user_stats, add_log, get_leaderboard
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

# ===== توكن البوت =====
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_IDS = config.get("admin_ids", [])

# ===== حالة المحادثة =====
ASK_NAME, ASK_PRICE = range(2)

# ===== نظام Rate Limiting =====
user_requests = {}


def check_rate_limit(user_id):
    """تحقق من حدود الاستخدام"""
    now = datetime.now()

    if user_id not in user_requests:
        user_requests[user_id] = {"hour": [], "day": []}

    # تنظيف الطلبات القديمة
    user_requests[user_id]["hour"] = [
        req for req in user_requests[user_id]["hour"] if now - req < timedelta(hours=1)
    ]
    user_requests[user_id]["day"] = [
        req for req in user_requests[user_id]["day"] if now - req < timedelta(days=1)
    ]

    # تحقق من الحدود
    hourly_limit = config["rate_limit"]["checks_per_hour"]
    daily_limit = config["rate_limit"]["checks_per_day"]

    if len(user_requests[user_id]["hour"]) >= hourly_limit:
        return False, "hour"
    if len(user_requests[user_id]["day"]) >= daily_limit:
        return False, "day"

    # إضافة الطلب الحالي
    user_requests[user_id]["hour"].append(now)
    user_requests[user_id]["day"].append(now)

    return True, None


# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name or "مستخدم"
    welcome_msg = (
        f"🎉 أهلاً وسهلاً {user_name}!\n\n"
        f"🤖 **BraveBot** - فاحص المنتجات الذكي\n\n"
        f"🔍 `/compliance` - فحص منتج جديد\n"
        f"📊 `/stats` - إحصائياتك الشخصية\n"
        f"🏆 `/leaderboard` - أفضل المستخدمين\n"
        f"ℹ️ `/help` - المساعدة الكاملة\n"
        f"⚙️ `/settings` - إعدادات الحساب\n\n"
        f"✨ **جديد:** نظام حماية من الإفراط في الاستخدام!"
    )
    await update.message.reply_text(welcome_msg, parse_mode="Markdown")
    add_log(f"User {update.effective_user.id} ({user_name}) بدأ استخدام البوت")


# ===== /help =====
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🆘 **دليل الاستخدام الكامل:**\n\n"
        "🔍 **فحص المنتجات:**\n"
        "• `/compliance` - بدء فحص منتج جديد\n"
        "• `/cancel` - إلغاء العملية الحالية\n\n"
        "📊 **الإحصائيات:**\n"
        "• `/stats` - إحصائياتك الشخصية\n"
        "• `/leaderboard` - أفضل المستخدمين\n\n"
        "⚙️ **الإعدادات:**\n"
        "• `/settings` - إعدادات حسابك\n"
        "• `/export` - تصدير بياناتك\n\n"
        "📋 **حدود الاستخدام:**\n"
        f"• {config['rate_limit']['checks_per_hour']} فحص/ساعة\n"
        f"• {config['rate_limit']['checks_per_day']} فحص/يوم\n\n"
        "💡 **نصيحة:** استخدم أسماء واضحة للمنتجات!"
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

        # تحديد المستوى
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
            f"🔍 إجمالي الفحوصات: `{total:,}`\n"
            f"✅ المقبولة: `{passed:,}`\n"
            f"❌ المرفوضة: `{failed:,}`\n"
            f"📊 معدل النجاح: `{success_rate:.1f}%`\n\n"
            f"🕒 آخر فحص: `{stats['last_check']}`"
        )

        await update.message.reply_text(message, parse_mode="Markdown")
        add_log(f"User {user_id} استعرض الإحصائيات - المستوى: {level}")

    except Exception as e:
        add_log(f"Database error in /stats: {str(e)}", level="ERROR")
        await update.message.reply_text("⚠️ حصل خطأ أثناء جلب الإحصائيات. حاول مرة أخرى.")


# ===== /leaderboard =====
async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        leaderboard = get_leaderboard()

        if not leaderboard:
            await update.message.reply_text("لا يوجد مستخدمين في القائمة حتى الآن.")
            return

        message = "🏆 **أفضل المستخدمين:**\n━━━━━━━━━━━━━━━━━━━\n\n"
        for rank, entry in enumerate(leaderboard, start=1):
            message += f"{rank}. **User {entry['user_id']}** - {entry['total_checks']} فحص\n"

        await update.message.reply_text(message, parse_mode="Markdown")

    except Exception as e:
        add_log(f"Error in /leaderboard: {str(e)}", level="ERROR")
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
        f"🆔 معرف المستخدم: `{user_id}`\n"
        f"⏰ فحوصات الساعة المتبقية: `{remaining_hour}`\n"
        f"📅 فحوصات اليوم المتبقية: `{remaining_day}`"
    )

    await update.message.reply_text(settings_msg, parse_mode="Markdown")


# ===== /compliance =====
async def compliance_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    allowed, limit_type = check_rate_limit(user_id)
    if not allowed:
        limit_msg = "ساعة" if limit_type == "hour" else "يوم"
        await update.message.reply_text(
            f"⏳ **وصلت للحد الأقصى!**\n"
            f"🚫 استنفدت عدد الفحوصات لهذه الـ{limit_msg}.\n"
            f"⏰ حاول مرة أخرى لاحقاً."
        )
        add_log(f"User {user_id} وصل للحد الأقصى - {limit_type}")
        return ConversationHandler.END

    await update.message.reply_text(
        "🛒 **بدء فحص منتج جديد**\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        "📝 اكتب اسم المنتج:"
    )
    return ASK_NAME


async def compliance_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_name = update.message.text.strip()

    if len(product_name) < 3:
        await update.message.reply_text("⚠️ اسم المنتج قصير جداً. أعد المحاولة.")
        return ASK_NAME

    context.user_data["product_name"] = product_name
    await update.message.reply_text(
        f"📦 المنتج: {product_name}\n\n💰 اكتب السعر بالدولار:"
    )
    return ASK_PRICE


async def compliance_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    product_name = context.user_data.get("product_name")
    price_text = update.message.text.strip()

    try:
        price = float(price_text)
    except ValueError:
        await update.message.reply_text("⚠️ السعر غير صحيح. أعد المحاولة.")
        return ASK_PRICE

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    compliance_result = check_product_compliance(
        {"name": product_name, "price": price, "user_id": user_id}
    )
    is_compliant = compliance_result.get("compliant", True)

    try:
        update_user_stats(user_id, is_compliant, timestamp)
        add_log(
            f"User {user_id} فحص '{product_name}' (${price}) - {'مطابق' if is_compliant else 'غير مطابق'}"
        )
    except Exception as e:
        add_log(f"Database error in compliance: {str(e)}", level="ERROR")

    result_icon = "✅" if is_compliant else "❌"
    result_text = "مطابق للشروط" if is_compliant else "غير مطابق للشروط"

    await update.message.reply_text(
        f"🔍 **نتيجة الفحص**\n━━━━━━━━━━━━━━━━━━━\n\n"
        f"📦 {product_name}\n"
        f"💰 ${price}\n"
        f"{result_icon} {result_text}\n"
        f"🕒 {timestamp}",
        parse_mode="Markdown",
    )

    return ConversationHandler.END


# ===== /cancel =====
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ تم إلغاء العملية.")
    add_log(f"User {update.effective_user.id} ألغى العملية")
    return ConversationHandler.END


# ===== إعداد قائمة الأوامر =====
async def setup_bot_commands(app):
    commands = [
        BotCommand("start", "بدء استخدام البوت"),
        BotCommand("compliance", "فحص منتج جديد"),
        BotCommand("stats", "عرض الإحصائيات"),
        BotCommand("leaderboard", "أفضل المستخدمين"),
        BotCommand("settings", "إعدادات الحساب"),
        BotCommand("help", "المساعدة"),
        BotCommand("cancel", "إلغاء العملية الحالية"),
    ]
    await app.bot.set_my_commands(commands)


# ===== تشغيل البوت =====
if __name__ == "__main__":
    if not TOKEN:
        print("❌ Error: TELEGRAM_TOKEN not found!")
        exit(1)

    add_log("🚀 BraveBot v2.0 starting with enhanced features...")

    from core.database_manager import init_db

    init_db()

    app = Application.builder().token(TOKEN).build()

    # أوامر منفصلة
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("leaderboard", leaderboard_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("settings", settings_command))

    # ConversationHandler لفحص المنتجات
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

    # إعداد قائمة الأوامر
    async def post_init(app):
        await setup_bot_commands(app)

    app.post_init = post_init
    print("🚀 BraveBot v2.0 is running...")
    app.run_polling(drop_pending_updates=True)
