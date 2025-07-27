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

# استيراد دوال الفحص
from core.compliance_checker import check_product_compliance
from core.database_manager import init_db, update_user_stats, get_user_stats

# ================== إعداد اللوجينج ==================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================== تحميل التوكن من Environment ==================
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

# ================== أوامر البوت ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        "🎉 مرحباً بك في بوت فحص المنتجات!\n\n"
        "✨ **الميزات المتاحة:**\n"
        "🔍 فحص compliance للمنتجات\n"
        "💬 محادثة تفاعلية ذكية\n"
        "📊 تتبع تاريخ الفحوصات\n"
        "⚡ سرعة ودقة في النتائج\n\n"
        "استخدم /help لعرض جميع الأوامر."
    )
    await update.message.reply_text(welcome_msg, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🌟 **الأوامر المتاحة:**\n\n"
        "🚀 `/start` - بدء البوت والترحيب\n"
        "🛒 `/compliance` - فحص منتج جديد (تفاعلي)\n"
        "📊 `/stats` - إحصائيات الفحوصات\n"
        "🚫 `/cancel` - إلغاء العملية الحالية\n"
        "❓ `/help` - عرض هذه القائمة\n\n"
        "💡 **نصائح:**\n"
        "• استخدم أسماء منتجات واضحة\n"
        "• تأكد من إدخال السعر بشكل صحيح\n"
        "• يمكنك إلغاء أي عملية في أي وقت"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    stats = get_user_stats(user_id)

    success_rate = (stats['passed_checks'] / stats['total_checks'] * 100) if stats['total_checks'] > 0 else 0

    stats_text = (
        f"📊 **إحصائياتك الشخصية:**\n\n"
        f"🔍 إجمالي الفحوصات: `{stats['total_checks']}`\n"
        f"✅ المنتجات المقبولة: `{stats['passed_checks']}`\n"
        f"❌ المنتجات المرفوضة: `{stats['failed_checks']}`\n"
        f"📈 معدل النجاح: `{success_rate:.1f}%`\n\n"
        f"🕒 آخر فحص: {stats['last_check']}"
    )
    await update.message.reply_text(stats_text, parse_mode='Markdown')

# ================== Compliance Conversation ==================

async def compliance_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_product'] = {}
    await update.message.reply_text(
        "🛒 **بدء فحص منتج جديد**\n\n"
        "📝 الخطوة 1/3: أدخل اسم المنتج\n"
        "💡 مثال: iPhone 15 Pro Max"
    )
    return ASK_NAME

async def compliance_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_name = update.message.text.strip()

    if len(product_name) < 3:
        await update.message.reply_text("⚠️ اسم المنتج قصير جداً! أعد إدخال اسم أطول.")
        return ASK_NAME

    context.user_data['current_product']['name'] = product_name

    keyboard = []
    for i in range(0, len(CATEGORIES), 2):
        row = [InlineKeyboardButton(CATEGORIES[i], callback_data=f"cat_{i}")]
        if i + 1 < len(CATEGORIES):
            row.append(InlineKeyboardButton(CATEGORIES[i + 1], callback_data=f"cat_{i + 1}"))
        keyboard.append(row)

    await update.message.reply_text(
        f"✅ تم حفظ الاسم: **{product_name}**\n\n📂 اختر فئة المنتج:",
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
        f"✅ تم حفظ الفئة: **{selected_category}**\n\n💰 أدخل سعر المنتج بالدولار:",
        parse_mode='Markdown'
    )
    return ASK_PRICE

async def compliance_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price_text = update.message.text.strip()

    try:
        price = float(price_text.replace(',', ''))
        if price <= 0:
            await update.message.reply_text("⚠️ السعر يجب أن يكون أكبر من صفر!")
            return ASK_PRICE
        if price > config.get('max_price', 10000):
            await update.message.reply_text(f"⚠️ الحد الأقصى للسعر هو ${config.get('max_price', 10000)}")
            return ASK_PRICE
    except ValueError:
        await update.message.reply_text("⚠️ أدخل رقم صحيح (مثال: 299.99)")
        return ASK_PRICE

    product = context.user_data['current_product']
    product['price'] = price
    product['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    is_compliant = check_product_compliance(product)

    # تحديث الإحصائيات في قاعدة البيانات
    user_id = update.effective_user.id
    update_user_stats(user_id, passed=is_compliant, timestamp=product['timestamp'])

    result_text = (
        f"🎯 **نتيجة الفحص:**\n\n"
        f"{'✅ مقبول' if is_compliant else '❌ مرفوض'}\n"
        f"🏷️ الاسم: {product['name']}\n"
        f"📂 الفئة: {product['category']}\n"
        f"💰 السعر: ${price:,.2f}\n"
        f"🕒 الوقت: {product['timestamp']}"
    )

    await update.message.reply_text(result_text, parse_mode='Markdown')
    return ConversationHandler.END

async def compliance_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop('current_product', None)
    await update.message.reply_text("🚫 تم إلغاء عملية الفحص.")
    return ConversationHandler.END

# ================== تشغيل البوت ==================

if __name__ == "__main__":
    if not TOKEN:
        logger.error("TELEGRAM_TOKEN environment variable is not set!")
        exit(1)

    init_db()  # إنشاء قاعدة البيانات

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))

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

    logger.info("Bot is running with advanced features...")
    print("🚀 Bot is running with advanced compliance checking...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
