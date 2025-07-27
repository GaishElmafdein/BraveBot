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
from core.manager import get_user_stats, update_user_stats, add_log
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

# ===== Rate Limiting =====
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
        f"ℹ️ `/help` - المساعدة الكاملة\n\n"
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
        "• `/settings` - إعدادات حسابك\n\n"
        f"📋 **حدود الاستخدام:**\n"
        f"• {config['rate_limit']['checks_per_hour']} فحص/ساعة\n"
        f"• {config['rate_limit']['checks_per_day']} فحص/يوم\n"
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

        # مستوى المستخدم
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
            f"🔍 إجمالي الفحوصات: `{total}`\n"
            f"✅ المقبولة: `{passed}`\n"
            f"❌ المرفوضة: `{failed}`\n"
            f"📈 معدل النجاح: `{success_rate:.1f}%`\n"
            f"🕒 آخر فحص: `{stats['last_check']}`"
        )

        await update.message.reply_text(message, parse_mode="Markdown")
        add_log(f"User {user_id} استعرض الإحصائيات")

    except Exception as e:
        add_log(f"Database error in /stats: {str(e)}", level="ERROR")
        await update.message.reply_text("⚠️ حصل خطأ أثناء جلب الإحصائيات.")

# ===== /leaderboard =====
async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        import sqlite3
        conn = sqlite3.connect("bravebot.db")
        cur = conn.cursor()
        cur.execute("""
            SELECT user_id, total_checks, passed_checks
            FROM user_stats
            ORDER BY total_checks DESC
            LIMIT 5
        """)
        rows = cur.fetchall()
        conn.close()

        if not rows:
            await update.message.reply_text("🏆 لا يوجد مستخدمون في القائمة بعد!")
            return

        message = "🏆 **أفضل 5 مستخدمين**\n━━━━━━━━━━━━━━━\n\n"
        rank = 1
        for user_id, total, passed in rows:
            success_rate = (passed / total * 100) if total > 0 else 0
            message += (
                f"#{rank} - `{user_id}`\n"
                f"🔍 فحوصات: {total} | معدل نجاح: {success_rate:.1f}%\n\n"
            )
            rank += 1

        await update.message.reply_text(message, parse_mode="Markdown")
        add_log("Leaderboard viewed")

    except Exception as e:
        add_log(f"Error in /leaderboard: {str(e)}", level="ERROR")
        await update.message.reply_text("⚠️ خطأ أثناء جلب قائمة المتصدرين.")

# ===== باقي الأوامر (/compliance و /settings و /cancel) =====
# (هنا نتركها زي ما كانت في الكود السابق لأننا بنضيف بس /leaderboard حالياً)

# ===== إعداد الأوامر =====
async def setup_bot_commands(app):
    commands = [
        BotCommand("start", "بدء استخدام البوت"),
        BotCommand("compliance", "فحص منتج جديد"),
        BotCommand("stats", "عرض الإحصائيات"),
        BotCommand("leaderboard", "أفضل المستخدمين"),
        BotCommand("settings", "إعدادات الحساب"),
        BotCommand("help", "المساعدة"),
        BotCommand("cancel", "إلغاء العملية"),
    ]
    await app.bot.set_my_commands(commands)

# ===== تشغيل البوت =====
if __name__ == "__main__":
    if not TOKEN:
        print("❌ Error: TELEGRAM_TOKEN not found in environment variables!")
        exit(1)

    add_log("🚀 BraveBot v2.0 starting with leaderboard feature...")

    app = Application.builder().token(TOKEN).build()

    # إعداد الأوامر
    app.job_queue.run_once(lambda context: setup_bot_commands(app), when=1)

    # إضافة الأوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("leaderboard", leaderboard_command))

    # باقي الهاندلرز موجودة في الكود القديم (compliance, settings, cancel...)

    print("🚀 BraveBot v2.0 is running with leaderboard!")
    app.run_polling(drop_pending_updates=True)
