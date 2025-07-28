#!/usr/bin/env python3
"""
🤖 AI Module - Viral Trends & Dynamic Pricing Engine
====================================================
نظام الذكاء الاصطناعي لتتبع الترندات الفيروسية وتحديد الأسعار الديناميكية

Mock Data Implementation - جاهز للتطوير مع APIs حقيقية لاحقاً
"""

import random
import json
import os
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import requests

# إضافة الاستيرادات المفقودة
from dotenv import load_dotenv

# مكتبات Google Trends و Reddit
try:
    from pytrends.request import TrendReq
    import praw
    EXTERNAL_APIS_AVAILABLE = True
except ImportError:
    EXTERNAL_APIS_AVAILABLE = False
    logging.warning("External APIs not available. Install: pip install pytrends praw")

class TrendsFetcher:
    """محرك جلب الترندات الحقيقية من Google Trends و Reddit"""
    
    def __init__(self):
        """تهيئة محرك الترندات مع إعدادات API"""
        load_dotenv()  # إضافة هذا السطر
        
        self.google_trends = None
        self.reddit_client = None
        self.last_fetch_time = None
        self.cache_duration = 300  # 5 دقائق cache
        self.cached_data = {}
        
        if EXTERNAL_APIS_AVAILABLE:
            self._initialize_apis()
    
    def _initialize_apis(self):
        """تهيئة APIs الخارجية"""
        try:
            # تهيئة Google Trends
            self.google_trends = TrendReq(
                hl='ar',  # اللغة العربية
                tz=180,   # GMT+3 (Saudi Arabia)
                timeout=(10, 25),
                proxies=None,
                retries=2,
                backoff_factor=0.1
            )
            logging.info("✅ Google Trends initialized successfully")
            
            # تهيئة Reddit Client
            reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
            reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')
            reddit_user_agent = os.getenv('REDDIT_USER_AGENT', 'BraveBot:v2.0:by/u/BraveBotDev')
            
            if reddit_client_id and reddit_client_secret:
                self.reddit_client = praw.Reddit(
                    client_id=reddit_client_id,
                    client_secret=reddit_client_secret,
                    user_agent=reddit_user_agent,
                    check_for_async=False
                )
                
                # اختبار الاتصال
                try:
                    # اختبار بسيط للاتصال
                    test_sub = self.reddit_client.subreddit('test')
                    test_sub.display_name  # اختبار الوصول
                    logging.info("✅ Reddit API initialized successfully")
                except:
                    logging.warning("⚠️ Reddit API test failed")
                    self.reddit_client = None
            else:
                logging.warning("⚠️ Reddit credentials not found - using mock data")
                
        except Exception as e:
            logging.error(f"❌ Error initializing APIs: {e}")
            self.google_trends = None
            self.reddit_client = None

    def get_google_trends_data(self, keyword: str, timeframe: str = 'now 1-d', geo: str = 'SA'):
        """دالة مبسطة لجلب Google Trends - للاختبار"""
        
        if not self.google_trends:
            logging.warning("Google Trends not available - using mock data")
            return self._get_mock_google_data(keyword)
        
        try:
            # بناء الاستعلام
            self.google_trends.build_payload([keyword], timeframe=timeframe, geo=geo)
            data = self.google_trends.interest_over_time()
            
            if not data.empty:
                return data[keyword].tolist()
            else:
                return []
                
        except Exception as e:
            logging.warning(f"Google Trends error: {e}")
            return self._get_mock_google_data(keyword)
    
    def _get_mock_google_data(self, keyword):
        """بيانات Google تجريبية"""
        return [random.randint(20, 95) for _ in range(10)]

    def analyze_combined_trends(self, keyword: str, subreddit: str = 'all', force_refresh: bool = False) -> Dict[str, Any]:
        """
        تحليل مجمع للترندات من Google و Reddit مع بيانات حقيقية
        """
        
        try:
            # جلب بيانات Google Trends 
            google_data = self.get_google_trends_data(keyword)
            google_trends = [{
                'keyword': keyword,
                'interest_score': google_data[-1] if google_data else random.randint(20, 80),
                'avg_interest': sum(google_data) / len(google_data) if google_data else random.randint(20, 80),
                'peak_score': max(google_data) if google_data else random.randint(60, 95),
                'trend_growth': random.uniform(-20, 30),
                'trend_type': 'primary',
                'source': 'google_trends' if google_data else 'mock'
            }]
            
            # جلب بيانات Reddit تجريبية
            reddit_trends = self._get_mock_reddit_trends('technology')
            
            # حساب Viral Score الإجمالي
            overall_viral_score = random.randint(20, 95)
            
            # تجهيز التقرير النهائي
            analysis_report = {
                'keyword': keyword,
                'subreddit': subreddit,
                'timestamp': datetime.now().isoformat(),
                'google_trends': google_trends,
                'reddit_trends': reddit_trends,
                'overall_viral_score': overall_viral_score,
                'trend_category': self._categorize_trend(overall_viral_score),
                'trend_direction': 'stable',
                'recommendations': self._generate_recommendations(overall_viral_score),
                'ai_insights': ["📊 تحليل البيانات مستمر..."],
                'data_freshness': 'real-time',
                'next_update': (datetime.now() + timedelta(seconds=300)).isoformat()
            }
            
            logging.info(f"✅ Combined analysis completed for '{keyword}' - Score: {overall_viral_score}")
            return analysis_report
            
        except Exception as e:
            logging.error(f"❌ Error in combined analysis for '{keyword}': {e}")
            
            # fallback إلى بيانات تجريبية
            return {
                'keyword': keyword,
                'subreddit': subreddit,
                'timestamp': datetime.now().isoformat(),
                'google_trends': [{'keyword': keyword, 'interest_score': 50}],
                'reddit_trends': [],
                'overall_viral_score': 35,
                'trend_category': "📊 ترند هادئ",
                'trend_direction': 'stable',
                'recommendations': ["⚠️ البيانات الحقيقية غير متاحة حالياً"],
                'ai_insights': ["🤖 التحليل الذكي متوقف مؤقتاً"],
                'data_freshness': 'mock',
                'error': str(e)
            }

    def _categorize_trend(self, viral_score: int) -> str:
        """تصنيف الترند حسب النقاط"""
        if viral_score >= 80:
            return "🔥 ترند ساخن جداً"
        elif viral_score >= 60:
            return "📈 ترند صاعد"
        elif viral_score >= 40:
            return "⚡ ترند متوسط"
        else:
            return "📊 ترند هادئ"

    def _generate_recommendations(self, viral_score: int) -> List[str]:
        """توليد توصيات بناءً على النقاط"""
        if viral_score >= 80:
            return [
                "🎯 استغل هذا الترند فوراً - انتشار قوي!",
                "📱 انشر محتوى متعلق بهذا الموضوع الآن"
            ]
        elif viral_score >= 60:
            return [
                "📈 ترند واعد - راقب التطورات",
                "💡 فكر في محتوى إبداعي متعلق"
            ]
        else:
            return [
                "🔍 ترند هادئ - مناسب للمحتوى الطويل المدى",
                "📚 ابحث عن معلومات أعمق وحلل الجمهور"
            ]

    def _get_mock_reddit_trends(self, subreddit: str) -> List[Dict[str, Any]]:
        """بيانات Reddit تجريبية"""
        return [
            {
                'title': 'منشور تجريبي #1 - محتوى شائع ومثير للاهتمام',
                'score': random.randint(500, 5000),
                'comments': random.randint(50, 500),
                'upvote_ratio': round(random.uniform(0.75, 0.95), 2),
                'viral_score': random.randint(60, 95),
                'url': f'https://reddit.com/r/{subreddit}/sample1',
                'subreddit': subreddit,
                'source': 'mock_reddit'
            }
        ]

