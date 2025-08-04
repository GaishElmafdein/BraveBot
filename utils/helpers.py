#!/usr/bin/env python3
"""
🛠️ BraveBot Helper Functions
============================
دوال مساعدة أساسية للنظام
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

def setup_logging(log_file: str = "logs/bravebot.log") -> logging.Logger:
    """إعداد نظام التسجيل مع ترميز آمن"""
    
    # إنشاء مجلد السجلات
    Path("logs").mkdir(exist_ok=True)
    
    # إعداد التنسيق بدون رموز خاصة
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # إعداد المسجل
    logger = logging.getLogger("BraveBot")
    logger.setLevel(logging.INFO)
    
    # تجنب المعالجات المكررة
    if not logger.handlers:
        # معالج الملف مع ترميز آمن
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8', errors='replace')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception:
            # fallback للترميز الافتراضي
            try:
                file_handler = logging.FileHandler(log_file, errors='replace')
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except:
                pass
        
        # معالج وحدة التحكم مع ترميز آمن
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # إعداد ترميز آمن للكونسول
        if hasattr(console_handler.stream, 'reconfigure'):
            try:
                console_handler.stream.reconfigure(encoding='utf-8', errors='replace')
            except:
                pass
        
        logger.addHandler(console_handler)
    
    return logger

def check_environment() -> bool:
    """فحص البيئة والإعدادات"""
    
    try:
        # فحص الملفات الأساسية
        essential_files = [
            "main.py",
            ".env",
            "ai/trends_engine.py",
            "core/ai_engine/ai_engine.py",
            "config/ai_config.json"
        ]
        
        missing_files = []
        for file_path in essential_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"⚠️ ملفات مفقودة: {', '.join(missing_files)}")
            # لا نفشل - فقط تحذير
        
        # فحص متغيرات البيئة الأساسية
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            print("⚠️ python-dotenv غير مثبت")
        
        telegram_token = os.getenv('TELEGRAM_TOKEN')
        if not telegram_token:
            print("⚠️ TELEGRAM_TOKEN غير موجود في .env")
            # لا نفشل - يمكن إضافته لاحقاً
        
        # فحص إمكانية الاستيراد
        try:
            from ai.trends_engine import fetch_viral_trends
            from core.ai_engine.ai_engine import get_ai_engine
            print("✅ الوحدات الأساسية متاحة")
        except ImportError as e:
            print(f"⚠️ مشكلة في الاستيراد: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في فحص البيئة: {e}")
        return False

def load_json_config(file_path: str, default: Dict[str, Any] = None) -> Dict[str, Any]:
    """تحميل ملف إعدادات JSON"""
    
    try:
        if not Path(file_path).exists():
            if default:
                return default
            raise FileNotFoundError(f"Config file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # إزالة التعليقات من JSON
            lines = content.split('\n')
            clean_lines = []
            for line in lines:
                if not line.strip().startswith('//'):
                    clean_lines.append(line)
            clean_content = '\n'.join(clean_lines)
            return json.loads(clean_content)
            
    except json.JSONDecodeError as e:
        print(f"❌ خطأ في JSON: {file_path} - {e}")
        return default or {}
    except Exception as e:
        print(f"❌ خطأ في تحميل الإعدادات: {e}")
        return default or {}

def save_json_config(data: Dict[str, Any], file_path: str) -> bool:
    """حفظ ملف إعدادات JSON"""
    
    try:
        # إنشاء المجلد إذا لم يكن موجوداً
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ فشل حفظ الإعدادات {file_path}: {e}")
        return False

def format_currency(amount: float, currency: str = "USD") -> str:
    """تنسيق العملة"""
    
    if currency == "USD":
        return f"${amount:.2f}"
    elif currency == "EUR":
        return f"€{amount:.2f}"
    elif currency == "SAR":
        return f"{amount:.2f} ر.س"
    else:
        return f"{amount:.2f} {currency}"

def format_percentage(value: float, decimals: int = 1) -> str:
    """تنسيق النسبة المئوية"""
    return f"{value:.{decimals}f}%"

def format_timestamp(timestamp: Optional[datetime] = None) -> str:
    """تنسيق الوقت"""
    if not timestamp:
        timestamp = datetime.now()
    
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """اختصار النص"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def validate_viral_score(score: Any) -> int:
    """التحقق من صحة نقاط الفيروسية"""
    try:
        score = int(score)
        return max(0, min(100, score))  # ضمان النطاق 0-100
    except (ValueError, TypeError):
        return 50  # قيمة افتراضية

