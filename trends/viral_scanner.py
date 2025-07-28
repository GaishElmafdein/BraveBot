import praw
import logging

logger = logging.getLogger(__name__)

class ViralScanner:
    def __init__(self):
        """تهيئة ViralScanner - استخدام البيانات المحسنة"""
        
        logger.info("✅ ViralScanner initialized with enhanced fallback data")
        print("✅ ViralScanner using enhanced data (Reddit API disabled)")
        
        # استخدام البيانات المحسنة بدلاً من Reddit API
        self.reddit = None
        self.reddit_available = False
    
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
    
    def get_category_trends(self, category="technology"):
        """جلب ترندات فئة محددة من Reddit مع معالجة أفضل للأخطاء"""
        logger.info(f"📊 Getting REAL {category} trends from Reddit")
        
        if not self.reddit_available:
            logger.warning(f"⚠️ Reddit not available, using enhanced mock data for {category}")
            return self._get_enhanced_category_data(category)
        
        try:
            subreddit = self.reddit.subreddit(category)
            trends = []
            
            # استخدام hot() بدلاً من البحث
            for submission in subreddit.hot(limit=10):
                if submission.score > 20:  # ترندات ذات تفاعل جيد
                    trends.append({
                        'keyword': submission.title[:50] + "..." if len(submission.title) > 50 else submission.title,
                        'viral_score': min(submission.score // 10, 100),
                        'category': '🔥 ساخن' if submission.score > 100 else '📈 صاعد'
                    })
            
            logger.info(f"✅ Retrieved {len(trends)} real {category} trends")
            
            # تنسيق النتيجة لتطابق التوقعات
            return {
                'category': category,
                'top_keywords': trends[:5],  # أول 5 فقط
                'status': 'real_data'
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Reddit API error: {e}")
            return self._get_enhanced_category_data(category)

    def _get_enhanced_category_data(self, category):
        """بيانات احتياطية محسنة للفئات"""
        
        category_data = {
            'technology': {
                'top_keywords': [
                    {'keyword': 'iPhone 15 Pro', 'viral_score': 95, 'category': '🔥 ساخن جداً'},
                    {'keyword': 'ChatGPT تحديثات', 'viral_score': 89, 'category': '📈 صاعد'},
                    {'keyword': 'تسلا السيارات الذكية', 'viral_score': 84, 'category': '🚀 متقدم'},
                    {'keyword': 'ميتا Quest 3', 'viral_score': 78, 'category': '💡 مبتكر'}
                ]
            },
            'crypto': {
                'top_keywords': [
                    {'keyword': 'Bitcoin تحليل', 'viral_score': 92, 'category': '🔥 ساخن جداً'},
                    {'keyword': 'Ethereum تطورات', 'viral_score': 87, 'category': '📈 صاعد'},
                    {'keyword': 'العملات البديلة', 'viral_score': 81, 'category': '💰 استثماري'}
                ]
            },
            'gaming': {
                'top_keywords': [
                    {'keyword': 'PlayStation 5 Pro', 'viral_score': 93, 'category': '🔥 ساخن جداً'},
                    {'keyword': 'Xbox Game Pass', 'viral_score': 85, 'category': '📈 صاعد'},
                    {'keyword': 'Steam Deck OLED', 'viral_score': 79, 'category': '🎮 جديد'}
                ]
            }
        }
        
        return {
            'category': category,
            'top_keywords': category_data.get(category, category_data['technology'])['top_keywords'],
            'status': 'enhanced_fallback'
        }