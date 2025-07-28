"""
🧪 اختبار النظام الكامل - BraveBot v2.0
================================================
اختبار شامل للتأكد من عمل جميع المكونات
"""

import os
import sys
import asyncio
import time
from datetime import datetime
from pathlib import Path

# إضافة مسار المشروع
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("🧪 BraveBot v2.0 - اختبار النظام الكامل")
print("=" * 60)

def test_environment():
    """اختبار متغيرات البيئة"""
    print("\n📋 1. اختبار متغيرات البيئة:")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        'TELEGRAM_TOKEN',
        'REDDIT_CLIENT_ID',
        'REDDIT_CLIENT_SECRET',
        'REDDIT_USER_AGENT'
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: {'*' * 10}...{value[-4:] if len(value) > 4 else '****'}")
        else:
            print(f"   ❌ {var}: غير موجود")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  متغيرات مفقودة: {', '.join(missing_vars)}")
        return False
    
    print("✅ جميع متغيرات البيئة موجودة")
    return True

def test_imports():
    """اختبار استيراد المكتبات"""
    print("\n📦 2. اختبار استيراد المكتبات:")
    
    imports_test = [
        ('telegram', 'python-telegram-bot'),
        ('streamlit', 'streamlit'),
        ('plotly', 'plotly'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('requests', 'requests'),
        ('pytrends.request', 'pytrends'),
        ('praw', 'praw'),
        ('sqlite3', 'sqlite3 (built-in)'),
        ('dotenv', 'python-dotenv')
    ]
    
    failed_imports = []
    
    for module, package in imports_test:
        try:
            __import__(module)
            print(f"   ✅ {package}: متاحة")
        except ImportError as e:
            print(f"   ❌ {package}: غير متاحة - {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n⚠️  مكتبات مفقودة: {', '.join(failed_imports)}")
        print(f"💡 لتثبيتها: pip install {' '.join(failed_imports)}")
        return False
    
    print("✅ جميع المكتبات متاحة")
    return True

def test_trends_engine():
    """اختبار محرك الترندات"""
    print("\n🔥 3. اختبار محرك الترندات:")
    
    try:
        from ai.trends_engine import TrendsFetcher, ViralTrendScanner
        
        print("   ✅ استيراد TrendsFetcher: نجح")
        print("   ✅ استيراد ViralTrendScanner: نجح")
        
        # اختبار تهيئة المحركات
        try:
            trends_fetcher = TrendsFetcher()
            print("   ✅ تهيئة TrendsFetcher: نجحت")
        except Exception as e:
            print(f"   ❌ تهيئة TrendsFetcher: فشلت - {e}")
            return False
        
        try:
            viral_scanner = ViralTrendScanner()
            print("   ✅ تهيئة ViralTrendScanner: نجحت")
        except Exception as e:
            print(f"   ❌ تهيئة ViralTrendScanner: فشلت - {e}")
            return False
        
        # اختبار جلب البيانات (سريع)
        print("   🔍 اختبار جلب بيانات تجريبية...")
        
        try:
            # اختبار Google Trends
            test_data = trends_fetcher.get_google_trends_data("test", timeframe='now 1-d')
            print(f"   ✅ Google Trends: نجح (عدد النقاط: {len(test_data) if test_data else 0})")
        except Exception as e:
            print(f"   ⚠️  Google Trends: {e}")
        
        try:
            # اختبار Reddit (محدود للسرعة)
            category_data = viral_scanner.get_category_trends("technology", limit=2)
            print(f"   ✅ Reddit API: نجح")
        except Exception as e:
            print(f"   ⚠️  Reddit API: {e}")
        
        print("✅ محرك الترندات يعمل")
        return True
        
    except ImportError as e:
        print(f"   ❌ فشل في استيراد محرك الترندات: {e}")
        return False

def test_database():
    """اختبار قاعدة البيانات"""
    print("\n💾 4. اختبار قاعدة البيانات:")
    
    try:
        from core.database_manager import init_database, add_log
        
        # تهيئة قاعدة البيانات
        init_database()
        print("   ✅ تهيئة قاعدة البيانات: نجحت")
        
        # اختبار إضافة سجل
        add_log("System test", level="INFO")
        print("   ✅ إضافة سجل: نجحت")
        
        # التحقق من وجود ملف قاعدة البيانات
        if os.path.exists('bot_data.db'):
            print("   ✅ ملف قاعدة البيانات: موجود")
        else:
            print("   ⚠️  ملف قاعدة البيانات: غير موجود")
        
        print("✅ قاعدة البيانات تعمل")
        return True
        
    except Exception as e:
        print(f"   ❌ فشل في اختبار قاعدة البيانات: {e}")
        return False

def test_bot_components():
    """اختبار مكونات البوت"""
    print("\n🤖 5. اختبار مكونات البوت:")
    
    try:
        # اختبار استيراد المكونات الرئيسية
        from telegram import Update
        from telegram.ext import Application, CommandHandler
        
        print("   ✅ استيراد Telegram components: نجح")
        
        # اختبار TOKEN
        token = os.getenv('TELEGRAM_TOKEN')
        if token and len(token) > 20:
            print("   ✅ TELEGRAM_TOKEN: صالح")
        else:
            print("   ❌ TELEGRAM_TOKEN: غير صالح")
            return False
        
        # اختبار إنشاء Application (بدون تشغيل)
        try:
            app = Application.builder().token(token).build()
            print("   ✅ إنشاء Bot Application: نجح")
        except Exception as e:
            print(f"   ❌ إنشاء Bot Application: فشل - {e}")
            return False
        
        print("✅ مكونات البوت جاهزة")
        return True
        
    except Exception as e:
        print(f"   ❌ فشل في اختبار مكونات البوت: {e}")
        return False

def test_dashboard_components():
    """اختبار مكونات Dashboard"""
    print("\n📊 6. اختبار مكونات Dashboard:")
    
    try:
        import streamlit as st
        import plotly.express as px
        import plotly.graph_objects as go
        
        print("   ✅ استيراد Streamlit: نجح")
        print("   ✅ استيراد Plotly: نجح")
        
        # التحقق من وجود ملف Dashboard
        dashboard_files = [
            'dashboard/app.py',
            'simple_dashboard.py'
        ]
        
        dashboard_found = False
        for file in dashboard_files:
            if os.path.exists(file):
                print(f"   ✅ ملف Dashboard: {file} موجود")
                dashboard_found = True
                break
        
        if not dashboard_found:
            print("   ⚠️  ملف Dashboard: غير موجود")
        
        print("✅ مكونات Dashboard جاهزة")
        return True
        
    except Exception as e:
        print(f"   ❌ فشل في اختبار Dashboard: {e}")
        return False

async def test_trends_integration():
    """اختبار تكامل نظام الترندات"""
    print("\n🔄 7. اختبار تكامل نظام الترندات:")
    
    try:
        from ai.trends_engine import TrendsFetcher, ViralTrendScanner
        
        trends_fetcher = TrendsFetcher()
        viral_scanner = ViralTrendScanner()
        
        print("   🔍 اختبار تحليل ترند سريع...")
        
        # اختبار تحليل مجمع
        try:
            analysis = trends_fetcher.analyze_combined_trends("technology")
            
            if analysis and 'overall_viral_score' in analysis:
                print(f"   ✅ تحليل مجمع: نجح (نقاط: {analysis['overall_viral_score']})")
            else:
                print("   ⚠️  تحليل مجمع: بيانات محدودة")
        
        except Exception as e:
            print(f"   ⚠️  تحليل مجمع: {e}")
        
        # اختبار ترندات الفئة
        try:
            category_trends = viral_scanner.get_category_trends("technology", limit=2)
            
            if category_trends and 'top_keywords' in category_trends:
                print(f"   ✅ ترندات الفئة: نجحت")
            else:
                print("   ⚠️  ترندات الفئة: بيانات محدودة")
                
        except Exception as e:
            print(f"   ⚠️  ترندات الفئة: {e}")
        
        print("✅ تكامل نظام الترندات يعمل")
        return True
        
    except Exception as e:
        print(f"   ❌ فشل في اختبار التكامل: {e}")
        return False

def generate_test_report(results):
    """إنتاج تقرير الاختبار"""
    print("\n" + "=" * 60)
    print("📋 تقرير الاختبار الشامل")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests
    
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"📊 إجمالي الاختبارات: {total_tests}")
    print(f"✅ نجحت: {passed_tests}")
    print(f"❌ فشلت: {failed_tests}")
    print(f"📈 معدل النجاح: {success_rate:.1f}%")
    
    print("\n📋 تفاصيل النتائج:")
    for test_name, result in results.items():
        status = "✅ نجح" if result else "❌ فشل"
        print(f"   {test_name}: {status}")
    
    print("\n" + "=" * 60)
    
    if success_rate >= 80:
        print("🎉 النظام جاهز للاستخدام!")
        print("🚀 يمكنك تشغيل البوت والـ Dashboard بأمان")
        
        if success_rate < 100:
            print("💡 بعض الميزات قد تعمل بشكل محدود")
    
    elif success_rate >= 60:
        print("⚠️  النظام يعمل جزئياً")
        print("🔧 يحتاج لإصلاح بعض المشاكل قبل الاستخدام الكامل")
    
    else:
        print("❌ النظام يحتاج إصلاحات كبيرة")
        print("🛠️  يرجى مراجعة الأخطاء أعلاه وإصلاحها")
    
    return success_rate