def validate_price(price: Any) -> float:
    """التحقق من صحة السعر"""
    try:
        price = float(price)
        return max(0.01, price)  # ضمان سعر إيجابي
    except (ValueError, TypeError):
        return 0.0

def create_directory_structure():
    """إنشاء هيكل المجلدات الأساسي"""
    directories = [
        'logs', 'data', 'data/cache', 'data/exports', 
        'data/backups', 'config', 'dashboard', 'bot'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        # إنشاء ملف .gitkeep للمجلدات الفارغة
        gitkeep_file = Path(directory) / '.gitkeep'
        if not gitkeep_file.exists():
            try:
                gitkeep_file.touch()
            except:
                pass

def get_project_info() -> Dict[str, Any]:
    """معلومات المشروع"""
    return {
        "name": "BraveBot AI Commerce Empire",
        "version": "2.0.0",
        "description": "AI-Powered E-commerce Trends Analysis Bot",
        "author": "BraveBot Team",
        "timestamp": format_timestamp(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "status": "Active Development"
    }

def quick_log(message: str, level: str = "info"):
    """تسجيل سريع"""
    logger = logging.getLogger("BraveBot")
    
    if level.lower() == "error":
        logger.error(message)
    elif level.lower() == "warning":
        logger.warning(message)
    else:
        logger.info(message)

def quick_format_result(data: Dict[str, Any], title: str = "Result") -> str:
    """تنسيق سريع للنتائج"""
    formatted = f"🎯 {title}\n" + "="*50 + "\n"
    
    for key, value in data.items():
        if isinstance(value, (int, float)):
            if key.endswith('_score') or key.endswith('_percentage'):
                formatted += f"• {key}: {value}%\n"
            elif key.endswith('_price') or key.endswith('_amount'):
                formatted += f"• {key}: ${value:.2f}\n"
            else:
                formatted += f"• {key}: {value}\n"
        else:
            formatted += f"• {key}: {value}\n"
    
    return formatted

def ensure_bot_files():
    """التأكد من وجود ملفات البوت الأساسية"""
    
    # إنشاء مجلد bot إذا لم يوجد
    bot_dir = Path("bot")
    bot_dir.mkdir(exist_ok=True)
    
    # إنشاء __init__.py
    init_file = bot_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text('"""BraveBot Telegram Bot Module"""', encoding='utf-8')
    
    # إنشاء telegram_bot.py إذا لم يوجد
    bot_file = bot_dir / "telegram_bot.py"
    if not bot_file.exists():
        # استخدام write_text مباشرة لتجنب مشاكل التنصيص
        bot_file.write_text(create_bot_code(), encoding='utf-8')
        print("✅ تم إنشاء ملف البوت")

def create_bot_code() -> str:
    """إنشاء كود البوت كـ string"""
    return """#!/usr/bin/env python3
# BraveBot Telegram Bot
# ===================

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "🤖 أهلاً بك في BraveBot AI Commerce Empire!\\n\\n"
        "🎯 الأوامر المتاحة:\\n"
        "/trends - تحليل الترندات\\n"
        "/price - اقتراح الأسعار\\n"
        "/insights - رؤى السوق\\n"
        "/help - المساعدة\\n\\n"
        "💡 أرسل أي كلمة مفتاحية لتحليلها!"
    )
    
    await update.message.reply_text(welcome_message)

async def trends_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        keyword = " ".join(context.args) if context.args else "gaming"
        
        await update.message.reply_text(f"🔍 جاري تحليل '{keyword}'...")
        
        from ai.trends_engine import fetch_viral_trends
        result = fetch_viral_trends(keyword, 5)
        
        response = f"📊 تحليل الترندات لـ: {keyword}\\n\\n"
        
        for i, trend in enumerate(result.get('top_keywords', [])[:3], 1):
            response += f"{i}. 🎯 {trend['keyword']}\\n"
            response += f"   📈 النقاط: {trend['viral_score']}%\\n"
            response += f"   🔗 المصدر: {trend.get('source', 'AI Analysis')}\\n\\n"
        
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Trends command error: {e}")
        await update.message.reply_text("❌ حدث خطأ في تحليل الترندات")

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if context.args:
            base_price = float(context.args[0])
        else:
            base_price = 19.99
        
        await update.message.reply_text(f"💰 جاري حساب السعر المقترح...")
        
        from ai.trends_engine import dynamic_pricing_suggestion
        pricing = dynamic_pricing_suggestion(base_price, 75)
        
        response = f"💰 اقتراح التسعير:\\n\\n"
        response += f"💵 السعر الأساسي: ${pricing['base_price']:.2f}\\n"
        response += f"🚀 السعر المقترح: ${pricing['suggested_price']:.2f}\\n"
        response += f"📈 هامش الربح: {pricing['profit_margin']:.1f}%\\n"
        response += f"⭐ التقييم: {pricing.get('recommendation', 'جيد')}"
        
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Price command error: {e}")
        await update.message.reply_text("❌ حدث خطأ في اقتراح السعر")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        keyword = update.message.text.strip()
        
        if len(keyword) > 50:
            await update.message.reply_text("❌ الكلمة المفتاحية طويلة جداً")
            return
        
        await update.message.reply_text(f"🔍 جاري تحليل '{keyword}'...")
        
        from ai.trends_engine import fetch_viral_trends
        result = fetch_viral_trends(keyword, 3)
        
        if result.get('top_keywords'):
            trend = result['top_keywords'][0]
            
            response = f"📊 تحليل سريع لـ: {keyword}\\n\\n"
            response += f"🎯 أفضل نتيجة: {trend['keyword']}\\n"
            response += f"📈 النقاط الفيروسية: {trend['viral_score']}%\\n"
            
            from ai.trends_engine import dynamic_pricing_suggestion
            pricing = dynamic_pricing_suggestion(19.99, trend['viral_score'])
            
            response += f"\\n💰 سعر مقترح: ${pricing['suggested_price']:.2f}\\n"
            response += f"📊 التوصية: {pricing.get('recommendation', 'متابعة')}"
            
        else:
            response = f"❌ لم أجد بيانات كافية عن '{keyword}'"
        
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Message handler error: {e}")
        await update.message.reply_text("❌ حدث خطأ في المعالجة")

async def create_bot_application():
    token = os.getenv('TELEGRAM_TOKEN')
    if not token:
        raise ValueError("TELEGRAM_TOKEN not found in environment variables")
    
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("trends", trends_command))
    application.add_handler(CommandHandler("price", price_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    return application

if __name__ == "__main__":
    import asyncio
    
    async def main():
        app = await create_bot_application()
        await app.run_polling()
    
    asyncio.run(main())
"""

# تصدير الوظائف
__all__ = [
    'setup_logging', 'check_environment', 'load_json_config', 'save_json_config',
    'format_currency', 'format_percentage', 'format_timestamp',
    'truncate_text', 'validate_viral_score', 'validate_price',
    'create_directory_structure', 'get_project_info', 
    'quick_log', 'quick_format_result', 'ensure_bot_files'
]