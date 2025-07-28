import praw
import logging

logger = logging.getLogger(__name__)

class ViralScanner:
    def __init__(self):
        # إعدادات Reddit API الحقيقية
        self.reddit = None
        self.mock_enabled = False  # ❌ إيقاف المحاكاة
        logger.info("🔥 ViralScanner initialized - REAL REDDIT DATA ONLY")
        
        # محاولة الاتصال بـ Reddit
        self._init_reddit_connection()
    
    def _init_reddit_connection(self):
        """تهيئة اتصال Reddit الحقيقي"""
        
        try:
            # استخدام Reddit بدون مصادقة (read-only)
            self.reddit = praw.Reddit(
                client_id="temp",  # يمكن استخدام قيم مؤقتة
                client_secret="temp",
                user_agent="BraveBot:1.0 (by /u/temp)"
            )
            
            # اختبار الاتصال
            self.reddit.subreddit("python").hot(limit=1)
            logger.info("✅ Reddit connection established")
            
        except Exception as e:
            logger.error(f"❌ Reddit connection failed: {e}")
            self.reddit = None
    
    def scan_reddit_trends(self, keyword, limit=5):
        """مسح Reddit للترندات الحقيقية فقط"""
        
        logger.info(f"🗨️ Scanning REAL Reddit trends for: {keyword}")
        
        if not self.reddit:
            logger.error("❌ Reddit not available - no mock data provided")
            return []
        
        try:
            trends = []
            
            # البحث في عدة subreddits
            subreddits = ['all', 'technology', 'trending', 'popular']
            
            for subreddit_name in subreddits:
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    
                    # البحث في المشاركات الساخنة
                    for submission in subreddit.search(keyword, limit=limit//len(subreddits) + 1, sort='hot', time_filter='day'):
                        if len(trends) >= limit:
                            break
                            
                        if submission.score > 10:  # فلترة المشاركات منخفضة التفاعل
                            trends.append({
                                'title': submission.title,
                                'score': submission.score,
                                'num_comments': submission.num_comments,
                                'url': submission.url,
                                'subreddit': str(submission.subreddit),
                                'created_utc': submission.created_utc
                            })
                
                except Exception as e:
                    logger.warning(f"⚠️ Failed to search subreddit {subreddit_name}: {e}")
                    continue
            
            # ترتيب حسب النقاط
            trends.sort(key=lambda x: x['score'], reverse=True)
            
            logger.info(f"✅ Found {len(trends)} real Reddit trends")
            return trends[:limit]
            
        except Exception as e:
            logger.error(f"❌ Reddit scan failed: {e}")
            return []
    
    def get_category_trends(self, category='technology'):
        """جلب ترندات فئة معينة من Reddit"""
        
        logger.info(f"📊 Getting REAL {category} trends from Reddit")
        
        if not self.reddit:
            logger.error(f"❌ Reddit not available for {category} trends")
            return []
        
        try:
            subreddit = self.reddit.subreddit(category)
            trends = []
            
            for submission in subreddit.hot(limit=10):
                if submission.score > 50:  # ترندات ذات تفاعل جيد
                    trends.append({
                        'title': submission.title,
                        'score': submission.score,
                        'comments': submission.num_comments,
                        'viral_score': min(submission.score // 10, 100)
                    })
            
            logger.info(f"✅ Retrieved {len(trends)} real {category} trends")
            return trends
            
        except Exception as e:
            logger.error(f"❌ Category trends failed for {category}: {e}")
            return []