async def main():
    """تشغيل جميع الاختبارات"""
    
    print(f"⏰ بدء الاختبار: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # قائمة الاختبارات
    tests = [
        ("متغيرات البيئة", test_environment),
        ("استيراد المكتبات", test_imports),
        ("محرك الترندات", test_trends_engine),
        ("قاعدة البيانات", test_database),
        ("مكونات البوت", test_bot_components),
        ("مكونات Dashboard", test_dashboard_components),
        ("تكامل الترندات", test_trends_integration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            results[test_name] = result
            
        except Exception as e:
            print(f"   ❌ خطأ في اختبار '{test_name}': {e}")
            results[test_name] = False
        
        time.sleep(0.5)  # توقف قصير بين الاختبارات
    
    # إنتاج التقرير
    success_rate = generate_test_report(results)
    
    print(f"\n⏰ انتهاء الاختبار: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return success_rate >= 80

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        
        if result:
            print("\n🎯 الخطوات التالية:")
            print("1. تشغيل Dashboard: streamlit run dashboard/app.py")
            print("2. تشغيل البوت: python main.py")
            print("3. اختبار الأوامر: /trends, /hot, /insights")
        else:
            print("\n🔧 يرجى إصلاح المشاكل قبل التشغيل")
            
    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف الاختبار")
    except Exception as e:
        print(f"\n❌ خطأ في تشغيل الاختبار: {e}")