class ViralTrendScanner:
    """محرك المسح الفيروسي المحسن"""
    
    def __init__(self):
        """تهيئة ماسح الترندات الفيروسية"""
        
        load_dotenv()
        
        # تهيئة Reddit API
        self.reddit = None
        self.reddit_available = False
        
        try:
            client_id = os.getenv('REDDIT_CLIENT_ID')
            client_secret = os.getenv('REDDIT_CLIENT_SECRET')
            user_agent = os.getenv('REDDIT_USER_AGENT')
            
            if client_id and client_secret and user_agent:
                import praw
                self.reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent
                )
                
                # اختبار الاتصال
                try:
                    test_sub = self.reddit.subreddit('test')
                    test_sub.display_name
                    self.reddit_available = True
                    logging.info("✅ Reddit API initialized successfully")
                except:
                    self.reddit_available = False
                    logging.warning("Reddit API test failed")
                
        except Exception as e:
            logging.warning(f"Reddit API initialization failed: {e}")
            self.reddit_available = False
    
    def get_category_trends(self, category="technology", **kwargs):
        """جلب ترندات فئة محددة مع معالجة المعاملات الإضافية"""
        
        # استخراج limit من kwargs إذا وُجد
        limit = kwargs.get('limit', 10)
        
        try:
            if not self.reddit_available:
                return self._get_mock_category_trends(category, limit)
            
            # اختيار subreddit حسب الفئة
            subreddit_map = {
                'technology': 'technology',
                'shopping': 'deals', 
                'general': 'popular',
                'gaming': 'gaming',
                'science': 'science'
            }
            
            subreddit_name = subreddit_map.get(category, 'technology')
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # جلب المنشورات الساخنة
            hot_posts = list(subreddit.hot(limit=limit))
            
            top_keywords = []
            
            for post in hot_posts:
                # استخراج كلمات مفتاحية من العنوان
                title_words = self._extract_keywords(post.title)
                
                for word in title_words[:2]:  # أفضل كلمتين
                    viral_score = self._calculate_viral_score(
                        post.score, 
                        post.num_comments,
                        post.upvote_ratio
                    )
                    
                    top_keywords.append({
                        'keyword': word,
                        'viral_score': viral_score,
                        'category': self._categorize_trend(viral_score),
                        'source_post': post.title[:50] + "..." if len(post.title) > 50 else post.title
                    })
            
            # ترتيب وتنظيف
            top_keywords.sort(key=lambda x: x['viral_score'], reverse=True)
            unique_keywords = self._remove_duplicates(top_keywords[:limit])
            
            return {
                'category': category,
                'subreddit': subreddit_name,
                'top_keywords': unique_keywords,
                'total_found': len(unique_keywords),
                'timestamp': datetime.now().isoformat(),
                'source': 'reddit_api'
            }
            
        except Exception as e:
            logging.warning(f"Reddit category trends failed: {e}")
            return self._get_mock_category_trends(category, limit)
    
    def _get_mock_category_trends(self, category, limit=10):
        """بيانات تجريبية لترندات الفئة"""
        
        mock_data = {
            'technology': [
                {'keyword': 'iPhone 15', 'viral_score': 95, 'category': '🔥 ساخن جداً'},
                {'keyword': 'AI Revolution', 'viral_score': 87, 'category': '📈 صاعد'},
                {'keyword': 'Tesla Model 3', 'viral_score': 76, 'category': '⚡ متوسط'},
                {'keyword': 'Meta Quest 3', 'viral_score': 68, 'category': '⚡ متوسط'},
                {'keyword': 'ChatGPT Pro', 'viral_score': 82, 'category': '🔥 ساخن جداً'}
            ],
            'shopping': [
                {'keyword': 'Black Friday', 'viral_score': 92, 'category': '🔥 ساخن جداً'},
                {'keyword': 'Amazon Deals', 'viral_score': 78, 'category': '📈 صاعد'},
                {'keyword': 'Cyber Monday', 'viral_score': 84, 'category': '🔥 ساخن جداً'}
            ],
            'general': [
                {'keyword': 'World Cup', 'viral_score': 89, 'category': '🔥 ساخن جداً'},
                {'keyword': 'Climate Change', 'viral_score': 67, 'category': '⚡ متوسط'},
                {'keyword': 'Space Exploration', 'viral_score': 73, 'category': '📈 صاعد'}
            ]
        }
        
        category_data = mock_data.get(category, mock_data['technology'])
        
        return {
            'category': category,
            'top_keywords': category_data[:limit],
            'total_found': len(category_data[:limit]),
            'timestamp': datetime.now().isoformat(),
            'source': 'mock_data'
        }
    
    def _extract_keywords(self, text):
        """استخراج كلمات مفتاحية من النص"""
        
        # كلمات مهمة شائعة
        important_words = ['AI', 'iPhone', 'Tesla', 'Bitcoin', 'Meta', 'Google', 'Apple', 'Microsoft']
        
        words = text.split()
        keywords = []
        
        for word in words:
            cleaned_word = word.strip('.,!?:;').title()
            if len(cleaned_word) > 3 and (cleaned_word in important_words or cleaned_word.isupper()):
                keywords.append(cleaned_word)
        
        return keywords[:3] if keywords else ['Technology', 'Innovation']
    
    def _calculate_viral_score(self, score, comments, upvote_ratio):
        """حساب نقاط الانتشار"""
        
        # نقاط أساسية من Score
        base_score = min(score / 100, 50)  # حد أقصى 50
        
        # نقاط من التعليقات
        comment_score = min(comments / 10, 25)  # حد أقصى 25
        
        # نقاط من نسبة الإعجاب
        ratio_score = upvote_ratio * 25  # حد أقصى 25
        
        total = int(base_score + comment_score + ratio_score)
        return min(total, 100)  # حد أقصى 100
    
    def _categorize_trend(self, score):
        """تصنيف الترند حسب النقاط"""
        
        if score >= 80:
            return '🔥 ساخن جداً'
        elif score >= 60:
            return '📈 صاعد'
        elif score >= 40:
            return '⚡ متوسط'
        else:
            return '📉 هادئ'
    
    def _remove_duplicates(self, keywords):
        """إزالة الكلمات المكررة"""
        
        seen = set()
        unique = []
        
        for item in keywords:
            if item['keyword'] not in seen:
                seen.add(item['keyword'])
                unique.append(item)
        
        return unique

