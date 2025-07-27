import os
import yaml
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

# ================== Logging ==================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================== Environment variables ==================
TOKEN = os.getenv("TELEGRAM_TOKEN")

# ================== تحميل إعدادات إضافية ==================
try:
    with open("config/config.yaml", encoding="utf-8") as file:
        config = yaml.safe_load(file)
except FileNotFoundError:
    logger.warning("Config file not found, using defaults")
    config = {"max_price": 10000, "min_price": 0.01}

# ================== Conversation States ==================
ASK_NAME, ASK_PRICE, ASK_CATEGORY, CONFIRM_PRODUCT = range(4)

# ================== قائمة الفئات ==================
CATEGORIES = [
    "إلكترونيات", "ملابس", "منزل وحديقة", "رياضة",
    "كتب", "ألعاب", "تجميل", "سيارات", "أخرى"
]

# ================== أوامر أساسية ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("البوت شغال بنجاح مع الإصدار الجديد 🚀")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🌟 **الأوامر المتاحة:**\n\n"
        "🚀 `/start` - تأكيد إن البوت شغال\n"
        "🛒 `/compliance` - بدء فحص منتج جديد\n"
        "❓ `/help` - عرض قائمة الأوامر المتاحة\n"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

# ================== بدء محادثة فحص المنتج ==================
async def compliance_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # إعادة تعيين بيانات المنتج
    context.user_data['current_product'] = {}

    await update.message.reply_text(
        "🛒 **بدء فحص منتج جديد**\n\n"
        "📝 الخطوة 1/3: أدخل اسم المنتج\n"
        "💡 مثال: iPhone 15 Pro Max",
        parse_mode='Markdown'
    )
    return ASK_NAME

# ================== تشغيل البوت ==================
if __name__ == "__main__":
    if not TOKEN:
        logger.error("TELEGRAM_TOKEN environment variable is not set!")
        exit(1)

    app = Application.builder().token(TOKEN).build()

    # أوامر أساسية
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # Conversation Handler الجديد
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("compliance", compliance_start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: None)],  # Placeholder
        },
        fallbacks=[],
        per_message=False,
    )
    app.add_handler(conv_handler)

    print("🚀 Bot is running with python-telegram-bot v20+ ...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
