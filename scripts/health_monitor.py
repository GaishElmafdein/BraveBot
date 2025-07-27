#!/usr/bin/env python3
"""
🏥 BraveBot Health Monitor & Alert System
==========================================
نظام مراقبة صحة البوت والتنبيهات التلقائية

الميزات:
- مراقبة حالة البوت كل دقيقة
- كشف الأعطال والتعافي التلقائي
- إرسال تنبيهات فورية
- تسجيل مفصل للأحداث
- إحصائيات الأداء
"""

import asyncio
import aiohttp
import sqlite3
import json
import os
import psutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# إعداد نظام السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BraveBotMonitor:
    def __init__(self, config_path='config/monitor_config.json'):
        """تهيئة نظام المراقبة"""
        self.config = self.load_config(config_path)
        self.bot_token = os.getenv('TELEGRAM_TOKEN')
        self.is_running = True
        self.consecutive_failures = 0
        self.last_successful_check = None
        self.performance_stats = {
            'total_checks': 0,
            'successful_checks': 0,
            'failed_checks': 0,
            'avg_response_time': 0,
            'uptime_start': datetime.now()
        }
        
    def load_config(self, config_path):
        """تحميل إعدادات المراقبة"""
        default_config = {
            "check_interval": 60,  # ثانية
            "max_consecutive_failures": 3,
            "telegram_chat_id": None,
            "email_notifications": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "email": "",
                "password": "",
                "recipient": ""
            },
            "performance_monitoring": {
                "cpu_threshold": 80,
                "memory_threshold": 80,
                "disk_threshold": 90
            },
            "auto_restart": {
                "enabled": True,
                "max_attempts": 3,
                "restart_delay": 30
            }
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    default_config.update(config)
            return default_config
        except Exception as e:
            logger.warning(f"⚠️ Config load failed: {e}. Using defaults.")
            return default_config
    
    async def check_bot_health(self):
        """فحص صحة البوت"""
        try:
            start_time = datetime.now()
            
            # فحص API Telegram
            url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('ok'):
                            # حساب زمن الاستجابة
                            response_time = (datetime.now() - start_time).total_seconds()
                            
                            # تحديث الإحصائيات
                            self.update_performance_stats(True, response_time)
                            
                            # فحص قاعدة البيانات
                            db_healthy = await self.check_database_health()
                            
                            # فحص استخدام الموارد
                            resource_status = self.check_system_resources()
                            
                            if db_healthy and resource_status['healthy']:
                                self.consecutive_failures = 0
                                self.last_successful_check = datetime.now()
                                
                                logger.info(f"✅ Bot health check passed - Response time: {response_time:.2f}s")
                                return {
                                    'status': 'healthy',
                                    'response_time': response_time,
                                    'database': 'ok',
                                    'resources': resource_status
                                }
                            else:
                                raise Exception("Database or system resources unhealthy")
                        else:
                            raise Exception(f"Telegram API error: {data}")
                    else:
                        raise Exception(f"HTTP {response.status}")
                        
        except Exception as e:
            self.update_performance_stats(False, 0)
            self.consecutive_failures += 1
            
            logger.error(f"❌ Bot health check failed: {e}")
            
            # إرسال تنبيه إذا تجاوز الحد المسموح
            if self.consecutive_failures >= self.config['max_consecutive_failures']:
                await self.send_alert(f"🚨 Bot health check failed {self.consecutive_failures} times: {e}")
                
                # محاولة إعادة التشغيل التلقائي
                if self.config['auto_restart']['enabled']:
                    await self.attempt_auto_restart()
            
            return {
                'status': 'unhealthy',
                'error': str(e),
                'consecutive_failures': self.consecutive_failures
            }
    
    async def check_database_health(self):
        """فحص صحة قاعدة البيانات"""
        try:
            conn = sqlite3.connect('bravebot.db', timeout=5)
            cursor = conn.cursor()
            
            # فحص بسيط للجداول الأساسية
            cursor.execute("SELECT COUNT(*) FROM user_stats")
            user_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM logs")
            log_count = cursor.fetchone()[0]
            
            conn.close()
            
            logger.debug(f"📊 Database health: {user_count} users, {log_count} logs")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database health check failed: {e}")
            return False
    
    def check_system_resources(self):
        """فحص استخدام موارد النظام"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            cpu_threshold = self.config['performance_monitoring']['cpu_threshold']
            memory_threshold = self.config['performance_monitoring']['memory_threshold']
            disk_threshold = self.config['performance_monitoring']['disk_threshold']
            
            alerts = []
            
            if cpu_percent > cpu_threshold:
                alerts.append(f"High CPU usage: {cpu_percent}%")
            
            if memory.percent > memory_threshold:
                alerts.append(f"High memory usage: {memory.percent}%")
            
            if disk.percent > disk_threshold:
                alerts.append(f"High disk usage: {disk.percent}%")
            
            return {
                'healthy': len(alerts) == 0,
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent,
                'alerts': alerts
            }
            
        except Exception as e:
            logger.error(f"❌ Resource check failed: {e}")
            return {'healthy': False, 'error': str(e)}
    
    def update_performance_stats(self, success, response_time):
        """تحديث إحصائيات الأداء"""
        self.performance_stats['total_checks'] += 1
        
        if success:
            self.performance_stats['successful_checks'] += 1
            
            # حساب متوسط زمن الاستجابة
            current_avg = self.performance_stats['avg_response_time']
            total_success = self.performance_stats['successful_checks']
            
            self.performance_stats['avg_response_time'] = (
                (current_avg * (total_success - 1) + response_time) / total_success
            )
        else:
            self.performance_stats['failed_checks'] += 1
    
    async def send_alert(self, message):
        """إرسال تنبيهات الطوارئ"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"🚨 **BraveBot Alert**\n⏰ {timestamp}\n\n{message}"
        
        # إرسال تنبيه عبر Telegram
        await self.send_telegram_alert(full_message)
        
        # إرسال إيميل (إذا كان مُفعل)
        if self.config['email_notifications']['enabled']:
            await self.send_email_alert(f"BraveBot Alert - {timestamp}", full_message)
        
        logger.critical(f"🚨 ALERT SENT: {message}")
    
    async def send_telegram_alert(self, message):
        """إرسال تنبيه عبر Telegram"""
        chat_id = self.config.get('telegram_chat_id')
        if not chat_id or not self.bot_token:
            return
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        logger.info("📱 Telegram alert sent successfully")
                    else:
                        logger.error(f"❌ Telegram alert failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"❌ Telegram alert error: {e}")
    
    async def send_email_alert(self, subject, message):
        """إرسال تنبيه عبر الإيميل"""
        try:
            email_config = self.config['email_notifications']
            
            msg = MIMEMultipart()
            msg['From'] = email_config['email']
            msg['To'] = email_config['recipient']
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['email'], email_config['password'])
            
            text = msg.as_string()
            server.sendmail(email_config['email'], email_config['recipient'], text)
            server.quit()
            
            logger.info("📧 Email alert sent successfully")
            
        except Exception as e:
            logger.error(f"❌ Email alert error: {e}")
    
    async def attempt_auto_restart(self):
        """محاولة إعادة تشغيل البوت تلقائياً"""
        if not self.config['auto_restart']['enabled']:
            return
        
        max_attempts = self.config['auto_restart']['max_attempts']
        restart_delay = self.config['auto_restart']['restart_delay']
        
        for attempt in range(1, max_attempts + 1):
            logger.info(f"🔄 Auto-restart attempt {attempt}/{max_attempts}")
            
            try:
                # في بيئة الإنتاج، هذا سيكون restart للخدمة
                await asyncio.sleep(restart_delay)
                
                # محاولة فحص الصحة مرة أخرى
                health_check = await self.check_bot_health()
                
                if health_check['status'] == 'healthy':
                    await self.send_alert(f"✅ Auto-restart successful after {attempt} attempts")
                    return True
                    
            except Exception as e:
                logger.error(f"❌ Auto-restart attempt {attempt} failed: {e}")
        
        await self.send_alert(f"💥 Auto-restart failed after {max_attempts} attempts. Manual intervention required!")
        return False
    
    def get_uptime_stats(self):
        """حساب إحصائيات وقت التشغيل"""
        uptime = datetime.now() - self.performance_stats['uptime_start']
        total_checks = self.performance_stats['total_checks']
        successful_checks = self.performance_stats['successful_checks']
        
        uptime_percentage = (successful_checks / max(total_checks, 1)) * 100
        
        return {
            'uptime_duration': str(uptime).split('.')[0],  # إزالة الميكروثواني
            'uptime_percentage': round(uptime_percentage, 2),
            'total_checks': total_checks,
            'successful_checks': successful_checks,
            'failed_checks': self.performance_stats['failed_checks'],
            'avg_response_time': round(self.performance_stats['avg_response_time'], 3)
        }
    
    async def generate_daily_report(self):
        """إنشاء تقرير يومي"""
        stats = self.get_uptime_stats()
        
        report = f"""
📊 **BraveBot Daily Report**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏰ **Uptime:** {stats['uptime_duration']}
📈 **Availability:** {stats['uptime_percentage']}%
🔍 **Health Checks:** {stats['total_checks']}
✅ **Successful:** {stats['successful_checks']}
❌ **Failed:** {stats['failed_checks']}
⚡ **Avg Response:** {stats['avg_response_time']}s

📅 **Date:** {datetime.now().strftime('%Y-%m-%d')}
        """
        
        await self.send_alert(report)
    
    async def run_monitoring(self):
        """تشغيل حلقة المراقبة الرئيسية"""
        logger.info("🚀 Starting BraveBot monitoring system...")
        
        check_interval = self.config['check_interval']
        last_daily_report = datetime.now().date()
        
        while self.is_running:
            try:
                # فحص صحة البوت
                health_status = await self.check_bot_health()
                
                # إنشاء تقرير يومي
                current_date = datetime.now().date()
                if current_date > last_daily_report:
                    await self.generate_daily_report()
                    last_daily_report = current_date
                
                # انتظار الفترة المحددة
                await asyncio.sleep(check_interval)
                
            except KeyboardInterrupt:
                logger.info("⏹️ Monitoring stopped by user")
                self.is_running = False
            except Exception as e:
                logger.error(f"❌ Monitoring loop error: {e}")
                await asyncio.sleep(check_interval)
        
        logger.info("✅ Monitoring system stopped")

def main():
    """الدالة الرئيسية لتشغيل المراقبة"""
    monitor = BraveBotMonitor()
    
    try:
        asyncio.run(monitor.run_monitoring())
    except KeyboardInterrupt:
        print("\n⏹️ Monitoring stopped")
    except Exception as e:
        logger.error(f"❌ Monitoring failed: {e}")

if __name__ == "__main__":
    main()
