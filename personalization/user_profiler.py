#!/usr/bin/env python3
"""
👤 User Personalization System
=============================
نظام التخصيص الشخصي وتحليل اهتمامات المستخدمين
"""

import json
import sqlite3
from datetime import datetime, timedelta
from collections import Counter
from pathlib import Path
import logging

# إعداد اللوغ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserProfiler:
    """محلل الملف الشخصي للمستخدم"""
    
    def __init__(self, db_path: str = "data/users.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """تهيئة قاعدة البيانات"""
        Path(self.db_path).parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    name TEXT,
                    interests TEXT,  -- JSON array
                    preferences TEXT,  -- JSON object
                    activity_history TEXT,  -- JSON array
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    action_type TEXT,  -- search, click, view, etc.
                    content TEXT,  -- keyword, product, trend
                    category TEXT,
                    metadata TEXT,  -- JSON with additional info
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
                )
            """)
    
    def create_user_profile(self, user_id: str, name: str = "", initial_interests: list = None):
        """إنشاء ملف شخصي جديد"""
        
        interests = initial_interests or []
        preferences = {
            'notification_frequency': 'daily',
            'preferred_categories': interests,
            'price_alert_threshold': 20,
            'viral_score_threshold': 80,
            'report_format': 'detailed'
        }
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO user_profiles 
                (user_id, name, interests, preferences, activity_history, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                name,
                json.dumps(interests),
                json.dumps(preferences),
                json.dumps([]),
                datetime.now()
            ))
        
        logger.info(f"تم إنشاء ملف شخصي للمستخدم: {user_id}")
    
    def track_user_interaction(self, user_id: str, action_type: str, content: str, 
                              category: str = "", metadata: dict = None):
        """تتبع تفاعل المستخدم"""
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO user_interactions 
                (user_id, action_type, content, category, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                user_id,
                action_type,
                content,
                category,
                json.dumps(metadata or {})
            ))
        
        # تحديث الملف الشخصي
        self._update_user_interests(user_id, content, category)
    
    def _update_user_interests(self, user_id: str, content: str, category: str):
        """تحديث اهتمامات المستخدم تلقائياً"""
        
        with sqlite3.connect(self.db_path) as conn:
            # جلب الاهتمامات الحالية
            cursor = conn.execute(
                "SELECT interests FROM user_profiles WHERE user_id = ?",
                (user_id,)
            )
            result = cursor.fetchone()
            
            if result:
                current_interests = json.loads(result[0] or '[]')
                
                # إضافة الفئة للاهتمامات
                if category and category not in current_interests:
                    current_interests.append(category)
                
                # تحديث قاعدة البيانات
                conn.execute("""
                    UPDATE user_profiles 
                    SET interests = ?, updated_at = ?
                    WHERE user_id = ?
                """, (
                    json.dumps(current_interests),
                    datetime.now(),
                    user_id
                ))
    
    def get_user_profile(self, user_id: str) -> dict:
        """جلب الملف الشخصي للمستخدم"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT name, interests, preferences, activity_history, created_at, updated_at
                FROM user_profiles WHERE user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            
            if result:
                return {
                    'user_id': user_id,
                    'name': result[0],
                    'interests': json.loads(result[1] or '[]'),
                    'preferences': json.loads(result[2] or '{}'),
                    'activity_history': json.loads(result[3] or '[]'),
                    'created_at': result[4],
                    'updated_at': result[5]
                }
            
            return {}
    
    def get_personalized_recommendations(self, user_id: str, trends_data: list) -> dict:
        """الحصول على توصيات شخصية"""
        
        profile = self.get_user_profile(user_id)
        
        if not profile:
            return self._get_default_recommendations(trends_data)
        
        user_interests = profile.get('interests', [])
        preferences = profile.get('preferences', {})
        
        # تحليل التفاعلات الحديثة
        recent_interactions = self._get_recent_interactions(user_id, days=7)
        
        # فلترة الترندات حسب الاهتمامات
        relevant_trends = []
        for trend in trends_data:
            trend_category = trend.get('category', '').lower()
            trend_keywords = trend.get('keyword', '').lower()
            
            # حساب نقاط الصلة
            relevance_score = 0
            
            # مطابقة الفئات
            if trend_category in [interest.lower() for interest in user_interests]:
                relevance_score += 50
            
            # مطابقة الكلمات المفتاحية من التفاعلات السابقة
            for interaction in recent_interactions:
                if interaction['content'].lower() in trend_keywords:
                    relevance_score += 30
            
            # إضافة نقاط الانتشار
            relevance_score += trend.get('viral_score', 0) * 0.2
            
            if relevance_score > 20:  # حد أدنى للصلة
                trend['relevance_score'] = relevance_score
                relevant_trends.append(trend)
        
        # ترتيب حسب الصلة
        relevant_trends.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # إنشاء التوصيات
        recommendations = {
            'user_id': user_id,
            'personalized': True,
            'top_trends': relevant_trends[:5],
            'categories_of_interest': user_interests,
            'recommended_actions': self._generate_action_recommendations(profile, relevant_trends),
            'generated_at': datetime.now().isoformat()
        }
        
        return recommendations
    
    def _get_recent_interactions(self, user_id: str, days: int = 7) -> list:
        """جلب التفاعلات الحديثة"""
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT action_type, content, category, metadata, timestamp
                FROM user_interactions 
                WHERE user_id = ? AND timestamp > ?
                ORDER BY timestamp DESC
            """, (user_id, cutoff_date))
            
            interactions = []
            for row in cursor.fetchall():
                interactions.append({
                    'action_type': row[0],
                    'content': row[1],
                    'category': row[2],
                    'metadata': json.loads(row[3] or '{}'),
                    'timestamp': row[4]
                })
            
            return interactions
    
    def _generate_action_recommendations(self, profile: dict, trends: list) -> list:
        """توليد توصيات الإجراءات"""
        
        actions = []
        
        for trend in trends[:3]:  # أفضل 3 ترندات
            viral_score = trend.get('viral_score', 0)
            
            if viral_score >= 80:
                actions.append({
                    'type': 'immediate_action',
                    'trend': trend['keyword'],
                    'recommendation': 'استغل هذا الترند فوراً - انتشار قوي جداً!',
                    'priority': 'high'
                })
            elif viral_score >= 60:
                actions.append({
                    'type': 'monitor',
                    'trend': trend['keyword'],
                    'recommendation': 'راقب هذا الترند - يبدو واعداً',
                    'priority': 'medium'
                })
        
        return actions
    
    def _get_default_recommendations(self, trends_data: list) -> dict:
        """توصيات افتراضية للمستخدمين الجدد"""
        
        # ترتيب حسب نقاط الانتشار
        sorted_trends = sorted(trends_data, key=lambda x: x.get('viral_score', 0), reverse=True)
        
        return {
            'personalized': False,
            'top_trends': sorted_trends[:5],
            'categories_of_interest': ['technology', 'general'],
            'recommended_actions': [
                {'type': 'explore', 'recommendation': 'استكشف الترندات المختلفة لبناء ملفك الشخصي'}
            ],
            'generated_at': datetime.now().isoformat()
        }
    
    def get_user_analytics(self, user_id: str) -> dict:
        """تحليلات المستخدم"""
        
        with sqlite3.connect(self.db_path) as conn:
            # إحصائيات التفاعل
            cursor = conn.execute("""
                SELECT action_type, COUNT(*) as count
                FROM user_interactions 
                WHERE user_id = ?
                GROUP BY action_type
            """, (user_id,))
            
            interaction_stats = dict(cursor.fetchall())
            
            # أكثر الفئات تفاعلاً
            cursor = conn.execute("""
                SELECT category, COUNT(*) as count
                FROM user_interactions 
                WHERE user_id = ? AND category != ''
                GROUP BY category
                ORDER BY count DESC
                LIMIT 5
            """, (user_id,))
            
            top_categories = dict(cursor.fetchall())
            
            # التفاعل الأسبوعي
            cursor = conn.execute("""
                SELECT DATE(timestamp) as date, COUNT(*) as count
                FROM user_interactions 
                WHERE user_id = ? AND timestamp > date('now', '-7 days')
                GROUP BY DATE(timestamp)
                ORDER BY date
            """, (user_id,))
            
            weekly_activity = dict(cursor.fetchall())
        
        return {
            'user_id': user_id,
            'interaction_stats': interaction_stats,
            'top_categories': top_categories,
            'weekly_activity': weekly_activity,
            'total_interactions': sum(interaction_stats.values()),
            'generated_at': datetime.now().isoformat()
        }

# إنشاء instance عالمي
user_profiler = UserProfiler()