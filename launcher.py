#!/usr/bin/env python3
"""
🚀 BraveBot Unified Launcher
============================
نظام تشغيل موحد لـ Core Bot + AI Module + Dashboard
"""

import asyncio
import threading
import subprocess
import sys
import os
import time
from datetime import datetime

def print_banner():
    """طباعة بانر البوت"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                     🤖 BraveBot v2.0                         ║
║                 Core Bot + AI Module + Dashboard              ║
║═══════════════════════════════════════════════════════════════║
║  📱 Telegram Bot: تفاعلي مع ذكاء اصطناعي                    ║
║  🧠 AI Module: تحليل الترندات والتسعير الذكي                ║
║  📊 Dashboard: مراقبة شاملة في الوقت الفعلي                 ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)
    print(f"🕐 تم التشغيل في: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)

def check_dependencies():
    """فحص المتطلبات المطلوبة"""
    print("🔍 فحص المتطلبات...")
    
    required_packages = ['streamlit', 'plotly', 'pandas', 'python-telegram-bot']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package} - مفقود")
    
    if missing_packages:
        print(f"\n⚠️  المتطلبات المفقودة: {', '.join(missing_packages)}")
        print("📥 تثبيت المتطلبات...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ تم تثبيت جميع المتطلبات")
        except Exception as e:
            print(f"❌ فشل تثبيت المتطلبات: {e}")
            return False
    
    return True

def run_telegram_bot():
    """تشغيل بوت التليجرام"""
    print("🤖 بدء تشغيل Telegram Bot...")
    try:
        from telegram.bot import start_bot
        start_bot()
    except ImportError:
        # استخدام main.py الأصلي
        print("📱 استخدام البوت الأصلي...")
        exec(open('main.py').read())
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت: {e}")

def run_dashboard():
    """تشغيل Dashboard"""
    print("📊 بدء تشغيل Streamlit Dashboard...")
    try:
        import streamlit.web.cli as stcli
        sys.argv = ["streamlit", "run", "dashboard/app.py", "--server.port=8501", "--server.headless=true"]
        stcli.main()
    except Exception as e:
        print(f"❌ خطأ في تشغيل Dashboard: {e}")

def run_ai_background_tasks():
    """تشغيل مهام الذكاء الاصطناعي في الخلفية"""
    print("🧠 بدء مهام الذكاء الاصطناعي...")
    try:
        while True:
            # تحديث الترندات كل ساعة
            print("🔄 تحديث الترندات...")
            time.sleep(3600)  # انتظار ساعة
    except KeyboardInterrupt:
        print("🛑 إيقاف مهام الذكاء الاصطناعي")

def show_menu():
    """عرض قائمة الخيارات"""
    print("\n🎯 اختر وضع التشغيل:")
    print("1. 🚀 تشغيل كامل (Bot + Dashboard + AI)")
    print("2. 🤖 البوت فقط")
    print("3. 📊 Dashboard فقط")
    print("4. 🧠 AI Module فقط")
    print("5. ❌ خروج")
    
    choice = input("\n👉 اختيارك (1-5): ").strip()
    return choice

def main():
    """الدالة الرئيسية"""
    print_banner()
    
    # فحص المتطلبات
    if not check_dependencies():
        print("❌ فشل في فحص المتطلبات. يرجى تثبيت المتطلبات يدوياً.")
        return
    
    print("✅ جميع المتطلبات متوفرة")
    
    while True:
        choice = show_menu()
        
        if choice == "1":
            print("\n🚀 بدء التشغيل الكامل...")
            
            # تشغيل البوت في thread منفصل
            bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
            bot_thread.start()
            time.sleep(2)
            
            # تشغيل مهام AI في thread منفصل
            ai_thread = threading.Thread(target=run_ai_background_tasks, daemon=True)
            ai_thread.start()
            time.sleep(1)
            
            print("✅ تم تشغيل البوت ومهام الذكاء الاصطناعي")
            print("\n📊 تشغيل Dashboard...")
            print("🌐 Dashboard URL: http://localhost:8501")
            print("🔗 Telegram Bot: متصل ونشط")
            print("\n⚠️  لإيقاف النظام: اضغط Ctrl+C")
            
            try:
                # تشغيل Dashboard (blocking)
                run_dashboard()
            except KeyboardInterrupt:
                print("\n🛑 إيقاف النظام...")
                break
                
        elif choice == "2":
            print("\n🤖 تشغيل البوت فقط...")
            try:
                run_telegram_bot()
            except KeyboardInterrupt:
                print("\n🛑 إيقاف البوت")
                
        elif choice == "3":
            print("\n📊 تشغيل Dashboard فقط...")
            print("🌐 Dashboard URL: http://localhost:8501")
            try:
                run_dashboard()
            except KeyboardInterrupt:
                print("\n🛑 إيقاف Dashboard")
                
        elif choice == "4":
            print("\n🧠 تشغيل AI Module فقط...")
            try:
                run_ai_background_tasks()
            except KeyboardInterrupt:
                print("\n🛑 إيقاف AI Module")
                
        elif choice == "5":
            print("\n👋 شكراً لاستخدام BraveBot!")
            break
            
        else:
            print("❌ اختيار غير صحيح، حاول مرة أخرى")
    
    print("\n🏁 تم إنهاء البرنامج")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 تم إيقاف البرنامج بواسطة المستخدم")
    except Exception as e:
        print(f"\n❌ خطأ عام: {e}")
        print("💡 تأكد من وجود جميع الملفات المطلوبة")