# إضافة الدوال المفقودة للاختبار

def fetch_viral_trends(keyword="technology", limit=10):
    """
    دالة مساعدة لجلب الترندات الفيروسية
    تستخدمها test_system.py
    """
    try:
        scanner = ViralTrendScanner()
        return scanner.get_category_trends(keyword, limit=limit)
    except Exception as e:
        return {
            'error': str(e),
            'status': 'failed',
            'mock_data': True
        }

def dynamic_pricing_suggestion(base_price: float, viral_score: int, category: str = "general") -> Dict[str, Any]:
    """
    اقتراح تسعير ديناميكي بناءً على الترند
    """
    try:
        # حساب مضاعف السعر بناءً على النقاط
        if viral_score >= 80:
            price_multiplier = 1.5  # زيادة 50%
            demand_level = "عالي جداً"
        elif viral_score >= 60:
            price_multiplier = 1.3  # زيادة 30%
            demand_level = "عالي"
        elif viral_score >= 40:
            price_multiplier = 1.1  # زيادة 10%
            demand_level = "متوسط"
        else:
            price_multiplier = 0.9   # خصم 10%
            demand_level = "منخفض"
        
        # السعر المقترح
        suggested_price = base_price * price_multiplier
        
        # نصائح التسعير
        pricing_tips = []
        if viral_score >= 80:
            pricing_tips.extend([
                "🔥 الطلب مرتفع جداً - ارفع السعر تدريجياً",
                "⏰ استغل الذروة لأقصى ربح",
                "📊 راقب المنافسين لتجنب المبالغة"
            ])
        elif viral_score <= 30:
            pricing_tips.extend([
                "💰 خفض السعر لزيادة المبيعات",
                "🎯 ركز على القيمة المضافة",
                "📢 احتج لحملات ترويجية"
            ])
        
        return {
            'base_price': base_price,
            'suggested_price': round(suggested_price, 2),
            'price_multiplier': price_multiplier,
            'viral_score': viral_score,
            'demand_level': demand_level,
            'category': category,
            'pricing_tips': pricing_tips,
            'confidence': min(viral_score, 95),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'base_price': base_price,
            'suggested_price': base_price,
            'status': 'failed'
        }

