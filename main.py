import os
import yaml
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# استيراد دوال قاعدة البيانات
from core.database_manager import get_user_stats, init_db

# ================== تحميل المتغيرات ==================
TOKEN = os.getenv("TELEGRAM_TOKEN")

with open("config/config.yaml", encoding="utf-8") as file:
    config = yaml.safe_load(file)

# ================== أوامر البوت ==================

# أمر start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        "🎉 البوت شغال بنجاح!\n\n"
        "استخدم /help لعرض الأوامر المتاحة."
    )
    await update.message.reply_text(welcome_msg)

# أمر help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🌟 الأوامر المتاحة:\n\n"
        "/start - تأكيد أن البوت شغال 🚀\n"
        "/compliance - بدء فحص منتج جديد 🛒\n"
        "/stats - عرض إحصائياتك الشخصية 🇮🇹\n"
        "/help - عرض هذه القائمة ❓"
    )
    await update.message.reply_text(help_text)

# أمر stats
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    stats = get_user_stats(user_id)

    stats_text = (
        f"📊 **إحصائياتك الشخصية:**\n\n"
        f"🔍 إجمالي الفحوصات: `{stats['total_checks']}`\n"
        f"✅ المنتجات المقبولة: `{stats['passed_checks']}`\n"
        f"❌ المنتجات المرفوضة: `{stats['failed_checks']}`\n"
        f"🕒 آخر فحص: {stats['last_check']}"
    )
    await update.message.reply_text(stats_text, parse_mode="Markdown")

# ================== تشغيل البوت ==================
if __name__ == "__main__":
    # نهيئ قاعدة البيانات هنا
    init_db()

    if not TOKEN:
        print("❌ ERROR - TELEGRAM_TOKEN environment variable is not set!")
        exit(1)

    app = Application.builder().token(TOKEN).build()

    # ربط الأوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))

    print("🚀 Bot is running with advanced compliance features...")
    app.run_polling()
