import yaml
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# قراءة التوكن من Environment Variable
TOKEN = os.getenv("TELEGRAM_TOKEN")

# قراءة بقية الإعدادات من config.yaml
with open("config/config.yaml", encoding="utf-8") as file:
    config = yaml.safe_load(file)

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("البوت شغال بنجاح مع الإصدار الجديد 🚀")

# تشغيل البوت
if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot is running with python-telegram-bot v20+ ...")
    app.run_polling()