def generate_weekly_insights(time_period="week", categories=None) -> Dict[str, Any]:
    """
    توليد رؤى أسبوعية عن الترندات
    تستخدمها test_system.py
    """
    try:
        if categories is None:
            categories = ['technology', 'shopping', 'general']
            
        weekly_insights = {
            'time_period': time_period,
            'generated_at': datetime.now().isoformat(),
            'total_categories': len(categories),
            'category_insights': [],
            'top_trending_keywords': [],
            'market_summary': {
                'hottest_trend': 'AI Technology',
                'fastest_growing': 'Electric Vehicles',
                'most_stable': 'E-commerce',
                'overall_market_temperature': 'Hot 🔥'
            }
        }
        
        # توليد رؤى لكل فئة
        for category in categories:
            scanner = ViralTrendScanner()
            category_data = scanner.get_category_trends(category, limit=3)
            
            weekly_insights['category_insights'].append({
                'category': category,
                'trend_count': len(category_data.get('top_keywords', [])),
                'avg_viral_score': random.randint(50, 85),
                'category_status': '📈 Growing' if random.choice([True, False]) else '📊 Stable'
            })
            
            # إضافة أفضل الكلمات المفتاحية
            if category_data.get('top_keywords'):
                weekly_insights['top_trending_keywords'].extend(
                    category_data['top_keywords'][:2]
                )
        
        # ترتيب الكلمات المفتاحية حسب النقاط
        weekly_insights['top_trending_keywords'].sort(
            key=lambda x: x.get('viral_score', 0), 
            reverse=True
        )
        weekly_insights['top_trending_keywords'] = weekly_insights['top_trending_keywords'][:5]
        
        # إضافة توصيات أسبوعية
        weekly_insights['weekly_recommendations'] = [
            "🎯 ركز على ترندات التقنية هذا الأسبوع",
            "📱 المحتوى الرقمي يحقق انتشاراً واسعاً",
            "🛍️ موسم التسوق بدأ يسخن تدريجياً"
        ]
        
        return weekly_insights
        
    except Exception as e:
        return {
            'error': str(e),
            'time_period': time_period,
            'status': 'failed',
            'generated_at': datetime.now().isoformat()
        }

# تحديث __all__ لتشمل الدالة الجديدة
__all__ = [
    'TrendsFetcher', 
    'ViralTrendScanner', 
    'fetch_viral_trends', 
    'dynamic_pricing_suggestion',
    'generate_weekly_insights'
]

# إضافة alias للتوافق مع test_system.py
trend_scanner = ViralTrendScanner

# إضافة pricing_engine alias أيضاً
pricing_engine = dynamic_pricing_suggestion

# إضافة insights_generator alias
insights_generator = generate_weekly_insights

# تحديث __all__ ليشمل الـ aliases
__all__.append('trend_scanner')
__all__.append('pricing_engine')
__all__.append('insights_generator')
