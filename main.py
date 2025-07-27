import os
import yaml
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# قراءة التوكن من Environment Variables
TOKEN = os.getenv("TELEGRAM_TOKEN")

# فحص وجود التوكن
if not TOKEN:
    print("❌ خطأ: TELEGRAM_TOKEN غير موجود في متغيرات البيئة")
    exit(1)

# تحميل إعدادات config.yaml (لو هتحتاجها مستقبلاً)
try:
    with open("config/config.yaml", encoding="utf-8") as file:
        config = yaml.safe_load(file)
except FileNotFoundError:
    print("⚠️ تحذير: ملف config.yaml غير موجود")
    config = {}

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("البوت شغال بنجاح مع الإصدار الجديد 🚀")

# أمر /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🛠 **الأوامر المتاحة حالياً:**\n\n"
        "/start - تأكيد إن البوت شغال\n"
        "/help - عرض هذه القائمة\n\n"
        "✨ أوامر جديدة هتضاف قريب زي (تتبع الترندات / فحص compliance)"
    )
    await update.message.reply_text(help_text)

# نقطة تشغيل البوت
if __name__ == "__main__":
    try:
        app = Application.builder().token(TOKEN).build()

        # إضافة Handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))

        print("🤖 Bot is running with python-telegram-bot v20+ ...")
        print("📝 استخدم Ctrl+C لإيقاف البوت")
        app.run_polling()
        
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت: {e}")
        exit(1)
