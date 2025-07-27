import os
import yaml
import asyncio
from datetime import datetime
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
from core.database_manager import get_user_stats, update_user_stats, add_log, init_db
from core.compliance_checker import check_product_compliance

# ===== تحميل الإعدادات =====
try:
    with open("config/config.yaml", "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
except FileNotFoundError:
    config = {
        "max_price": 1000000,
        "min_price": 0.01,
        "owner_id": None,
    }

TOKEN = os.getenv("TELEGRAM_TOKEN")
OWNER_ID = config.get("owner_id")

ASK_NAME, ASK_PRICE = range(2)

# ===== تحقق من المالك =====
def is_owner(user_id):
    return OWNER_ID is None or user_id == OWNER_ID

# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("⛔ هذا البوت للاستخدام الشخصي فقط.")
        return

    user_name = update.effective_user.first_name or "مالك البوت"
    welcome_msg = (
        f"👑 أهلاً {user_name}!\n\n"
        f"🤖 **BraveBot Personal Edition** - بدون حدود\n\n"
        f"🔍 `/compliance` - فحص منتج جديد\n"
        f"📊 `/stats` - إحصائياتك\n"
        f"📤 `/export` - تصدير البيانات\n"
        f"🗑️ `/reset` - مسح الإحصائيات\n"
        f"🔧 `/admin` - أدوات المطور\n"
        f"ℹ️ `/help` - المساعدة"
    )
    await update.message.reply_text(welcome_msg, parse_mode="Markdown")
    add_log("بدء تشغيل البوت الشخصي", user_id=update.effective_user.id)

# ===== /help =====
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    help_text = (
        "🆘 **دليل البوت الشخصي:**\n\n"
        "• `/compliance` - فحص منتج جديد (لا محدود)\n"
        "• `/stats` - إحصائياتك الشخصية\n"
        "• `/export` - تصدير البيانات\n"
        "• `/reset` - مسح الإحصائيات\n"
        "• `/admin` - أدوات المطور\n"
        "• `/cancel` - إلغاء العملية"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# ===== /stats =====
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    stats = get_user_stats(update.effective_user.id)
    total = stats["total_checks"]
    passed = stats["passed_checks"]
    failed = stats["failed_checks"]
    success_rate = (passed / total * 100) if total > 0 else 0
    level = "👑 إمبراطور الفحص" if total > 500 else "🔥 متقدم" if total > 100 else "🌱 مبتدئ"

    message = (
        f"📊 **إحصائياتك**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🔍 الإجمالي: {total}\n"
        f"✅ المقبولة: {passed}\n"
        f"❌ المرفوضة: {failed}\n"
        f"📈 النجاح: {success_rate:.1f}%\n"
        f"🏆 المستوى: {level}\n"
    )
    await update.message.reply_text(message, parse_mode="Markdown")

# ===== /compliance =====
async def compliance_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("⛔ هذا البوت للاستخدام الشخصي فقط.")
        return ConversationHandler.END
    await update.message.reply_text("📝 اكتب اسم المنتج:")
    return ASK_NAME

async def compliance_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["product_name"] = update.message.text.strip()
    await update.message.reply_text("💰 اكتب سعر المنتج بالدولار:")
    return ASK_PRICE

async def compliance_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    product_name = context.user_data.get("product_name")
    try:
        price = float(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("⚠️ أدخل رقم صحيح.")
        return ASK_PRICE

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    processing_msg = await update.message.reply_text("🔄 **جارٍ الفحص...**")
    await asyncio.sleep(1)

    result = check_product_compliance({"name": product_name, "price": price, "user_id": user_id})
    is_compliant = result.get("compliant", True)
    reason = result.get("reason", "")

    update_user_stats(user_id, is_compliant, timestamp)
    await processing_msg.delete()

    result_icon = "✅" if is_compliant else "❌"
    await update.message.reply_text(
        f"🔍 المنتج: {product_name}\n"
        f"💰 السعر: ${price:,.2f}\n"
        f"النتيجة: {result_icon} {reason}",
        parse_mode="Markdown"
    )
    return ConversationHandler.END

# ===== /cancel =====
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ تم الإلغاء.")
    return ConversationHandler.END

# ===== إعداد الأوامر =====
async def setup_bot_commands(app):
    commands = [
        BotCommand("start", "بدء البوت"),
        BotCommand("compliance", "فحص منتج"),
        BotCommand("stats", "إحصائياتك"),
        BotCommand("export", "تصدير البيانات"),
        BotCommand("reset", "مسح الإحصائيات"),
        BotCommand("admin", "لوحة تحكم المطور"),
        BotCommand("help", "المساعدة"),
        BotCommand("cancel", "إلغاء"),
    ]
    await app.bot.set_my_commands(commands)

# ===== تشغيل البوت =====
if __name__ == "__main__":
    if not TOKEN:
        print("❌ Error: TELEGRAM_TOKEN not found!")
        exit(1)

    init_db()
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("compliance", compliance_start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, compliance_name)],
            ASK_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, compliance_price)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv_handler)

    async def post_init(app):
        await setup_bot_commands(app)

    app.post_init = post_init
    print("👑 BraveBot Personal Edition is running...")
    app.run_polling(drop_pending_updates=True)
