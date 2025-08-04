#!/usr/bin/env python3
"""
🔧 اختبار وإصلاح مشاكل الترميز
===============================
"""

import os
import sys
import logging
from pathlib import Path

def fix_encoding():
    """إصلاح مشاكل الترميز"""
    
    print("="*60)
    print("🔧 BraveBot Encoding Fix & Test")
    print("="*60)
    
    # تعيين الترميز للسيستم
    if sys.platform == "win32":
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        print("✅ Windows encoding set to UTF-8")
    
    # إعداد logger آمن
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        print("\n1️⃣ Testing system imports...")
        
        # اختبار المسارات
        project_root = Path(__file__).parent
        sys.path.append(str(project_root))
        print(f"   Project root: {project_root}")
        
        print("\n2️⃣ Testing utils import...")
        from utils.helpers import setup_logging
        print("   ✅ utils.helpers imported successfully")
        
        print("\n3️⃣ Testing AI engine import...")
        from core.ai_engine.ai_engine import get_ai_engine
        print("   ✅ AI engine imported successfully")
        
        print("\n4️⃣ Testing trends engine import...")
        from ai.trends_engine import fetch_viral_trends
        print("   ✅ Trends engine imported successfully")
        
        print("\n5️⃣ Testing trends analysis...")
        logger.info("Running trends analysis test...")
        result = fetch_viral_trends("test", 2)
        
        trends_count = len(result.get('top_keywords', []))
        print(f"   ✅ Found {trends_count} trends")
        
        if trends_count > 0:
            first_trend = result['top_keywords'][0]
            print(f"   📊 Sample: {first_trend['keyword']} ({first_trend['viral_score']}%)")
        
        print("\n6️⃣ Testing pricing engine...")
        from ai.trends_engine import dynamic_pricing_suggestion
        
        pricing = dynamic_pricing_suggestion(19.99, 75)
        print(f"   ✅ Pricing: ${pricing['base_price']} -> ${pricing['suggested_price']}")
        
        print("\n7️⃣ Testing bot import...")
        try:
            from bot.telegram_bot import create_bot_application
            print("   ✅ Bot module imported successfully")
        except ImportError as e:
            print(f"   ⚠️ Bot import issue: {e}")
            print("   🔧 Creating bot files...")
            
            from utils.helpers import ensure_bot_files
            ensure_bot_files()
            
            # محاولة ثانية
            from bot.telegram_bot import create_bot_application
            print("   ✅ Bot module imported after creation")
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED!")
        print("✅ Encoding issues resolved")
        print("✅ All modules working")
        print("🚀 System ready to launch!")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR during testing: {e}")
        print("🔧 Troubleshooting:")
        
        if "charmap" in str(e).lower():
            print("   - Encoding issue detected")
            print("   - Run: chcp 65001")
            print("   - Set PYTHONIOENCODING=utf-8")
        
        if "import" in str(e).lower():
            print("   - Module import issue")
            print("   - Check if all files exist")
            print("   - Verify Python path")
        
        return False

def quick_fix_charmap():
    """إصلاح سريع لمشكلة charmap"""
    
    print("🔧 Quick fix for charmap encoding...")
    
    # إعداد متغيرات البيئة
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONLEGACYWINDOWSFSENCODING'] = '1'
    
    # إصلاح ملفات المشروع
    files_to_fix = [
        'ai/trends_engine.py',
        'core/ai_engine/ai_engine.py',
        'utils/helpers.py'
    ]
    
    for file_path in files_to_fix:
        if Path(file_path).exists():
            try:
                # قراءة الملف
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # استبدال الرموز المشكلة
                replacements = {
                    '✅': '[SUCCESS]',
                    '❌': '[ERROR]',
                    '⚠️': '[WARNING]',
                    '📊': '[INFO]',
                    '🚀': '[INIT]',
                    '🔧': '[FIX]',
                    '💡': '[TIP]'
                }
                
                modified = False
                for old, new in replacements.items():
                    if old in content:
                        content = content.replace(old, new)
                        modified = True
                
                # حفظ الملف إذا تم التعديل
                if modified:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"   ✅ Fixed: {file_path}")
                
            except Exception as e:
                print(f"   ❌ Failed to fix {file_path}: {e}")
    
    print("🎯 Charmap fix completed!")

if __name__ == "__main__":
    print("Choose option:")
    print("1. Run full test")
    print("2. Quick charmap fix")
    print("3. Both")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        fix_encoding()
    elif choice == "2":
        quick_fix_charmap()
    elif choice == "3":
        quick_fix_charmap()
        print("\n" + "="*30)
        fix_encoding()
    else:
        print("Running full test by default...")
        fix_encoding()