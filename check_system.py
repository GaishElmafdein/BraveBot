#!/usr/bin/env python3
"""
🔍 BraveBot System Checker
=========================
فحص شامل لجميع مكونات النظام قبل التشغيل
"""

import os
import sys
import time
import json
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# إضافة مسار المشروع
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class BraveBotSystemChecker:
    """فاحص النظام الشامل"""
    
    def __init__(self):
        self.results = {}
        self.errors = []
        self.warnings = []
        
    def print_header(self):
        """طباعة رأس الفاحص"""
        print("🔍 BraveBot v2.0 - System Health Check")
        print("=" * 50)
        print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Project: {project_root}")
        print("=" * 50)
    
    def check_environment(self) -> bool:
        """فحص متغيرات البيئة"""
        print("\n🌍 1. Environment Variables Check:")
        
        env_file = project_root / ".env"
        env_example = project_root / ".env.example"
        
        if not env_file.exists():
            if env_example.exists():
                print("   ⚠️  .env file missing, but .env.example found")
                print("   💡 Run: cp .env.example .env")
            else:
                print("   ❌ Both .env and .env.example missing")
                return False
        
        # فحص المتغيرات المطلوبة
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = [
            ('TELEGRAM_TOKEN', 'Telegram Bot Token'),
            ('DATABASE_URL', 'Database URL'),
        ]
        
        missing_vars = []
        for var, desc in required_vars:
            value = os.getenv(var)
            if not value:
                print(f"   ❌ {var}: Missing")
                missing_vars.append(var)
            else:
                # إخفاء التوكن الحساس
                display_value = value[:10] + "..." if len(value) > 10 else value
                print(f"   ✅ {var}: {display_value}")
        
        if missing_vars:
            print(f"\n   💡 Add these to your .env file:")
            for var in missing_vars:
                print(f"   {var}=your_value_here")
            return False
        
        print("   ✅ All environment variables found")
        return True
    
    def check_dependencies(self) -> bool:
        """فحص المكتبات المطلوبة"""
        print("\n📦 2. Dependencies Check:")
        
        dependencies = [
            ('telegram', 'python-telegram-bot'),
            ('streamlit', 'streamlit'),
            ('pandas', 'pandas'),
            ('plotly', 'plotly'),
            ('requests', 'requests'),
            ('dotenv', 'python-dotenv'),
            ('sqlite3', 'sqlite3 (built-in)'),
            ('asyncio', 'asyncio (built-in)'),
            ('pathlib', 'pathlib (built-in)')
        ]
        
        missing = []
        for module, package in dependencies:
            try:
                __import__(module)
                print(f"   ✅ {package}")
            except ImportError:
                print(f"   ❌ {package}: Not installed")
                missing.append(package)
        
        if missing:
            print(f"\n   💡 Install missing packages:")
            print(f"   pip install {' '.join([p for p in missing if 'built-in' not in p])}")
            return False
        
        print("   ✅ All dependencies available")
        return True
    
    def check_file_structure(self) -> bool:
        """فحص هيكل الملفات"""
        print("\n📁 3. File Structure Check:")
        
        required_files = [
            'main.py',
            'requirements.txt',
            'dashboard/app.py',
            'core/__init__.py',
            'core/config.py',
            'telegrambot/__init__.py',
            'ai/__init__.py'
        ]
        
        optional_files = [
            'core/ai_engine/ai_engine.py',
            'ai/trends_engine.py',
            'telegram/handlers.py',
            'bot/main.py'
        ]
        
        missing_required = []
        for file_path in required_files:
            full_path = project_root / file_path
            if full_path.exists():
                print(f"   ✅ {file_path}")
            else:
                print(f"   ❌ {file_path}: Missing")
                missing_required.append(file_path)
        
        print("\n   📋 Optional files:")
        for file_path in optional_files:
            full_path = project_root / file_path
            if full_path.exists():
                print(f"   ✅ {file_path}")
            else:
                print(f"   ⚠️  {file_path}: Optional, not found")
        
        if missing_required:
            return False
        
        print("   ✅ Core file structure complete")
        return True
    
    def check_database(self) -> bool:
        """فحص قاعدة البيانات"""
        print("\n🗃️  4. Database Check:")
        
        try:
            import sqlite3
            
            db_url = os.getenv('DATABASE_URL', 'sqlite:///bravebot.db')
            if db_url.startswith('sqlite:///'):
                db_path = db_url.replace('sqlite:///', '')
                db_full_path = project_root / db_path
                
                if db_full_path.exists():
                    print(f"   ✅ Database file exists: {db_path}")
                    
                    # فحص الاتصال
                    conn = sqlite3.connect(str(db_full_path))
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    conn.close()
                    
                    print(f"   ✅ Database accessible, {len(tables)} tables found")
                else:
                    print(f"   ⚠️  Database file will be created: {db_path}")
            else:
                print(f"   ✅ External database configured: {db_url[:20]}...")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Database error: {e}")
            return False
    
    def check_ai_engine(self) -> bool:
        """فحص محرك الذكاء الاصطناعي"""
        print("\n🧠 5. AI Engine Check:")
        
        try:
            # محاولة استيراد المحرك
            from core.ai_engine.ai_engine import get_ai_engine, get_engine_status
            
            engine = get_ai_engine()
            status = get_engine_status()
            
            print(f"   ✅ AI Engine Status: {status.get('status', 'unknown')}")
            print(f"   ✅ Active Engines: {len(status.get('active_engines', []))}")
            print(f"   ✅ Cache Size: {status.get('cache_size', 0)}")
            
            return True
            
        except ImportError as e:
            print(f"   ⚠️  AI Engine: Limited mode ({e})")
            return True  # لا يعتبر خطأ حرج
        except Exception as e:
            print(f"   ❌ AI Engine error: {e}")
            return False
    
    def check_telegram_bot(self) -> bool:
        """فحص إعدادات بوت التليجرام"""
        print("\n🤖 6. Telegram Bot Check:")
        
        token = os.getenv('TELEGRAM_TOKEN')
        if not token:
            print("   ❌ TELEGRAM_TOKEN not found")
            return False
        
        try:
            import requests
            
            # فحص صحة التوكن
            url = f"https://api.telegram.org/bot{token}/getMe"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    bot_info = data['result']
                    print(f"   ✅ Bot Token Valid: @{bot_info.get('username', 'unknown')}")
                    print(f"   ✅ Bot Name: {bot_info.get('first_name', 'unknown')}")
                    return True
                else:
                    print(f"   ❌ Invalid token response: {data}")
                    return False
            else:
                print(f"   ❌ Token validation failed: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            print(f"   ⚠️  Network error, cannot validate token: {e}")
            return True  # Network issues shouldn't fail the check
        except Exception as e:
            print(f"   ❌ Token check error: {e}")
            return False
    
    def check_dashboard(self) -> bool:
        """فحص Dashboard"""
        print("\n📊 7. Dashboard Check:")
        
        dashboard_file = project_root / "dashboard" / "app.py"
        
        if not dashboard_file.exists():
            print("   ❌ Dashboard app.py not found")
            return False
        
        print("   ✅ Dashboard file exists")
        
        # فحص إمكانية تشغيل streamlit
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'streamlit', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"   ✅ Streamlit available: {version}")
                return True
            else:
                print(f"   ❌ Streamlit error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("   ⚠️  Streamlit check timeout")
            return True
        except Exception as e:
            print(f"   ❌ Streamlit check failed: {e}")
            return False
    
    def check_ports(self) -> bool:
        """فحص المنافذ المطلوبة"""
        print("\n🔌 8. Port Availability Check:")
        
        import socket
        
        ports_to_check = [
            (8501, "Streamlit Dashboard"),
            (8080, "Alternative Dashboard")
        ]
        
        all_available = True
        for port, service in ports_to_check:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            
            try:
                result = sock.connect_ex(('localhost', port))
                if result == 0:
                    print(f"   ⚠️  Port {port} ({service}): In use")
                    all_available = False
                else:
                    print(f"   ✅ Port {port} ({service}): Available")
            except Exception as e:
                print(f"   ⚠️  Port {port} check failed: {e}")
            finally:
                sock.close()
        
        return all_available
    
    async def test_system_integration(self) -> bool:
        """اختبار التكامل بين المكونات"""
        print("\n🔗 9. System Integration Test:")
        
        try:
            # اختبار محرك الترندات
            from ai.trends_engine import fetch_viral_trends
            
            print("   🔍 Testing trends engine...")
            result = await asyncio.wait_for(
                asyncio.to_thread(fetch_viral_trends, "test", 1),
                timeout=10
            )
            
            if result and 'top_keywords' in result:
                print("   ✅ Trends engine: Working")
            else:
                print("   ⚠️  Trends engine: Limited functionality")
            
            return True
            
        except ImportError:
            print("   ⚠️  Trends engine: Not available")
            return True
        except asyncio.TimeoutError:
            print("   ⚠️  Trends engine: Timeout")
            return True
        except Exception as e:
            print(f"   ❌ Integration test failed: {e}")
            return False
    
    def generate_report(self) -> Dict[str, Any]:
        """إنتاج تقرير النتائج"""
        passed = sum(1 for result in self.results.values() if result)
        total = len(self.results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"\n" + "=" * 50)
        print("📋 SYSTEM CHECK REPORT")
        print("=" * 50)
        
        for check_name, result in self.results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {check_name}")
        
        print(f"\n📊 Overall Score: {passed}/{total} ({success_rate:.1f}%)")
        
        if success_rate >= 90:
            print("🎉 System Status: EXCELLENT - Ready for production!")
        elif success_rate >= 70:
            print("✅ System Status: GOOD - Ready to run with minor issues")
        elif success_rate >= 50:
            print("⚠️  System Status: FAIR - Some issues need attention")
        else:
            print("❌ System Status: POOR - Critical issues must be fixed")
        
        return {
            'success_rate': success_rate,
            'passed': passed,
            'total': total,
            'results': self.results,
            'errors': self.errors,
            'warnings': self.warnings
        }
    
    def print_recommendations(self):
        """طباعة التوصيات"""
        print(f"\n💡 RECOMMENDATIONS:")
        print("-" * 30)
        
        if not self.results.get('Environment Variables', True):
            print("• Set up environment variables in .env file")
        
        if not self.results.get('Dependencies', True):
            print("• Install missing Python packages")
        
        if not self.results.get('File Structure', True):
            print("• Restore missing core files")
        
        if not self.results.get('Telegram Bot', True):
            print("• Check TELEGRAM_TOKEN and bot configuration")
        
        if not self.results.get('Dashboard', True):
            print("• Install streamlit: pip install streamlit")
        
        print("\n🚀 QUICK START:")
        print("1. Fix any FAIL items above")
        print("2. Run: python main.py")
        print("3. Or run: python launcher.py")
    
    async def run_full_check(self) -> Dict[str, Any]:
        """تشغيل الفحص الكامل"""
        self.print_header()
        
        # تشغيل جميع الفحوصات
        checks = [
            ("Environment Variables", self.check_environment),
            ("Dependencies", self.check_dependencies),
            ("File Structure", self.check_file_structure),
            ("Database", self.check_database),
            ("AI Engine", self.check_ai_engine),
            ("Telegram Bot", self.check_telegram_bot),
            ("Dashboard", self.check_dashboard),
            ("Port Availability", self.check_ports),
            ("System Integration", self.test_system_integration)
        ]
        
        for check_name, check_func in checks:
            try:
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()
                
                self.results[check_name] = result
                
            except Exception as e:
                print(f"   ❌ {check_name} check failed: {e}")
                self.results[check_name] = False
                self.errors.append(f"{check_name}: {e}")
        
        # إنتاج التقرير
        report = self.generate_report()
        self.print_recommendations()
        
        return report

async def main():
    """الدالة الرئيسية"""
    checker = BraveBotSystemChecker()
    report = await checker.run_full_check()
    
    # حفظ التقرير
    report_file = project_root / "logs" / f"system_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n📄 Report saved: {report_file}")
    
    return report['success_rate'] >= 70

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit_code = 0 if success else 1
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️ System check interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ System check failed: {e}")
        sys.exit(1)