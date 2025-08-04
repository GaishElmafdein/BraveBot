import os
import sys
import logging
from core.config import BraveBotConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_system_status():
    """Check the status of various components of the BraveBot application."""
    config = BraveBotConfig()
    
    # Check AI Engine status
    try:
        from core.ai_engine.ai_engine import BraveBotAIEngine
        ai_engine = BraveBotAIEngine()
        ai_status = ai_engine.get_status()
        logger.info(f"AI Engine Status: {ai_status['status']}")
    except Exception as e:
        logger.error(f"Failed to check AI Engine status: {e}")

    # Check Telegram Bot status
    try:
        from bot.telegram_bot import TelegramBot
        telegram_bot = TelegramBot(config.telegram.token)
        bot_status = telegram_bot.get_status()
        logger.info(f"Telegram Bot Status: {bot_status}")
    except Exception as e:
        logger.error(f"Failed to check Telegram Bot status: {e}")

    # Check Dashboard status
    try:
        # Assuming the dashboard has a method to check its status
        from dashboard.app import Dashboard
        dashboard = Dashboard()
        dashboard_status = dashboard.get_status()
        logger.info(f"Dashboard Status: {dashboard_status}")
    except Exception as e:
        logger.error(f"Failed to check Dashboard status: {e}")

if __name__ == "__main__":
    check_system_status()