#!/usr/bin/env python3
"""
🔄 BraveBot Auto-Update & Enhancement System
============================================
نظام التحديثات التلقائية والتحسينات المستقبلية

الميزات:
- تحديثات تلقائية من GitHub
- إشعارات الإنجازات الأسبوعية
- نظام التحسينات التدريجية
- إحصائيات متقدمة
"""

import asyncio
import json
import os
import subprocess
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BraveBotEnhancer:
    def __init__(self):
        self.config_path = Path("config/enhancement_config.json")
        self.config = self.load_config()
        
    def load_config(self):
        """تحميل إعدادات التحسينات"""
        default_config = {
            "auto_update": {
                "enabled": True,
                "check_interval_hours": 24,
                "backup_before_update": True
            },
            "weekly_achievements": {
                "enabled": True,
                "send_day": "sunday",
                "send_time": "18:00"
            },
            "feature_flags": {
                "advanced_analytics": True,
                "user_recommendations": True,
                "achievement_predictions": True
            },
            "version": "2.0.0"
        }
        
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    default_config.update(config)
            return default_config
        except Exception as e:
            logger.warning(f"Config load failed: {e}")
            return default_config
    
    async def check_for_updates(self):
        """فحص التحديثات المتاحة من GitHub"""
        try:
            # فحص الـ commits الجديدة
            result = subprocess.run(
                ["git", "fetch", "origin"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # فحص إذا كان هناك تحديثات
                result = subprocess.run(
                    ["git", "rev-list", "HEAD..origin/main", "--count"],
                    capture_output=True,
                    text=True
                )
                
                updates_count = int(result.stdout.strip())
                
                if updates_count > 0:
                    logger.info(f"🔄 {updates_count} updates available")
                    return await self.apply_updates()
                else:
                    logger.info("✅ BraveBot is up to date")
                    return True
            
        except Exception as e:
            logger.error(f"❌ Update check failed: {e}")
            return False
    
    async def apply_updates(self):
        """تطبيق التحديثات"""
        try:
            # إنشاء نسخة احتياطية قبل التحديث
            if self.config["auto_update"]["backup_before_update"]:
                logger.info("📥 Creating backup before update...")
                from scripts.backup_system import BraveBotBackup
                backup = BraveBotBackup()
                backup.create_backup()
            
            # تطبيق التحديث
            result = subprocess.run(
                ["git", "pull", "origin", "main"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("✅ Update applied successfully")
                
                # إعادة تشغيل البوت (في بيئة الإنتاج)
                await self.restart_bot()
                return True
            else:
                logger.error(f"❌ Update failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Update application failed: {e}")
            return False
    
    async def restart_bot(self):
        """إعادة تشغيل البوت بعد التحديث"""
        logger.info("🔄 Restarting bot after update...")
        # في بيئة الإنتاج، هذا سيستخدم خدمة النظام
        pass
    
    async def send_weekly_achievements_report(self):
        """إرسال تقرير الإنجازات الأسبوعي"""
        try:
            # جمع إحصائيات آخر أسبوع
            week_ago = datetime.now() - timedelta(days=7)
            
            conn = sqlite3.connect('bravebot.db')
            cursor = conn.cursor()
            
            # إحصائيات المستخدمين النشطين
            cursor.execute("""
                SELECT COUNT(DISTINCT user_id) 
                FROM logs 
                WHERE timestamp > ? AND message LIKE '%فحص%'
            """, (week_ago.isoformat(),))
            
            active_users = cursor.fetchone()[0]
            
            # إجمالي الفحوص الأسبوعية
            cursor.execute("""
                SELECT COUNT(*) 
                FROM logs 
                WHERE timestamp > ? AND message LIKE '%فحص%'
            """, (week_ago.isoformat(),))
            
            weekly_checks = cursor.fetchone()[0]
            
            # أفضل المستخدمين
            cursor.execute("""
                SELECT user_id, total_checks 
                FROM user_stats 
                ORDER BY total_checks DESC 
                LIMIT 5
            """)
            
            top_users = cursor.fetchall()
            conn.close()
            
            # إنشاء التقرير
            report = self.generate_weekly_report(
                active_users, weekly_checks, top_users
            )
            
            # إرسال التقرير لجميع المستخدمين النشطين
            await self.broadcast_weekly_report(report)
            
        except Exception as e:
            logger.error(f"❌ Weekly report failed: {e}")
    
    def generate_weekly_report(self, active_users, weekly_checks, top_users):
        """إنشاء تقرير أسبوعي مفصل"""
        report = f"""
🏆 **التقرير الأسبوعي - BraveBot**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **إحصائيات الأسبوع:**
👥 المستخدمون النشطون: **{active_users:,}**
🔍 إجمالي الفحوص: **{weekly_checks:,}**
📈 متوسط الفحوص لكل مستخدم: **{weekly_checks/max(active_users,1):.1f}**

🥇 **المتصدرون:**
"""
        
        for i, (user_id, total_checks) in enumerate(top_users, 1):
            medal = ["🥇", "🥈", "🥉", "🏅", "⭐"][i-1] if i <= 5 else "👤"
            report += f"{medal} المركز {i}: **{total_checks:,}** فحص\n"
        
        report += f"""
🎯 **نصائح للأسبوع القادم:**
• استخدم `/achievements` لمتابعة تقدمك
• جرب فحص منتجات متنوعة
• ادع أصدقاءك لاستخدام البوت

💡 **تذكير:** البوت يُحدث تلقائياً لخدمة أفضل!

📅 **تاريخ التقرير:** {datetime.now().strftime('%Y-%m-%d')}
        """
        
        return report
    
    async def broadcast_weekly_report(self, report):
        """إرسال التقرير لجميع المستخدمين"""
        try:
            # هذا سيتطلب integration مع البوت الأساسي
            logger.info("📤 Broadcasting weekly report to all users")
            
            # في التطبيق الحقيقي، سنحتاج إلى:
            # 1. الحصول على قائمة المستخدمين النشطين
            # 2. إرسال الرسالة لكل مستخدم
            # 3. تسجيل حالة الإرسال
            
        except Exception as e:
            logger.error(f"❌ Report broadcast failed: {e}")
    
    async def analyze_user_patterns(self):
        """تحليل أنماط استخدام المستخدمين"""
        try:
            conn = sqlite3.connect('bravebot.db')
            cursor = conn.cursor()
            
            # تحليل أوقات الذروة
            cursor.execute("""
                SELECT strftime('%H', timestamp) as hour, COUNT(*) as count
                FROM logs 
                WHERE message LIKE '%فحص%' 
                GROUP BY hour 
                ORDER BY count DESC
            """)
            
            peak_hours = cursor.fetchall()
            
            # تحليل الأيام الأكثر نشاطاً
            cursor.execute("""
                SELECT strftime('%w', timestamp) as day_of_week, COUNT(*) as count
                FROM logs 
                WHERE message LIKE '%فحص%' 
                GROUP BY day_of_week 
                ORDER BY count DESC
            """)
            
            active_days = cursor.fetchall()
            
            conn.close()
            
            patterns = {
                'peak_hours': peak_hours[:3],  # أفضل 3 ساعات
                'active_days': active_days[:3],  # أفضل 3 أيام
                'analysis_date': datetime.now().isoformat()
            }
            
            # حفظ النتائج للاستفادة منها لاحقاً
            with open('analytics/user_patterns.json', 'w', encoding='utf-8') as f:
                json.dump(patterns, f, ensure_ascii=False, indent=2)
            
            logger.info("📊 User patterns analysis completed")
            return patterns
            
        except Exception as e:
            logger.error(f"❌ Pattern analysis failed: {e}")
            return {}
    
    async def predict_user_achievements(self, user_id):
        """توقع الإنجازات المستقبلية للمستخدمين"""
        try:
            conn = sqlite3.connect('bravebot.db')
            cursor = conn.cursor()
            
            # الحصول على إحصائيات المستخدم
            cursor.execute("""
                SELECT total_checks, 
                       datetime(last_check) as last_check,
                       datetime(joined_date) as joined_date
                FROM user_stats 
                WHERE user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            total_checks, last_check, joined_date = result
            
            # حساب معدل النشاط
            if joined_date:
                join_date = datetime.fromisoformat(joined_date)
                days_active = (datetime.now() - join_date).days or 1
                daily_rate = total_checks / days_active
                
                # التنبؤ بالإنجازات المستقبلية
                next_milestones = [25, 50, 100, 250, 500, 1000]
                predictions = []
                
                for milestone in next_milestones:
                    if total_checks < milestone:
                        remaining = milestone - total_checks
                        days_to_achieve = remaining / max(daily_rate, 0.1)
                        
                        predictions.append({
                            'milestone': milestone,
                            'days_remaining': int(days_to_achieve),
                            'estimated_date': (datetime.now() + timedelta(days=days_to_achieve)).strftime('%Y-%m-%d')
                        })
                
            conn.close()
            return predictions[:3]  # أول 3 إنجازات قادمة
            
        except Exception as e:
            logger.error(f"❌ Achievement prediction failed: {e}")
            return []
    
    async def generate_personalized_recommendations(self, user_id):
        """إنشاء توصيات شخصية للمستخدمين"""
        try:
            conn = sqlite3.connect('bravebot.db')
            cursor = conn.cursor()
            
            # تحليل نشاط المستخدم
            cursor.execute("""
                SELECT total_checks, passed_checks, failed_checks,
                       datetime(last_check) as last_check
                FROM user_stats 
                WHERE user_id = ?
            """, (user_id,))
            
            stats = cursor.fetchone()
            if not stats:
                return []
            
            total, passed, failed, last_check = stats
            success_rate = (passed / max(total, 1)) * 100
            
            recommendations = []
            
            # توصيات بناءً على معدل النجاح
            if success_rate < 50:
                recommendations.append({
                    'type': 'improvement',
                    'message': 'جرب فحص منتجات بأسعار متوسطة لتحسين معدل نجاحك',
                    'action': 'compliance'
                })
            
            # توصيات بناءً على النشاط
            if last_check:
                last_check_date = datetime.fromisoformat(last_check)
                days_since = (datetime.now() - last_check_date).days
                
                if days_since > 7:
                    recommendations.append({
                        'type': 'engagement',
                        'message': 'لم نرك منذ فترة! عُد وتابع تقدمك في الإنجازات',
                        'action': 'stats'
                    })
            
            # توصيات الإنجازات
            achievements_predictions = await self.predict_user_achievements(user_id)
            if achievements_predictions:
                next_achievement = achievements_predictions[0]
                recommendations.append({
                    'type': 'achievement',
                    'message': f'أنت قريب من إنجاز {next_achievement["milestone"]} فحص! باقي {next_achievement["days_remaining"]} يوم فقط',
                    'action': 'achievements'
                })
            
            conn.close()
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Recommendations failed: {e}")
            return []

def main():
    """تشغيل نظام التحسينات"""
    enhancer = BraveBotEnhancer()
    
    async def run_enhancement_cycle():
        logger.info("🚀 Starting enhancement cycle...")
        
        # فحص التحديثات
        await enhancer.check_for_updates()
        
        # تحليل أنماط المستخدمين
        await enhancer.analyze_user_patterns()
        
        # إرسال التقارير الأسبوعية (إذا كان اليوم مناسب)
        if datetime.now().strftime('%A').lower() == enhancer.config['weekly_achievements']['send_day']:
            await enhancer.send_weekly_achievements_report()
        
        logger.info("✅ Enhancement cycle completed")
    
    try:
        asyncio.run(run_enhancement_cycle())
    except Exception as e:
        logger.error(f"❌ Enhancement cycle failed: {e}")

if __name__ == "__main__":
    main()
