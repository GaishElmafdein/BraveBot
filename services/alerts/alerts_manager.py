#!/usr/bin/env python3
"""
🚨 Advanced Alerts Manager
==========================
نظام التنبيهات المتقدم للتجارة والتداول
"""

import asyncio
import logging
import sqlite3
import json
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import requests

class AlertType(Enum):
    PROFIT_THRESHOLD = "profit_threshold"
    STOCK_DEPLETION = "stock_depletion"
    COMPETITOR_PRICE = "competitor_price"
    TRADING_SIGNAL = "trading_signal"
    MARKET_VOLATILITY = "market_volatility"
    SYSTEM_HEALTH = "system_health"
    WHALE_MOVEMENT = "whale_movement"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"

class AlertPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Alert:
    id: str
    type: AlertType
    priority: AlertPriority
    title: str
    message: str
    data: Dict[str, Any]
    created_at: datetime
    is_read: bool
    user_id: str
    account_id: Optional[str]

class AlertsManager:
    def __init__(self, db_path: str = "bravebot.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.active_monitors = {}
        self.alert_handlers = {}
        self._init_database()
    
    def _init_database(self):
        """إنشاء جداول التنبيهات"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_read BOOLEAN DEFAULT 0,
                    user_id TEXT NOT NULL,
                    account_id TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alert_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    is_enabled BOOLEAN DEFAULT 1,
                    settings TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    async def create_alert(
        self,
        alert_type: AlertType,
        priority: AlertPriority,
        title: str,
        message: str,
        user_id: str,
        data: Dict[str, Any] = None,
        account_id: str = None
    ) -> str:
        """إنشاء تنبيه جديد"""
        
        alert_id = f"alert_{alert_type.value}_{int(datetime.now().timestamp())}_{user_id}"
        
        alert = Alert(
            id=alert_id,
            type=alert_type,
            priority=priority,
            title=title,
            message=message,
            data=data or {},
            created_at=datetime.now(),
            is_read=False,
            user_id=user_id,
            account_id=account_id
        )
        
        # حفظ في قاعدة البيانات
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO alerts 
                (id, type, priority, title, message, data, user_id, account_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                alert.id,
                alert.type.value,
                alert.priority.value,
                alert.title,
                alert.message,
                json.dumps(alert.data),
                alert.user_id,
                alert.account_id
            ))
            conn.commit()
        
        # إرسال التنبيه
        await self._send_alert(alert)
        
        self.logger.info(f"Alert created: {alert_id} ({alert_type.value})")
        return alert_id
    
    async def _send_alert(self, alert: Alert):
        """إرسال التنبيه عبر القنوات المختلفة"""
        
        # إرسال عبر التليجرام
        await self._send_telegram_alert(alert)
        
        # إرسال إيميل (اختياري)
        if alert.priority in [AlertPriority.HIGH, AlertPriority.CRITICAL]:
            await self._send_email_alert(alert)
    
    async def _send_telegram_alert(self, alert: Alert):
        """إرسال تنبيه عبر التليجرام"""
        
        try:
            # استيراد بوت التليجرام
            import os
            from telegram import Bot
            
            bot_token = os.getenv('TELEGRAM_TOKEN')
            if not bot_token:
                return
            
            bot = Bot(token=bot_token)
            
            # تنسيق الرسالة
            priority_emoji = {
                AlertPriority.LOW: "ℹ️",
                AlertPriority.MEDIUM: "⚠️",
                AlertPriority.HIGH: "🔥",
                AlertPriority.CRITICAL: "🚨"
            }
            
            message = f"""
{priority_emoji.get(alert.priority, '📢')} **{alert.title}**

{alert.message}

🕐 {alert.created_at.strftime('%Y-%m-%d %H:%M:%S')}
📊 النوع: {alert.type.value}
⚡ الأولوية: {alert.priority.value}
            """
            
            # إرسال للمستخدم (نحتاج chat_id من user_id)
            # هذا مبسط - في الواقع نحتاج ربط user_id بـ chat_id
            chat_id = await self._get_user_chat_id(alert.user_id)
            if chat_id:
                await bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            self.logger.error(f"Failed to send Telegram alert: {e}")
    
    async def _send_email_alert(self, alert: Alert):
        """إرسال تنبيه عبر الإيميل"""
        # تنفيذ بسيط - in production استخدم مكتبة مثل sendgrid
        pass
    
    async def _get_user_chat_id(self, user_id: str) -> Optional[str]:
        """جلب chat_id للمستخدم"""
        # في database محفوظ ربط user_id بـ chat_id
        # مبسط للمثال
        return None
    
    # مراقبات متخصصة
    async def start_profit_monitor(
        self,
        user_id: str,
        threshold: float,
        product_id: str = None
    ):
        """مراقبة حد الربح"""
        
        monitor_id = f"profit_monitor_{user_id}_{int(datetime.now().timestamp())}"
        
        async def monitor():
            while monitor_id in self.active_monitors:
                try:
                    # فحص الأرباح الحالية
                    current_profit = await self._calculate_current_profit(user_id, product_id)
                    
                    if current_profit >= threshold:
                        await self.create_alert(
                            AlertType.PROFIT_THRESHOLD,
                            AlertPriority.HIGH,
                            "🎯 هدف الربح تحقق!",
                            f"تحقق ربح قدره ${current_profit:.2f} (الهدف: ${threshold:.2f})",
                            user_id,
                            {"current_profit": current_profit, "threshold": threshold}
                        )
                        
                        # إيقاف المراقبة بعد التنبيه
                        break
                    
                    await asyncio.sleep(300)  # فحص كل 5 دقائق
                    
                except Exception as e:
                    self.logger.error(f"Profit monitor error: {e}")
                    await asyncio.sleep(60)
        
        self.active_monitors[monitor_id] = asyncio.create_task(monitor())
        return monitor_id
    
    async def start_stock_monitor(
        self,
        user_id: str,
        product_id: str,
        threshold: int = 5
    ):
        """مراقبة نفاد المخزون"""
        
        monitor_id = f"stock_monitor_{user_id}_{product_id}"
        
        async def monitor():
            while monitor_id in self.active_monitors:
                try:
                    # فحص المخزون الحالي
                    current_stock = await self._get_product_stock(product_id)
                    
                    if current_stock <= threshold:
                        await self.create_alert(
                            AlertType.STOCK_DEPLETION,
                            AlertPriority.MEDIUM,
                            "📦 مخزون منخفض!",
                            f"المنتج {product_id} متبقي منه {current_stock} قطع فقط",
                            user_id,
                            {"product_id": product_id, "current_stock": current_stock}
                        )
                    
                    await asyncio.sleep(3600)  # فحص كل ساعة
                    
                except Exception as e:
                    self.logger.error(f"Stock monitor error: {e}")
                    await asyncio.sleep(300)
        
        self.active_monitors[monitor_id] = asyncio.create_task(monitor())
        return monitor_id
    
    async def start_competitor_price_monitor(
        self,
        user_id: str,
        product_id: str,
        competitor_urls: List[str]
    ):
        """مراقبة أسعار المنافسين"""
        
        monitor_id = f"competitor_monitor_{user_id}_{product_id}"
        
        async def monitor():
            last_prices = {}
            
            while monitor_id in self.active_monitors:
                try:
                    for url in competitor_urls:
                        current_price = await self._scrape_competitor_price(url)
                        
                        if url in last_prices:
                            price_change = current_price - last_prices[url]
                            
                            if abs(price_change) > 5:  # تغيير بأكثر من $5
                                direction = "انخفض" if price_change < 0 else "ارتفع"
                                
                                await self.create_alert(
                                    AlertType.COMPETITOR_PRICE,
                                    AlertPriority.MEDIUM,
                                    "💰 تغيير سعر المنافس",
                                    f"السعر {direction} بمقدار ${abs(price_change):.2f}\nالسعر الجديد: ${current_price:.2f}",
                                    user_id,
                                    {
                                        "product_id": product_id,
                                        "competitor_url": url,
                                        "old_price": last_prices[url],
                                        "new_price": current_price,
                                        "change": price_change
                                    }
                                )
                        
                        last_prices[url] = current_price
                    
                    await asyncio.sleep(7200)  # فحص كل ساعتين
                    
                except Exception as e:
                    self.logger.error(f"Competitor monitor error: {e}")
                    await asyncio.sleep(600)
        
        self.active_monitors[monitor_id] = asyncio.create_task(monitor())
        return monitor_id
    
    # Trading Alerts
    async def start_crypto_whale_monitor(
        self,
        user_id: str,
        symbol: str,
        threshold_amount: float
    ):
        """مراقبة حركات الحيتان في العملات المشفرة"""
        
        monitor_id = f"whale_monitor_{user_id}_{symbol}"
        
        async def monitor():
            while monitor_id in self.active_monitors:
                try:
                    # فحص المعاملات الكبيرة
                    whale_transactions = await self._get_whale_transactions(symbol, threshold_amount)
                    
                    for tx in whale_transactions:
                        await self.create_alert(
                            AlertType.WHALE_MOVEMENT,
                            AlertPriority.HIGH,
                            "🐋 حركة حوت كبيرة!",
                            f"معاملة {symbol} بقيمة ${tx['amount']:,.2f}\nالاتجاه: {tx['direction']}",
                            user_id,
                            tx
                        )
                    
                    await asyncio.sleep(300)  # فحص كل 5 دقائق
                    
                except Exception as e:
                    self.logger.error(f"Whale monitor error: {e}")
                    await asyncio.sleep(60)
        
        self.active_monitors[monitor_id] = asyncio.create_task(monitor())
        return monitor_id
    
    # Helper functions
    async def _calculate_current_profit(
        self, 
        user_id: str, 
        product_id: str = None
    ) -> float:
        """حساب الربح الحالي"""
        # تنفيذ مبسط - في الواقع يحسب من المبيعات والمشتريات
        return 0.0
    
    async def _get_product_stock(self, product_id: str) -> int:
        """جلب مخزون المنتج"""
        # تنفيذ مبسط - يجلب من Amazon/eBay APIs
        return 0
    
    async def _scrape_competitor_price(self, url: str) -> float:
        """استخراج سعر المنافس"""
        # تنفيذ مبسط - web scraping
        return 0.0
    
    async def _get_whale_transactions(
        self, 
        symbol: str, 
        threshold: float
    ) -> List[Dict]:
        """جلب معاملات الحيتان"""
        # تنفيذ مبسط - استخدام APIs مثل Whale Alert
        return []
    
    def stop_monitor(self, monitor_id: str):
        """إيقاف مراقب معين"""
        if monitor_id in self.active_monitors:
            self.active_monitors[monitor_id].cancel()
            del self.active_monitors[monitor_id]
            self.logger.info(f"Monitor stopped: {monitor_id}")
    
    def get_user_alerts(
        self, 
        user_id: str, 
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Dict]:
        """جلب تنبيهات المستخدم"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM alerts WHERE user_id = ?"
            params = [user_id]
            
            if unread_only:
                query += " AND is_read = 0"
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            
            alerts = []
            for row in cursor.fetchall():
                alerts.append({
                    'id': row[0],
                    'type': row[1],
                    'priority': row[2],
                    'title': row[3],
                    'message': row[4],
                    'data': json.loads(row[5]) if row[5] else {},
                    'created_at': row[6],
                    'is_read': bool(row[7])
                })
            
            return alerts
    
    def mark_alert_read(self, alert_id: str) -> bool:
        """تحديد التنبيه كمقروء"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE alerts 
                SET is_read = 1
                WHERE id = ?
            """, (alert_id,))
            
            success = cursor.rowcount > 0
            if success:
                conn.commit()
            
            return success

# تصدير الفئة
__all__ = ['AlertsManager', 'Alert', 'AlertType', 'AlertPriority']