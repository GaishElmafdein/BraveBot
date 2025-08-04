from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str):
        self.updater = Updater(token, use_context=True)
        self.dispatcher = self.updater.dispatcher

        # Register command handlers
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("help", self.help))
        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.handle_message))

    def start(self, update: Update, context: CallbackContext):
        update.message.reply_text("Welcome to BraveBot! Use /help to see available commands.")

    def help(self, update: Update, context: CallbackContext):
        update.message.reply_text("Available commands:\n/start - Start the bot\n/help - Show this help message")

    def handle_message(self, update: Update, context: CallbackContext):
        user_message = update.message.text
        logger.info(f"Received message: {user_message}")
        update.message.reply_text(f"You said: {user_message}")

    def run(self):
        logger.info("Starting the Telegram bot...")
        self.updater.start_polling()
        self.updater.idle()