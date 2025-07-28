#!/usr/bin/env python3
"""
📱 Telegram Push Notifications
=============================
إرسال تنبيهات فورية عند الترندات الساخنة
"""

import asyncio
import telegram
from telegram import Bot
from datetime import datetime
import json
import logging
from pathlib import Path

# إعداد اللوغ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramAlerts:
    """نظام التنبيهات عبر تيليجرام"""
    
    def __init__(self, bot_token: str = None):
        self.bot_token = bot_token or "YOUR_BOT_TOKEN"
        self.bot = Bot(token=self.bot_token)
        
        # قائمة المشتركين (يمكن حفظها في قاعدة البيانات)
        self.subscribers = self._load_subscribers()
        
        # حدود التنبيهات
        self.viral_threshold = 80  # نقاط الانتشار للتنبيه
        self.price_drop_threshold = 20  # نسبة انخفاض السعر %
    
    def _load_subscribers(self) -> dict:
        """تحميل قائمة المشتركين"""
        subscribers_file = Path("data/subscribers.json")
        
        if subscribers_file.exists():
            with open(subscribers_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # مشتركين افتراضيين للتجربة
        return {
            "123456789": {  # Telegram User ID
                "name": "المستخدم التجريبي",
                "interests": ["technology", "crypto", "gaming"],
                "notifications": {
                    "viral_trends": True,
                    "price_alerts": True,
                    "weekly_reports": True
                },
                "joined_date": datetime.now().isoformat()
            }
        }
    
    def _save_subscribers(self):
        """حفظ قائمة المشتركين"""
        subscribers_file = Path("data/subscribers.json")
        subscribers_file.parent.mkdir(exist_ok=True)
        
        with open(subscribers_file, 'w', encoding='utf-8') as f:
            json.dump(self.subscribers, f, ensure_ascii=False, indent=2, default=str)
    
    async def send_viral_trend_alert(self, trend_data: dict):
        """إرسال تنبيه للترند الساخن"""
        
        viral_score = trend_data.get('overall_viral_score', 0)
        
        if viral_score < self.viral_threshold:
            return
        
        # تحضير الرسالة
        keyword = trend_data.get('keyword', 'غير محدد')
        category = trend_data.get('trend_category', '📈 ترند')
        
        message = f"""
🔥 **تنبيه ترند ساخن!** 🔥

📊 **الكلمة المفتاحية:** {keyword}
⭐ **نقاط الانتشار:** {viral_score}/100
🏷️ **التصنيف:** {category}

📈 **توصياتنا:**
• استغل هذا الترند فوراً!
• انشر محتوى متعلق الآن
• راقب المنافسين

🕒 **الوقت:** {datetime.now().strftime('%H:%M - %d/%m/%Y')}

---
🤖 BraveBot Dashboard
        """
        
        # إرسال للمشتركين المهتمين
        sent_count = 0
        for user_id, user_data in self.subscribers.items():
            try:
                if user_data.get('notifications', {}).get('viral_trends', True):
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                    sent_count += 1
                    await asyncio.sleep(0.1)  # تجنب Rate Limiting
                    
            except Exception as e:
                logger.error(f"خطأ إرسال تنبيه للمستخدم {user_id}: {e}")
        
        logger.info(f"تم إرسال تنبيه الترند الساخن لـ {sent_count} مستخدم")
    
    async def send_price_alert(self, price_data: dict):
        """إرسال تنبيه انخفاض الأسعار"""
        
        keyword = price_data.get('keyword', 'غير محدد')
        best_deal = price_data.get('best_deals', [{}])[0]
        
        if not best_deal:
            return
        
        message = f"""
💰 **تنبيه سعر مميز!** 💰

🛒 **المنتج:** {best_deal.get('title', 'غير محدد')[:50]}...
💵 **السعر:** ${best_deal.get('price', 0):.2f}
🏪 **المتجر:** {best_deal.get('source', 'غير محدد')}
🔗 **الرابط:** {best_deal.get('url', '#')}

📊 **مقارنة الأسعار:**
• أقل سعر: ${price_data.get('price_analysis', {}).get('min_price', 0):.2f}
• متوسط السعر: ${price_data.get('price_analysis', {}).get('avg_price', 0):.2f}

🕒 **الوقت:** {datetime.now().strftime('%H:%M - %d/%m/%Y')}

---
🤖 BraveBot Dashboard
        """
        
        # إرسال للمشتركين
        sent_count = 0
        for user_id, user_data in self.subscribers.items():
            try:
                if user_data.get('notifications', {}).get('price_alerts', True):
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                    sent_count += 1
                    await asyncio.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"خطأ إرسال تنبيه السعر للمستخدم {user_id}: {e}")
        
        logger.info(f"تم إرسال تنبيه الأسعار لـ {sent_count} مستخدم")
    
    async def send_custom_alert(self, message: str, user_ids: list = None):
        """إرسال تنبيه مخصص"""
        
        target_users = user_ids or list(self.subscribers.keys())
        sent_count = 0
        
        for user_id in target_users:
            try:
                await self.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode='Markdown'
                )
                sent_count += 1
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"خطأ إرسال رسالة مخصصة للمستخدم {user_id}: {e}")
        
        logger.info(f"تم إرسال الرسالة المخصصة لـ {sent_count} مستخدم")
    
    def add_subscriber(self, user_id: str, user_data: dict):
        """إضافة مشترك جديد"""
        self.subscribers[user_id] = user_data
        self._save_subscribers()
        logger.info(f"تم إضافة مشترك جديد: {user_id}")
    
    def remove_subscriber(self, user_id: str):
        """إزالة مشترك"""
        if user_id in self.subscribers:
            del self.subscribers[user_id]
            self._save_subscribers()
            logger.info(f"تم إزالة مشترك: {user_id}")

# إنشاء instance عالمي
telegram_alerts = TelegramAlerts()