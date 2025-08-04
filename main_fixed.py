#!/usr/bin/env python3
"""
BraveBot AI Commerce Empire - Main Launcher (Fixed Version)
==========================================================
نظام متقدم لتحليل الترندات والتجارة الذكية - نسخة محسنة
"""

import asyncio
import nest_asyncio
import threading
import time
import sys
import os
from pathlib import Path
from datetime import datetime

# إصلاح Event Loop للنظام الكامل
import platform
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

nest_asyncio.apply()

# إعداد المسارات
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# استيراد المكونات
from utils.helpers import setup_logging, check_environment
from core.ai_engine.ai_engine import get_ai_engine, get_engine_status

# إعداد Logger
logger = setup_logging()

class BraveBotLauncher:
    """مشغل BraveBot المتقدم مع إدارة Event Loop محسنة"""
    
    def __init__(self):
        self.bot_running = False
        self.dashboard_running = False
        self.bot_thread = None
        self.dashboard_thread = None
        
    def show_main_menu(self):
        """عرض القائمة الرئيسية"""
        
        print("\n" + "="*60)
        print("BraveBot AI Commerce Empire v2.0")
        print("="*60)
        
        # حالة النظام - إصلاح
        try:
            engine_status = get_engine_status()
            ai_status = "[SUCCESS] نشط" if engine_status.get('status') == 'active' else "[READY] جاهز"
        except:
            ai_status = "[READY] جاهز"
        
        print(f"AI Engine: {ai_status}")
        print(f"الوقت: {datetime.now().strftime('%H:%M:%S')}")
        print("="*60)
        
        print("اختر الخدمة:")
        print("1. البوت فقط (Telegram Bot)")
        print("2. Dashboard فقط (Web Interface)")
        print("3. النظام الكامل (مستحسن)")
        print("4. الإعدادات والصيانة")
        print("5. إنهاء البرنامج")
        print("="*60)
        
        return input("اختيارك (1-5): ").strip()

    def start_telegram_bot_thread(self):
        """تشغيل بوت التليجرام في thread منفصل"""
        
        def run_bot():
            try:
                from telegrambot import create_bot_application
                
                # إنشاء حلقة أحداث جديدة للبوت
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                async def bot_main():
                    application = create_bot_application()
                    print("[SUCCESS] Bot started successfully!")
                    print("Send /start to your bot to begin!")
                    
                    # تشغيل البوت - الطريقة الصحيحة
                    await application.run_polling(
                        drop_pending_updates=True
                    )
                
                # تشغيل البوت
                loop.run_until_complete(bot_main())
                
            except Exception as e:
                logger.error(f"Bot thread error: {e}")
                self.bot_running = False
            finally:
                try:
                    loop.close()
                except:
                    pass
    
        # تشغيل في thread منفصل
        self.bot_thread = threading.Thread(target=run_bot, daemon=True)
        self.bot_thread.start()
        self.bot_running = True
        
        print("البوت يعمل في الخلفية...")
        return True

    def start_dashboard_thread(self):
        """تشغيل Dashboard في thread منفصل"""
        
        def run_dashboard():
            try:
                import subprocess
                import webbrowser
                import os
                
                print("تشغيل Dashboard...")
                
                # تأكد من وجود ملف Dashboard
                dashboard_file = project_root / "dashboard" / "app.py"
                if not dashboard_file.exists():
                    print("إنشاء Dashboard...")
                    self.create_simple_dashboard()
                
                # تشغيل Dashboard باستخدام cmd
                cmd = f'streamlit run "{dashboard_file}" --server.port 8501 --server.headless true'
                
                print(f"Executing: {cmd}")
                
                # تشغيل الأمر
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(project_root),
                    creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
                )
                
                # انتظار قليل للتأكد من البدء
                time.sleep(5)
                
                # فتح المتصفح
                try:
                    webbrowser.open("http://localhost:8501")
                    print("✅ Dashboard opened in browser!")
                except Exception as e:
                    print(f"Browser error: {e}")
                    print("📱 Manual access: http://localhost:8501")
            
                # مراقبة العملية
                while self.dashboard_running:
                    if process.poll() is not None:
                        print("❌ Dashboard process ended")
                        break
                    time.sleep(1)
                
            except Exception as e:
                print(f"❌ Dashboard error: {e}")
                print("💡 Try manual start: streamlit run dashboard/app.py")
            finally:
                self.dashboard_running = False
    
        # تشغيل في thread منفصل
        self.dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
        self.dashboard_thread.start()
        self.dashboard_running = True
        
        return True

    def create_simple_dashboard(self):
        """إنشاء Dashboard بسيط إذا لم يوجد"""
        
        dashboard_dir = project_root / "dashboard"
        dashboard_dir.mkdir(exist_ok=True)
        
        dashboard_code = '''
import streamlit as st
import sys
from pathlib import Path

# إضافة مسار المشروع
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

st.set_page_config(
    page_title="BraveBot Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("BraveBot AI Commerce Empire")
st.markdown("---")

# تحليل الترندات
st.header("تحليل الترندات")

col1, col2 = st.columns(2)

with col1:
    keyword = st.text_input("كلمة البحث", value="gaming chair")
    if st.button("تحليل"):
        try:
            from ai.trends_engine import fetch_viral_trends
            
            with st.spinner("جاري التحليل..."):
                result = fetch_viral_trends(keyword, 5)
            
            st.success("تم التحليل بنجاح!")
            
            # عرض النتائج
            for trend in result.get('top_keywords', []):
                st.metric(
                    f"النتيجة: {trend['keyword']}", 
                    f"{trend['viral_score']}%",
                    f"المصدر: {trend.get('source', 'AI Analysis')}"
                )
                
        except Exception as e:
            st.error(f"خطأ: {e}")

with col2:
    st.subheader("التسعير الذكي")
    
    base_price = st.number_input("السعر الأساسي", value=29.99, min_value=0.01)
    viral_score = st.slider("النقاط الفيروسية", 0, 100, 75)
    
    if st.button("اقتراح السعر"):
        try:
            from ai.trends_engine import dynamic_pricing_suggestion
            
            pricing = dynamic_pricing_suggestion(base_price, viral_score)
            
            st.success(f"السعر المقترح: ${pricing['suggested_price']:.2f}")
            st.info(f"هامش الربح: {pricing['profit_margin']:.1f}%")
            
        except Exception as e:
            st.error(f"خطأ: {e}")

# معلومات النظام
st.markdown("---")
st.subheader("معلومات النظام")

try:
    from core.ai_engine.ai_engine import get_engine_status
    status = get_engine_status()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("محرك AI", "نشط" if status['status'] == 'active' else "معطل")
    
    with col2:
        st.metric("الإصدار", "v2.0")
    
    with col3:
        st.metric("الحالة", "جاهز")
        
except Exception as e:
    st.error(f"خطأ في حالة النظام: {e}")
'''
        
        dashboard_file = dashboard_dir / "app.py"
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(dashboard_code)
        
        print("تم إنشاء Dashboard بسيط")

    def start_bot_only(self):
        """تشغيل البوت فقط"""
        
        print("تشغيل البوت...")
        success = self.start_telegram_bot_thread()
        
        if success:
            print("[SUCCESS] البوت يعمل!")
            print("أرسل /start للبوت للبدء")
            
            # انتظار إشارة الإيقاف
            try:
                while self.bot_running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nتم إيقاف البوت")
                
        return success

    def start_dashboard_only(self):
        """تشغيل Dashboard فقط"""
        
        print("تشغيل Dashboard...")
        success = self.start_dashboard_thread()
        
        if success:
            print("[SUCCESS] Dashboard يعمل!")
            print("اذهب إلى: http://localhost:8501")
            
            # انتظار إشارة الإيقاف
            try:
                while self.dashboard_running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nتم إيقاف Dashboard")
                
        return success

    def start_full_system(self):
        """تشغيل النظام الكامل"""
        
        print("تشغيل النظام الكامل...")
        
        bot_success = self.start_telegram_bot_thread()
        dashboard_success = self.start_dashboard_thread()
        
        if bot_success and dashboard_success:
            print("[SUCCESS] النظام الكامل يعمل!")
            print("البوت: أرسل /start")
            print("Dashboard: http://localhost:8501")
            
            # انتظار إشارة الإيقاف
            try:
                while self.bot_running or self.dashboard_running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nتم إيقاف النظام الكامل")
                
        return bot_success and dashboard_success

    def show_settings_menu(self):
        """قائمة الإعدادات"""
        
        print("\nإعدادات النظام")
        print("-" * 30)
        
        try:
            # فحص البيئة
            env_status = check_environment()
            print(f"البيئة: سليمة" if env_status else "البيئة: تحتاج مراجعة")
            
            # حالة المحرك
            engine_status = get_engine_status()
            print(f"محرك AI: {engine_status['status']}")
            
            # إحصائيات سريعة
            from ai.trends_engine import fetch_viral_trends
            test_result = fetch_viral_trends("test", 1)
            print(f"محرك الترندات: يعمل ({len(test_result.get('top_keywords', []))} نتيجة)")
            
        except Exception as e:
            print(f"خطأ في فحص الإعدادات: {e}")
        
        input("\nاضغط Enter للعودة...")

    def run(self):
        """تشغيل التطبيق الرئيسي"""
        
        # التحقق من البيئة
        if not check_environment():
            print("فشل فحص البيئة!")
            return
        
        # التحقق من محرك AI
        engine = get_ai_engine()
        if not engine:
            print("فشل تحميل محرك AI!")
            return
        
        print("[SUCCESS] جميع الأنظمة جاهزة!")
        
        # حلقة القائمة الرئيسية
        while True:
            try:
                choice = self.show_main_menu()
                
                if choice == "1":
                    self.start_bot_only()
                elif choice == "2":
                    self.start_dashboard_only()
                elif choice == "3":
                    self.start_full_system()
                elif choice == "4":
                    self.show_settings_menu()
                elif choice == "5":
                    print("شكراً لاستخدام BraveBot!")
                    break
                else:
                    print("خيار غير صحيح!")
                    
            except KeyboardInterrupt:
                print("\nتم إنهاء البرنامج")
                break

def main():
    """النقطة الرئيسية للتطبيق"""
    
    try:
        launcher = BraveBotLauncher()
        launcher.run()
        
    except Exception as e:
        logger.error(f"Critical error: {e}")
        print(f"خطأ حرج: {e}")

if __name__ == "__main__":
    main()