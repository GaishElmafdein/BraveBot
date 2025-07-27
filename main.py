import os
import yaml
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ================== إعداد اللوجينج ==================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================== تحميل التوكن من Environment ==================
TOKEN = os.getenv("TELEGRAM_TOKEN")

# ================== تحميل إعدادات من config ==================
try:
    with open("config/config.yaml", encoding="utf-8") as file:
        config = yaml.safe_load(file)
except FileNotFoundError:
    logger.warning("Config file not found, using defaults")
    config = {"max_price": 10000}

# ================== Conversation States ==================
ASK_NAME, ASK_PRICE, ASK_CATEGORY, CONFIRM_PRODUCT = range(4)

# ================== قائمة الفئات ==================
CATEGORIES = [
    "إلكترونيات", "ملابس", "منزل وحديقة", "رياضة",
    "كتب", "ألعاب", "تجميل", "سيارات", "أخرى"
]

# ================== أوامر أساسية ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 تأكيد إن البوت شغال!\nاستخدم /help لعرض الأوامر المتاحة."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🌟 **الأوامر المتاحة:**\n\n"
        "🚀 `/start` - تأكيد أن البوت شغال\n"
        "🛒 `/compliance` - بدء فحص منتج جديد (تفاعلي)\n"
        "❓ `/help` - عرض قائمة الأوامر المتاحة\n"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

# ================== دوال المحادثة (compliance) ==================

async def compliance_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_product'] = {}
    await update.message.reply_text(
        "🛒 **بدء فحص منتج جديد**\n\n"
        "📝 الخطوة 1/3: اكتب اسم المنتج",
        parse_mode='Markdown'
    )
    return ASK_NAME

async def compliance_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_name = update.message.text.strip()

    if len(product_name) < 3:
        await update.message.reply_text("⚠️ الاسم قصير جداً، أدخل اسم أطول شوية.")
        return ASK_NAME

    context.user_data['current_product']['name'] = product_name

    # أزرار الفئات
    keyboard = []
    for i in range(0, len(CATEGORIES), 2):
        row = [InlineKeyboardButton(CATEGORIES[i], callback_data=f"cat_{i}")]
        if i + 1 < len(CATEGORIES):
            row.append(InlineKeyboardButton(CATEGORIES[i + 1], callback_data=f"cat_{i + 1}"))
        keyboard.append(row)

    await update.message.reply_text(
        f"✅ تم حفظ الاسم: **{product_name}**\n\nاختر الفئة:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return ASK_CATEGORY

async def category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category_index = int(query.data.split('_')[1])
    selected_category = CATEGORIES[category_index]

    context.user_data['current_product']['category'] = selected_category

    await query.edit_message_text(
        f"✅ تم اختيار الفئة: **{selected_category}**\n\n"
        f"💰 الخطوة 3/3: اكتب سعر المنتج (بالدولار)",
        parse_mode='Markdown'
    )
    return ASK_PRICE

async def compliance_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price_text = update.message.text.strip()

    try:
        price = float(price_text)
        if price <= 0:
            await update.message.reply_text("⚠️ السعر لازم يكون أكبر من صفر.")
            return ASK_PRICE
    except ValueError:
        await update.message.reply_text("⚠️ السعر غير صحيح! أدخل رقم فقط.")
        return ASK_PRICE

    context.user_data['current_product']['price'] = price
    product = context.user_data['current_product']

    keyboard = [
        [
            InlineKeyboardButton("✅ تأكيد", callback_data="confirm_yes"),
            InlineKeyboardButton("❌ إلغاء", callback_data="confirm_no")
        ]
    ]

    summary = (
        f"📋 **ملخص المنتج:**\n\n"
        f"🏷️ الاسم: {product['name']}\n"
        f"📂 الفئة: {product['category']}\n"
        f"💰 السعر: ${price}\n\n"
        "هل تريد المتابعة للفحص؟"
    )

    await update.message.reply_text(summary, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    return CONFIRM_PRODUCT

async def confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "confirm_yes":
        await query.edit_message_text("✅ تم الفحص: المنتج مطابق (محاكاة).")
    else:
        await query.edit_message_text("🚫 تم إلغاء العملية.")

    return ConversationHandler.END

# ================== Conversation Handler ==================
def main():
    if not TOKEN:
        logger.error("TELEGRAM_TOKEN environment variable is not set!")
        exit(1)

    app = Application.builder().token(TOKEN).build()

    # أوامر أساسية
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # Conversation Handler الخاص بـ /compliance
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("compliance", compliance_start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, compliance_name)],
            ASK_CATEGORY: [CallbackQueryHandler(category_callback, pattern="^cat_")],
            ASK_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, compliance_price)],
            CONFIRM_PRODUCT: [CallbackQueryHandler(confirm_callback, pattern="^confirm_")],
        },
        fallbacks=[],
        per_message=False
    )

    app.add_handler(conv_handler)

    print("🚀 Bot is running with compliance feature...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

# ================== تشغيل ==================
if __name__ == "__main__":
    main()