import logging
from core.ai_engine.ai_engine import BraveBotAIEngine
from bot.telegram_bot import TelegramBot
from dashboard.app import Dashboard

def check_system_status():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Check AI Engine status
    ai_engine = BraveBotAIEngine()
    ai_status = ai_engine.get_status()
    logger.info(f"AI Engine Status: {ai_status['status']}")

    # Check Telegram Bot status
    telegram_bot = TelegramBot()
    bot_status = telegram_bot.get_status()
    logger.info(f"Telegram Bot Status: {bot_status}")

    # Check Dashboard status
    dashboard = Dashboard()
    dashboard_status = dashboard.get_status()
    logger.info(f"Dashboard Status: {dashboard_status}")

if __name__ == "__main__":
    check_system_status()