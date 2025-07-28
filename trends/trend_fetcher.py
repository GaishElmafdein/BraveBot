# في بداية الملف أضف:

import logging
logger = logging.getLogger(__name__)

class TrendsFetcher:
    def __init__(self):
        # إزالة أي mock data
        self.mock_enabled = False  # ❌ إيقاف المحاكاة نماماً
        logger.info("🔥 TrendsFetcher initialized - REAL DATA ONLY")
    
    def get_trending_keywords(self, keyword, timeframe='today 3-m'):
        """جلب البيانات الحقيقية فقط"""
        
        logger.info(f"📡 Fetching REAL Google Trends for: {keyword}")
        
        try:
            # محاولة Google Trends الحقيقي
            from pytrends.request import TrendReq
            
            pytrends = TrendReq(hl='en-US', tz=360)
            pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo='', gprop='')
            
            # جلب البيانات
            interest_over_time = pytrends.interest_over_time()
            related_queries = pytrends.related_queries()
            
            if interest_over_time.empty:
                logger.warning(f"⚠️ No Google Trends data for: {keyword}")
                return []
            
            # تحويل البيانات
            trends_data = []
            
            # بيانات الاهتمام عبر الوقت
            if not interest_over_time.empty:
                latest_interest = interest_over_time[keyword].iloc[-1]
                trends_data.append({
                    'keyword': keyword,
                    'interest_score': int(latest_interest),
                    'trend_type': 'primary'
                })
            
            # الاستعلامات ذات الصلة
            if related_queries[keyword]['rising'] is not None:
                rising_queries = related_queries[keyword]['rising'].head(3)
                for _, row in rising_queries.iterrows():
                    trends_data.append({
                        'keyword': row['query'],
                        'interest_score': int(row['value']) if row['value'] != '<1' else 1,
                        'trend_type': 'related'
                    })
            
            logger.info(f"✅ Retrieved {len(trends_data)} real Google trends")
            return trends_data
            
        except ImportError:
            logger.error("❌ pytrends not installed - install with: pip install pytrends")
            return []
        except Exception as e:
            logger.error(f"❌ Google Trends API failed: {e}")
            return []
    
    def analyze_combined_trends(self, keyword):
        """تحليل شامل - بيانات حقيقية فقط"""
        
        logger.info(f"🔍 Analyzing REAL trends for: {keyword}")
        
        try:
            google_trends = self.get_trending_keywords(keyword)
            
            if not google_trends:
                logger.warning(f"⚠️ No real data found for: {keyword}")
                return None
            
            # حساب النقاط الحقيقية
            total_interest = sum(t['interest_score'] for t in google_trends)
            viral_score = min(total_interest, 100)  # حد أقصى 100
            
            return {
                'keyword': keyword,
                'overall_viral_score': viral_score,
                'google_trends': google_trends,
                'reddit_trends': [],  # سيتم ملؤها من ViralScanner
                'recommendations': self._generate_real_recommendations(viral_score)
            }
            
        except Exception as e:
            logger.error(f"❌ Combined analysis failed: {e}")
            return None
    
    def _generate_real_recommendations(self, viral_score):
        """توصيات حقيقية حسب النقاط"""
        
        if viral_score >= 70:
            return [
                "🔥 ترند ساخن - استغل الفرصة فوراً",
                "📱 انشر محتوى متعلق بهذا الموضوع الآن",
                "💰 فكر في استثمار تسويقي سريع"
            ]
        elif viral_score >= 40:
            return [
                "📈 ترند صاعد - راقب التطورات",
                "💡 خطط لمحتوى إبداعي متعلق",
                "⏰ استراتيجية متوسطة المدى مناسبة"
            ]
        else:
            return [
                "📊 اهتمام محدود حالياً",
                "🔍 ابحث عن زوايا جديدة",
                "📚 مناسب للمحتوى طويل المدى"
            ]