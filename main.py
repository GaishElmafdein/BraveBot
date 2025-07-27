import os
import yaml
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# استدعاء دوال قاعدة البيانات
from core.database_manager import init_db, get_user_stats, update_user_stats, add_log

# ================ تحميل التوكن من Environment ==================
TOKEN = os.getenv("TELEGRAM_TOKEN")

# ================ تحميل إعدادات إضافية من config.yaml ==================
try:
    with open("config/config.yaml", encoding="utf-8") as file:
        config = yaml.safe_load(file)
except FileNotFoundError:
    config = {"max_price": 10000}

# ================ تهيئة قاعدة البيانات ==================
init_db()

# ================ أوامر البوت ==================

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        "🎉 أهلاً بيك في بوت BraveBot!\n\n"
        "استخدم /help لعرض الأوامر المتاحة."
    )
    await update.message.reply_text(welcome_msg)
    add_log(f"User {update.effective_user.id} used /start")  # تسجيل الاستخدام

# أمر /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🌟 الأوامر المتاحة:\n\n"
        "🚀 /start - تأكيد أن البوت شغال\n"
        "🛒 /compliance - بدء فحص منتج جديد\n"
        "📊 /stats - عرض إحصائياتك الشخصية\n"
        "❓ /help - عرض هذه القائمة"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")
    add_log(f"User {update.effective_user.id} used /help")

# أمر /stats
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    stats = get_user_stats(user_id)

    stats_text = (
        "📊 إحصائياتك الشخصية:\n\n"
        f"🔍 إجمالي الفحوصات: {stats['total_checks']}\n"
        f"✅ المنتجات المقبولة: {stats['passed_checks']}\n"
        f"❌ المنتجات المرفوضة: {stats['failed_checks']}\n"
        f"🕒 آخر فحص: {stats['last_check']}"
    )

    await update.message.reply_text(stats_text, parse_mode="Markdown")
    add_log(f"User {user_id} requested stats: {stats}")

# أمر /compliance (placeholder مبدئي)
async def compliance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛒 بدء فحص منتج جديد...")
    add_log(f"User {update.effective_user.id} started compliance check")

# ================ تشغيل البوت ==================
if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("ERROR: TELEGRAM_TOKEN environment variable is not set!")

    app = Application.builder().token(TOKEN).build()

    # إضافة Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("compliance", compliance_command))

    add_log("Bot is running with advanced compliance features...")  # تسجيل بدء التشغيل
    print("🚀 Bot is running with advanced compliance features...")

    app.run_polling()
