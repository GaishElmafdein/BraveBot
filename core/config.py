#!/usr/bin/env python3
"""
🏗️ BraveBot Ultimate - Enterprise Configuration System
======================================================
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str = field(default_factory=lambda: os.getenv('DATABASE_URL', 'sqlite:///bravebot.db'))
    pool_size: int = field(default_factory=lambda: int(os.getenv('DB_POOL_SIZE', '10')))
    max_overflow: int = field(default_factory=lambda: int(os.getenv('DB_MAX_OVERFLOW', '20')))
    pool_timeout: int = field(default_factory=lambda: int(os.getenv('DB_POOL_TIMEOUT', '30')))
    echo: bool = field(default_factory=lambda: os.getenv('DB_ECHO', 'false').lower() == 'true')

@dataclass
class TelegramConfig:
    """Telegram Bot configuration"""
    token: str = field(default_factory=lambda: os.getenv('TELEGRAM_TOKEN', ''))
    webhook_url: str = field(default_factory=lambda: os.getenv('TELEGRAM_WEBHOOK_URL', ''))
    admin_ids: List[int] = field(default_factory=lambda: [
        int(x) for x in os.getenv('TELEGRAM_ADMIN_IDS', '').split(',') if x.strip()
    ])
    max_message_length: int = field(default_factory=lambda: int(os.getenv('TELEGRAM_MAX_MSG_LENGTH', '4096')))

@dataclass
class AIConfig:
    """AI and ML configuration"""
    openai_api_key: str = field(default_factory=lambda: os.getenv('OPENAI_API_KEY', ''))
    reddit_client_id: str = field(default_factory=lambda: os.getenv('REDDIT_CLIENT_ID', ''))
    reddit_client_secret: str = field(default_factory=lambda: os.getenv('REDDIT_CLIENT_SECRET', ''))
    reddit_user_agent: str = field(default_factory=lambda: os.getenv('REDDIT_USER_AGENT', 'BraveBot/1.0'))
    confidence_threshold: float = field(default_factory=lambda: float(os.getenv('AI_CONFIDENCE_THRESHOLD', '0.7')))

@dataclass
class TradingConfig:
    """Trading APIs configuration"""
    binance_api_key: str = field(default_factory=lambda: os.getenv('BINANCE_API_KEY', ''))
    binance_api_secret: str = field(default_factory=lambda: os.getenv('BINANCE_API_SECRET', ''))
    binance_testnet: bool = field(default_factory=lambda: os.getenv('BINANCE_TESTNET', 'true').lower() == 'true')
    alpha_vantage_key: str = field(default_factory=lambda: os.getenv('ALPHA_VANTAGE_KEY', ''))
    max_position_size: float = field(default_factory=lambda: float(os.getenv('MAX_POSITION_SIZE', '0.1')))
    stop_loss_percentage: float = field(default_factory=lambda: float(os.getenv('STOP_LOSS_PERCENTAGE', '0.05')))

@dataclass
class AmazonConfig:
    """Amazon SP-API configuration"""
    client_id: str = field(default_factory=lambda: os.getenv('AMAZON_CLIENT_ID', ''))
    client_secret: str = field(default_factory=lambda: os.getenv('AMAZON_CLIENT_SECRET', ''))
    refresh_token: str = field(default_factory=lambda: os.getenv('AMAZON_REFRESH_TOKEN', ''))
    marketplace_id: str = field(default_factory=lambda: os.getenv('AMAZON_MARKETPLACE_ID', 'ATVPDKIKX0DER'))

@dataclass
class EbayConfig:
    """eBay API configuration"""
    app_id: str = field(default_factory=lambda: os.getenv('EBAY_APP_ID', ''))
    dev_id: str = field(default_factory=lambda: os.getenv('EBAY_DEV_ID', ''))
    cert_id: str = field(default_factory=lambda: os.getenv('EBAY_CERT_ID', ''))
    token: str = field(default_factory=lambda: os.getenv('EBAY_TOKEN', ''))

class BraveBotConfig:
    """Master Configuration Class"""
    
    def __init__(self):
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        self.version = os.getenv('APP_VERSION', '1.0.0')
        
        # Initialize configuration sections
        self.database = DatabaseConfig()
        self.telegram = TelegramConfig()
        self.ai = AIConfig()
        self.trading = TradingConfig()
        self.amazon = AmazonConfig()
        self.ebay = EbayConfig()
        
        # Application settings
        self.app_name = "BraveBot Ultimate AI Commerce Empire"
        self.worker_processes = int(os.getenv('WORKER_PROCESSES', '4'))
        self.max_requests = int(os.getenv('MAX_REQUESTS', '1000'))
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Configure application logging"""
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Create logs directory
        Path('logs').mkdir(exist_ok=True)
    
    def is_production(self) -> bool:
        return self.environment == 'production'
    
    def is_development(self) -> bool:
        return self.environment == 'development'

# Global configuration instance
config = BraveBotConfig()

__all__ = ['config', 'BraveBotConfig']