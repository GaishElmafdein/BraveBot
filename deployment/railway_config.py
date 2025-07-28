#!/usr/bin/env python3
"""
🚀 Railway Deployment Configuration
==================================
إعدادات النشر على Railway
"""

import os
from pathlib import Path

# إنشاء ملف requirements.txt
requirements_content = """
streamlit>=1.47.1
plotly>=6.2.0
pandas>=2.3.1
requests>=2.32.3
asyncio
telegram-bot>=20.0
reportlab>=4.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
sqlite3
python-dotenv>=1.0.0
nest-asyncio>=1.6.0
"""

# إنشاء ملف Procfile
procfile_content = """
web: streamlit run dashboard/app.py --server.port=$PORT --server.address=0.0.0.0
"""

# إنشاء ملف .env.example
env_example_content = """
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# eBay API Configuration
EBAY_APP_ID=your_ebay_app_id_here

# Amazon/RapidAPI Configuration
RAPIDAPI_KEY=your_rapidapi_key_here

# Database Configuration
DATABASE_URL=sqlite:///data/bravebot.db

# Application Settings
DEBUG=False
ENVIRONMENT=production
"""

# إنشاء ملف runtime.txt
runtime_content = """
python-3.11.0
"""

def create_deployment_files():
    """إنشاء ملفات النشر"""
    
    # إنشاء requirements.txt
    with open("requirements.txt", "w") as f:
        f.write(requirements_content.strip())
    
    # إنشاء Procfile
    with open("Procfile", "w") as f:
        f.write(procfile_content.strip())
    
    # إنشاء .env.example
    with open(".env.example", "w") as f:
        f.write(env_example_content.strip())
    
    # إنشاء runtime.txt
    with open("runtime.txt", "w") as f:
        f.write(runtime_content.strip())
    
    print("✅ تم إنشاء ملفات النشر بنجاح!")
    print("📁 الملفات المُنشأة:")
    print("  - requirements.txt")
    print("  - Procfile")
    print("  - .env.example")
    print("  - runtime.txt")
    
    print("\n🚀 خطوات النشر على Railway:")
    print("1. انشئ حساب على railway.app")
    print("2. ارفع المشروع على GitHub")
    print("3. اربط Repository بـ Railway")
    print("4. أضف المتغيرات البيئية من .env.example")
    print("5. انتظر النشر التلقائي!")

if __name__ == "__main__":
    create_deployment_files()