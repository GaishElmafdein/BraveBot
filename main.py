import os
import yaml
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ========== تحميل المتغيرات البيئية ==========
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# ========== إعداد اللوجينج ==========
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== تحميل إعدادات config.yaml ==========
try:
    with open("config/config.yaml", encoding="utf-8") as file:
        config = yaml.safe_load(file)
except FileNotFoundError:
    logger.warning("⚠️ ملف config.yaml غير موجود. سيتم استخدام القيم الافتراضية.")
    config = {"max_price": 10000, "min_price": 0.01}

# ========== أوامر البوت ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة ترحيب عند بدء التشغيل"""
    welcome_msg = (
        "🚀 البوت شغال بنجاح مع الإصدار الجديد!\n\n"
        "استخدم /help لعرض جميع الأوامر المتاحة."
    )
    await update.message.reply_text(welcome_msg)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """قائمة المساعدة"""
    help_text = (
        "🌟 **الأوامر المتاحة:**\n\n"
        "🚀 `/start` - تأكيد أن البوت شغال\n"
        "🛒 `/compliance` - بدء فحص منتج جديد\n"
        "❓ `/help` - عرض قائمة الأوامر المتاحة"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# ========== نقطة البداية ==========
if __name__ == "__main__":
    if not TOKEN:
        logger.error("❌ TELEGRAM_TOKEN غير متوفر في المتغيرات البيئية!")
        exit(1)

    app = Application.builder().token(TOKEN).build()

    # تسجيل الأوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    print("🚀 Bot is running with advanced compliance features...")
    app.run_polling()
