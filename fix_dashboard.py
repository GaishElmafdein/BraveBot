#!/usr/bin/env python3
"""
إصلاح Dashboard من مشاكل الترميز
"""

from pathlib import Path

def fix_dashboard_encoding():
    """إصلاح ترميز Dashboard"""
    
    print("🔧 إصلاح Dashboard...")
    
    dashboard_files = [
        "dashboard/app.py",
        "main.py"
    ]
    
    # رموز المشكلة والبدائل
    emoji_fixes = {
        '🤖': 'BraveBot',
        '📊': '[تحليل]',
        '🔍': '[بحث]',
        '🚀': '[تشغيل]',
        '✅': '[نجح]',
        '❌': '[خطأ]',
        '⚠️': '[تحذير]',
        '📈': '[إحصائيات]',
        '💰': '[سعر]',
        '🎯': '[هدف]',
        '🌟': '[مميز]',
        '💡': '[نصيحة]'
    }
    
    for file_path in dashboard_files:
        path = Path(file_path)
        if path.exists():
            try:
                # قراءة الملف
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # استبدال الرموز
                original_content = content
                for emoji, replacement in emoji_fixes.items():
                    content = content.replace(emoji, replacement)
                
                # حفظ إذا تم التعديل
                if content != original_content:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✅ تم إصلاح: {file_path}")
                else:
                    print(f"✓ سليم: {file_path}")
                    
            except Exception as e:
                print(f"❌ فشل إصلاح {file_path}: {e}")
        else:
            print(f"⚠️ غير موجود: {file_path}")
    
    print("🎯 تم الإصلاح!")

if __name__ == "__main__":
    fix_dashboard_encoding()