import os
import yaml
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from core.compliance_checker import check_product_compliance

# ================== Environment variables ==================
TOKEN = os.getenv("TELEGRAM_TOKEN")

# ================== Load config ==================
try:
    with open("config/config.yaml", encoding="utf-8") as file:
        config = yaml.safe_load(file)
except FileNotFoundError:
    config = {"max_price": 10000, "min_price": 0.01}

# ================== Conversation states ==================
ASK_NAME, ASK_CATEGORY, ASK_PRICE, CONFIRM_PRODUCT = range(4)

CATEGORIES = [
    "إلكترونيات", "ملابس", "منزل وحديقة", "رياضة",
    "كتب", "ألعاب", "تجميل", "سيارات", "أخرى"
]

# ================== Commands ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        "🎉 البوت شغال بنجاح!\n\n"
        "استخدم /help لعرض الأوامر المتاحة."
    )
    await update.message.reply_text(welcome_msg)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🌟 الأوامر المتاحة:\n\n"
        "/start - 🚀 تأكيد أن البوت شغال\n"
        "/compliance - 🛒 بدء فحص منتج جديد\n"
        "/help - ❓ عرض قائمة الأوامر المتاحة"
    )
    await update.message.reply_text(help_text)

# ================== Compliance conversation ==================
async def compliance_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["current_product"] = {}
    await update.message.reply_text(
        "🛒 بدء فحص منتج جديد\n\n"
        "✏️ الخطوة 1/3: اكتب اسم المنتج"
    )
    return ASK_NAME

async def compliance_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_name = update.message.text.strip()
    if len(product_name) < 3:
        await update.message.reply_text("⚠️ الاسم قصير جدًا، اكتب اسم أطول:")
        return ASK_NAME

    context.user_data["current_product"]["name"] = product_name

    # Inline keyboard categories
    keyboard = []
    for i in range(0, len(CATEGORIES), 2):
        row = [InlineKeyboardButton(CATEGORIES[i], callback_data=f"cat_{i}")]
        if i + 1 < len(CATEGORIES):
            row.append(InlineKeyboardButton(CATEGORIES[i + 1], callback_data=f"cat_{i+1}"))
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"✅ تم حفظ الاسم: {product_name}\n\n"
        "📂 الخطوة 2/3: اختر فئة المنتج:",
        reply_markup=reply_markup
    )
    return ASK_CATEGORY

async def category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category_index = int(query.data.split("_")[1])
    selected_category = CATEGORIES[category_index]
    context.user_data["current_product"]["category"] = selected_category

    await query.edit_message_text(
        f"✅ تم اختيار الفئة: {selected_category}\n\n"
        "💰 الخطوة 3/3: اكتب سعر المنتج (بالدولار)"
    )
    return ASK_PRICE

async def compliance_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price_text = update.message.text.strip()
    try:
        price = float(price_text)
        if price <= 0:
            raise ValueError
        if price > config.get("max_price", 10000):
            await update.message.reply_text(
                f"⚠️ السعر أعلى من الحد المسموح (${config['max_price']})، اكتب سعر أقل:"
            )
            return ASK_PRICE
    except ValueError:
        await update.message.reply_text("⚠️ اكتب رقم صحيح للسعر:")
        return ASK_PRICE

    context.user_data["current_product"]["price"] = price

    product = context.user_data["current_product"]
    result = check_product_compliance(product)

    if result:
        await update.message.reply_text("✅ الفحص: المنتج مطابق للشروط (محاكاة)")
    else:
        await update.message.reply_text("❌ الفحص: المنتج غير مطابق للشروط (محاكاة)")

    return ConversationHandler.END

async def compliance_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚫 تم إلغاء العملية.")
    return ConversationHandler.END

# ================== Main ==================
if __name__ == "__main__":
    if not TOKEN:
        print("❌ ERROR: TELEGRAM_TOKEN not set!")
        exit(1)

    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("compliance", compliance_start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, compliance_name)],
            ASK_CATEGORY: [CallbackQueryHandler(category_callback, pattern="^cat_")],
            ASK_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, compliance_price)],
        },
        fallbacks=[CommandHandler("cancel", compliance_cancel)],
    )
    app.add_handler(conv_handler)

    print("🚀 Bot is running with advanced compliance features...")
    app.run_polling()
