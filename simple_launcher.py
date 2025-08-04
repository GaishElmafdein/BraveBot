#!/usr/bin/env python3
"""
🚀 BraveBot AI Commerce & Trading Empire - Enhanced Launcher
============================================================
تشغيل النظام المتكامل مع الميزات الجديدة
"""

import os
import sys
import time
import asyncio
import threading
import subprocess
import webbrowser
from pathlib import Path
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

class EnhancedBraveBotLauncher:
    def __init__(self):
        self.bot_running = False
        self.dashboard_running = False
        self.services_running = {}
        
    def print_header(self):
        """طباعة رأس البرنامج المحدث"""
        print("\n" + "=" * 70)
        print("🚀 BraveBot AI Commerce & Trading Empire v3.0")
        print("=" * 70)
        print(f"📅 Time: {time.strftime('%H:%M:%S')}")
        print("🧠 AI Engine: [READY]")
        print("💰 Trading Engine: [READY]")
        print("👥 Multi-Account: [READY]")
        print("🚨 Alerts System: [READY]")
        print("=" * 70)
    
    def start_enhanced_bot(self):
        """تشغيل البوت المحسن مع الأوامر الجديدة"""
        print("\n🤖 Starting Enhanced Telegram Bot...")
        
        def run_bot():
            try:
                # استيراد المكتبات
                from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
                from telegram.ext import Application, CommandHandler, CallbackQueryHandler
                
                # استيراد الخدمات الجديدة
                from services.accounts.accounts_manager import AccountsManager
                from services.alerts.alerts_manager import AlertsManager
                
                # تهيئة الخدمات
                accounts_manager = AccountsManager()
                alerts_manager = AlertsManager()
                
                # الحصول على التوكن
                token = os.getenv('TELEGRAM_TOKEN')
                if not token:
                    print("❌ TELEGRAM_TOKEN not found!")
                    return
                
                # إنشاء التطبيق
                app = Application.builder().token(token).build()
                
                # الأوامر الأساسية المحدثة
                async def start_command(update: Update, context):
                    keyboard = [
                        [
                            InlineKeyboardButton("🔥 الترندات الفيروسية", callback_data="viral_trends"),
                            InlineKeyboardButton("💰 حاسبة الربح", callback_data="profit_calc")
                        ],
                        [
                            InlineKeyboardButton("👥 الحسابات", callback_data="accounts"),
                            InlineKeyboardButton("🚨 التنبيهات", callback_data="alerts")
                        ],
                        [
                            InlineKeyboardButton("📈 التداول", callback_data="trading"),
                            InlineKeyboardButton("⚙️ التنفيذ التلقائي", callback_data="auto_exec")
                        ],
                        [
                            InlineKeyboardButton("📊 Dashboard", url="http://localhost:8501")
                        ]
                    ]
                    
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    welcome_text = """
🚀 **BraveBot AI Commerce & Trading Empire v3.0**

مرحباً بك في **النظام الأكثر تطوراً** للتجارة الذكية والتداول! 

**🎯 الميزات الجديدة:**
• 👥 **Multi-Account Support** - إدارة حسابات متعددة
• 🚨 **Advanced Alerts** - تنبيهات ذكية متقدمة  
• 📈 **Trading Module** - تداول العملات والأسهم
• ⚡ **Auto Execution** - تنفيذ تلقائي للصفقات

**💡 اختر من القائمة أدناه للبدء:**
                    """
                    
                    await update.message.reply_text(
                        welcome_text, 
                        parse_mode='Markdown',
                        reply_markup=reply_markup
                    )
                
                # أوامر الحسابات الجديدة
                async def accounts_command(update: Update, context):
                    user_id = str(update.effective_user.id)
                    
                    # جلب حسابات المستخدم
                    amazon_accounts = accounts_manager.get_accounts_by_platform("amazon")
                    ebay_accounts = accounts_manager.get_accounts_by_platform("ebay")
                    trading_accounts = accounts_manager.get_accounts_by_platform("binance")
                    
                    response = "👥 **إدارة الحسابات**\n\n"
                    
                    if amazon_accounts:
                        response += "🛒 **Amazon:**\n"
                        for acc in amazon_accounts[:3]:
                            stats = accounts_manager.get_account_stats(acc.id)
                            response += f"• {acc.name} - استخدام: {stats['total_uses']}\n"
                        response += "\n"
                    
                    if ebay_accounts:
                        response += "🏪 **eBay:**\n"
                        for acc in ebay_accounts[:3]:
                            stats = accounts_manager.get_account_stats(acc.id)
                            response += f"• {acc.name} - نجاح: {stats['success_rate']:.1f}%\n"
                        response += "\n"
                    
                    if trading_accounts:
                        response += "📈 **Trading:**\n"
                        for acc in trading_accounts[:3]:
                            response += f"• {acc.name} - نشط\n"
                        response += "\n"
                    
                    if not (amazon_accounts or ebay_accounts or trading_accounts):
                        response += "⚠️ لا توجد حسابات مضافة\n\n"
                        response += "استخدم `/add_account` لإضافة حساب جديد"
                    else:
                        response += "💡 استخدم `/add_account` لإضافة المزيد"
                    
                    await update.message.reply_text(response, parse_mode='Markdown')
                
                # أوامر التنبيهات
                async def alerts_command(update: Update, context):
                    user_id = str(update.effective_user.id)
                    
                    # جلب التنبيهات غير المقروءة
                    unread_alerts = alerts_manager.get_user_alerts(user_id, unread_only=True)
                    all_alerts = alerts_manager.get_user_alerts(user_id, limit=10)
                    
                    response = "🚨 **نظام التنبيهات**\n\n"
                    
                    if unread_alerts:
                        response += f"🔔 **تنبيهات جديدة ({len(unread_alerts)}):**\n"
                        for alert in unread_alerts[:5]:
                            priority_emoji = {"low": "ℹ️", "medium": "⚠️", "high": "🔥", "critical": "🚨"}
                            response += f"{priority_emoji.get(alert['priority'], '📢')} {alert['title']}\n"
                        response += "\n"
                    
                    response += f"📊 **آخر 5 تنبيهات:**\n"
                    for alert in all_alerts[:5]:
                        read_status = "✅" if alert['is_read'] else "🔴"
                        response += f"{read_status} {alert['title'][:30]}...\n"
                    
                    response += "\n💡 الأوامر:\n"
                    response += "• `/monitor_profit 100` - مراقبة ربح $100\n"
                    response += "• `/monitor_stock PRODUCT_ID` - مراقبة المخزون\n"
                    response += "• `/alerts_settings` - إعدادات التنبيهات"
                    
                    await update.message.reply_text(response, parse_mode='Markdown')
                
                # أوامر التداول الجديدة
                async def trading_command(update: Update, context):
                    response = """
📈 **Trading Intelligence Module**

**🔥 الأوامر المتاحة:**

**تحليل السوق:**
• `/btc` - تحليل Bitcoin
• `/eth` - تحليل Ethereum  
• `/market` - نظرة عامة على السوق
• `/signals` - إشارات التداول

**إدارة المحفظة:**
• `/portfolio` - عرض المحفظة
• `/balance` - الرصيد الحالي
• `/pnl` - الأرباح والخسائر

**التنبيهات:**
• `/set_alert BTC 50000` - تنبيه عند وصول BTC لـ $50,000
• `/whale_alert BTC` - تنبيهات حركة الحيتان

**⚠️ تحذير:** هذا النظام للأغراض التعليمية. استثمر بحذر!
                    """
                    
                    await update.message.reply_text(response, parse_mode='Markdown')
                
                # أوامر التنفيذ التلقائي
                async def auto_exec_command(update: Update, context):
                    response = """
⚡ **Auto Execution System**

**🎯 الوضع الحالي:** تجريبي (يتطلب موافقة يدوية)

**الأوامر المتاحة:**

**Amazon → eBay Flipping:**
• `/flip_product ASIN` - تحليل وتنفيذ Flip
• `/queue` - عرض طلبات التنفيذ المعلقة
• `/approve ORDER_ID` - الموافقة على طلب

**الإعدادات:**
• `/set_max_price 100` - أقصى سعر للشراء
• `/set_profit_margin 30` - هامش ربح 30%
• `/auto_mode on/off` - تفعيل/إلغاء التنفيذ التلقائي

**📊 الإحصائيات:**
• طلبات معلقة: 0
• نجح اليوم: 0  
• إجمالي الربح: $0

⚠️ **تأكد من إعداد حساباتك أولاً!**
                    """
                    
                    await update.message.reply_text(response, parse_mode='Markdown')
                
                # معالج الأزرار التفاعلية
                async def button_handler(update: Update, context):
                    query = update.callback_query
                    await query.answer()
                    
                    if query.data == "viral_trends":
                        await viral_command(update, context)
                    elif query.data == "accounts":
                        await accounts_command(update, context)
                    elif query.data == "alerts":
                        await alerts_command(update, context)
                    elif query.data == "trading":
                        await trading_command(update, context)
                    elif query.data == "auto_exec":
                        await auto_exec_command(update, context)
                
                # الأوامر المحسنة الموجودة
                async def trends_command(update: Update, context):
                    if not context.args:
                        await update.message.reply_text(
                            "🔍 **تحليل الترندات المتقدم**\n\n"
                            "الاستخدام: `/trends <اسم المنتج>`\n"
                            "مثال: `/trends wireless earbuds`\n\n"
                            "**الميزات الجديدة:**\n"
                            "• تحليل المنافسين\n"
                            "• توقعات الأسعار\n"
                            "• تقييم المخاطر\n"
                            "• إشارات الشراء",
                            parse_mode='Markdown'
                        )
                        return
                    
                    keyword = ' '.join(context.args)
                    loading_msg = await update.message.reply_text("🔄 تحليل متقدم جاري...")
                    
                    try:
                        from ai.trends_engine import fetch_viral_trends
                        
                        result = fetch_viral_trends(keyword, 5)
                        
                        if result and result.get('top_keywords'):
                            response = f"🔥 **تحليل متقدم: {keyword}**\n\n"
                            
                            for i, trend in enumerate(result['top_keywords'][:3]):
                                emoji = ["🥇", "🥈", "🥉"][i]
                                response += f"{emoji} **{trend['keyword']}**\n"
                                response += f"🔥 النتيجة الفيروسية: {trend['viral_score']}%\n"
                                response += f"💰 إمكانية الربح: {trend.get('profit_potential', 75)}%\n"
                                response += f"📊 المنافسة: {trend.get('competition', 'متوسطة')}\n"
                                response += f"⚡ إشارة الشراء: {trend.get('buy_signal', 'محايد')}\n\n"
                            
                            # توصيات التنفيذ التلقائي
                            avg_score = result.get('avg_viral_score', 0)
                            if avg_score > 80:
                                response += "🚀 **توصية:** مؤهل للتنفيذ التلقائي!\n"
                                response += f"استخدم `/flip_product` للبدء"
                            elif avg_score > 60:
                                response += "✅ **توصية:** جيد للاستثمار اليدوي"
                            else:
                                response += "⚠️ **توصية:** يحتاج مراقبة إضافية"
                        else:
                            response = f"⚠️ لم أجد ترندات قوية لـ '{keyword}'\n\nجرب كلمات أخرى أو أكثر تحديداً."
                        
                        await loading_msg.edit_text(response, parse_mode='Markdown')
                        
                    except Exception as e:
                        await loading_msg.edit_text(
                            f"❌ خطأ في التحليل: {str(e)}\n\n"
                            "💡 جرب مرة أخرى"
                        )
                
                async def viral_command(update: Update, context):
                    loading_msg = await update.message.reply_text("🔄 البحث عن الفرص الذهبية...")
                    
                    try:
                        from ai.trends_engine import fetch_viral_trends
                        
                        categories = ["electronics", "gaming", "fashion", "home", "sports"]
                        all_results = []
                        
                        for category in categories:
                            result = fetch_viral_trends(category, 2)
                            if result and result.get('top_keywords'):
                                for item in result['top_keywords']:
                                    item['category'] = category
                                all_results.extend(result['top_keywords'])
                        
                        all_results.sort(key=lambda x: x['viral_score'], reverse=True)
                        top_viral = all_results[:7]
                        
                        if top_viral:
                            response = "🔥 **أهم الفرص الاستثمارية:**\n\n"
                            
                            emojis = ["🥇", "🥈", "🥉", "🏅", "⭐", "💎", "🎯"]
                            for i, item in enumerate(top_viral):
                                response += f"{emojis[i]} **{item['keyword']}**\n"
                                response += f"📊 فئة: {item.get('category', 'عام')}\n"
                                response += f"🔥 النتيجة: {item['viral_score']}%\n"
                                response += f"💰 الربح المتوقع: {item.get('profit_potential', 75)}%\n"
                                
                                # إضافة توصية تنفيذ
                                if item['viral_score'] > 85:
                                    response += "🚀 **مؤهل للتنفيذ التلقائي**\n"
                                elif item['viral_score'] > 70:
                                    response += "✅ **فرصة ممتازة**\n"
                                
                                response += "\n"
                            
                            response += "💡 **نصائح:**\n"
                            response += "• 🚀 النتيجة +85%: تنفيذ فوري\n"
                            response += "• ✅ النتيجة +70%: فرصة جيدة\n"
                            response += "• ⚠️ النتيجة -70%: تحتاج بحث\n\n"
                            response += "استخدم `/flip_product` للمنتجات المؤهلة!"
                            
                        else:
                            response = "⚠️ لا توجد فرص قوية حالياً.\nسأعاود البحث خلال 30 دقيقة."
                        
                        await loading_msg.edit_text(response, parse_mode='Markdown')
                        
                    except Exception as e:
                        await loading_msg.edit_text(f"❌ خطأ في البحث: {str(e)}")
                
                # أوامر التداول الفعلية
                async def btc_command(update: Update, context):
                    loading_msg = await update.message.reply_text("🔄 تحليل Bitcoin...")
                    
                    try:
                        from services.trading.trading_engine import TradingEngine, AssetType
                        trading_engine = TradingEngine()
                        
                        # تحليل BTC
                        signal = await trading_engine.analyze_asset("BTC", AssetType.CRYPTO)
                        market_data = await trading_engine.get_crypto_price("BTC")
                        
                        if signal and market_data:
                            signal_emoji = {
                                "buy": "🟢",
                                "strong_buy": "🚀",
                                "sell": "🔴", 
                                "strong_sell": "💥",
                                "hold": "🟡"
                            }
                            
                            response = f"""
📈 **Bitcoin (BTC) Analysis**

💰 **السعر الحالي:** ${market_data.price:,.2f}
📊 **التغيير 24ساعة:** {market_data.change_percent_24h:+.2f}%
📈 **الأعلى:** ${market_data.high_24h:,.2f}
📉 **الأدنى:** ${market_data.low_24h:,.2f}

{signal_emoji.get(signal.signal.value, '📊')} **الإشارة:** {signal.signal.value.upper()}
🎯 **مستوى الثقة:** {signal.confidence:.1f}%

**📋 أسباب التحليل:**
"""
                            for reason in signal.reasons:
                                response += f"• {reason}\n"
                            
                            if signal.target_price:
                                response += f"\n🎯 **السعر المستهدف:** ${signal.target_price:,.2f}"
                            if signal.stop_loss:
                                response += f"\n🛑 **وقف الخسارة:** ${signal.stop_loss:,.2f}"
                            
                            response += f"\n\n⏰ **آخر تحديث:** {signal.timestamp.strftime('%H:%M')}"
                            
                        else:
                            response = "❌ فشل في تحليل Bitcoin. حاول مرة أخرى."
                        
                        await loading_msg.edit_text(response, parse_mode='Markdown')
                        
                    except Exception as e:
                        await loading_msg.edit_text(f"❌ خطأ في التحليل: {str(e)}")
                
                async def eth_command(update: Update, context):
                    loading_msg = await update.message.reply_text("🔄 تحليل Ethereum...")
                    
                    try:
                        from services.trading.trading_engine import TradingEngine, AssetType
                        trading_engine = TradingEngine()
                        
                        signal = await trading_engine.analyze_asset("ETH", AssetType.CRYPTO)
                        market_data = await trading_engine.get_crypto_price("ETH")
                        
                        if signal and market_data:
                            signal_emoji = {
                                "buy": "🟢", "strong_buy": "🚀", "sell": "🔴", 
                                "strong_sell": "💥", "hold": "🟡"
                            }
                            
                            response = f"""
🔷 **Ethereum (ETH) Analysis**

💰 **السعر:** ${market_data.price:,.2f}
📊 **24ساعة:** {market_data.change_percent_24h:+.2f}%

{signal_emoji.get(signal.signal.value, '📊')} **الإشارة:** {signal.signal.value.upper()}
🎯 **الثقة:** {signal.confidence:.1f}%

**تحليل:**
"""
                            for reason in signal.reasons[:3]:
                                response += f"• {reason}\n"
                            
                            if signal.target_price:
                                response += f"\n🎯 الهدف: ${signal.target_price:,.2f}"
                            if signal.stop_loss:
                                response += f"\n🛑 وقف الخسارة: ${signal.stop_loss:,.2f}"
                            
                        else:
                            response = "❌ فشل في تحليل Ethereum"
                        
                        await loading_msg.edit_text(response, parse_mode='Markdown')
                        
                    except Exception as e:
                        await loading_msg.edit_text(f"❌ خطأ: {str(e)}")
                
                async def market_command(update: Update, context):
                    loading_msg = await update.message.reply_text("🔄 تحديث السوق...")
                    
                    try:
                        from services.trading.trading_engine import TradingEngine
                        trading_engine = TradingEngine()
                        
                        market_overview = await trading_engine.get_market_overview()
                        
                        if 'error' not in market_overview:
                            response = "📊 **نظرة عامة على السوق**\n\n"
                            
                            # العملات المشفرة
                            response += "🔷 **العملات المشفرة:**\n"
                            for crypto in market_overview.get('crypto', []):
                                change_emoji = "🟢" if crypto['change_24h'] > 0 else "🔴"
                                response += f"{change_emoji} {crypto['symbol']}: ${crypto['price']:,.2f} ({crypto['change_24h']:+.1f}%)\n"
                            
                            # الأسهم
                            response += "\n📈 **الأسهم:**\n"
                            for stock in market_overview.get('stocks', []):
                                change_emoji = "🟢" if stock['change_24h'] > 0 else "🔴"  
                                response += f"{change_emoji} {stock['symbol']}: ${stock['price']:,.2f} ({stock['change_24h']:+.1f}%)\n"
                            

                            response += f"\n⏰ آخر تحديث: {datetime.now().strftime('%H:%M')}"  
                        else:
                            response = "❌ فشل في جلب بيانات السوق"
                        
                        await loading_msg.edit_text(response, parse_mode='Markdown')
                        
                    except Exception as e:
                        await loading_msg.edit_text(f"❌ خطأ: {str(e)}")
                
                async def signals_command(update: Update, context):
                    loading_msg = await update.message.reply_text("🔄 تحليل إشارات متعددة...")
                    
                    try:
                        from services.trading.trading_engine import TradingEngine, AssetType
                        trading_engine = TradingEngine()
                        
                        # تحليل عدة أصول
                        assets = [
                            ("BTC", AssetType.CRYPTO),
                            ("ETH", AssetType.CRYPTO),
                            ("AAPL", AssetType.STOCK),
                            ("TSLA", AssetType.STOCK)
                        ]
                        
                        response = "🎯 **إشارات التداول**\n\n"
                        
                        for symbol, asset_type in assets:
                            signal = await trading_engine.analyze_asset(symbol, asset_type)
                            if signal:
                                signal_emoji = {
                                    "buy": "🟢", "strong_buy": "🚀", "sell": "🔴",
                                    "strong_sell": "💥", "hold": "🟡"
                                }
                                
                                emoji = signal_emoji.get(signal.signal.value, '📊')
                                response += f"{emoji} **{symbol}**: {signal.signal.value} ({signal.confidence:.0f}%)\n"
                            
                            await asyncio.sleep(1)  # تجنب rate limiting
                        
                        response += "\n💡 **نصائح:**\n"
                        response += "• 🚀 Strong Buy: إشارة قوية للشراء\n"
                        response += "• 🟢 Buy: إشارة شراء جيدة\n"
                        response += "• 🟡 Hold: الاحتفاظ بالوضع الحالي\n"
                        response += "• 🔴 Sell: إشارة بيع\n"
                        response += "• 💥 Strong Sell: إشارة بيع قوية\n\n"
                        response += "⚠️ **تحذير:** هذه إشارات تعليمية فقط"
                        
                        await loading_msg.edit_text(response, parse_mode='Markdown')
                        
                    except Exception as e:
                        await loading_msg.edit_text(f"❌ خطأ: {str(e)}")

                # إضافة المعالجات الجديدة
                app.add_handler(CommandHandler("btc", btc_command))
                app.add_handler(CommandHandler("eth", eth_command))
                app.add_handler(CommandHandler("market", market_command))
                app.add_handler(CommandHandler("signals", signals_command))
                
                # إضافة جميع المعالجات
                app.add_handler(CommandHandler("start", start_command))
                app.add_handler(CommandHandler("trends", trends_command))
                app.add_handler(CommandHandler("viral", viral_command))
                app.add_handler(CommandHandler("accounts", accounts_command))
                app.add_handler(CommandHandler("alerts", alerts_command))
                app.add_handler(CommandHandler("trading", trading_command))
                app.add_handler(CommandHandler("autoexec", auto_exec_command))
                app.add_handler(CallbackQueryHandler(button_handler))
                
                print("✅ Enhanced Bot handlers loaded!")
                
                # تشغيل البوت
                async def main():
                    async with app:
                        await app.start()
                        print("🚀 Enhanced BraveBot is running...")
                        print("📱 Send /start to explore new features!")
                        await app.updater.start_polling(drop_pending_updates=True)
                        await asyncio.Event().wait()
                
                asyncio.run(main())
                
            except Exception as e:
                print(f"❌ Enhanced Bot error: {e}")
                self.bot_running = False
        
        # تشغيل في thread منفصل
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        self.bot_running = True
        
        print("✅ Enhanced Bot thread started")
        time.sleep(3)
    
    def start_services(self):
        """تشغيل الخدمات الإضافية"""
        print("\n⚙️ Starting Additional Services...")
        
        # تشغيل نظام التنبيهات
        def run_alerts_service():
            try:
                from services.alerts.alerts_manager import AlertsManager
                alerts_manager = AlertsManager()
                
                print("🚨 Alerts service started")
                # الخدمة تعمل في الخلفية
                
            except Exception as e:
                print(f"❌ Alerts service error: {e}")
        
        alerts_thread = threading.Thread(target=run_alerts_service, daemon=True)
        alerts_thread.start()
        self.services_running['alerts'] = True
        
        print("✅ Additional services started")
    
    def run_enhanced_system(self):
        """تشغيل النظام المحسن الكامل"""
        self.print_header()
        
        print("\n🚀 Starting Enhanced Complete System...")
        print("-" * 50)
        
        # تشغيل الخدمات الإضافية
        self.start_services()
        
        # تشغيل البوت المحسن
        self.start_enhanced_bot()
        
        # تشغيل Dashboard (نفس الطريقة السابقة)
        self.start_dashboard()
        
        print("\n" + "=" * 70)
        print("🎉 BraveBot AI Commerce & Trading Empire Running!")
        print("=" * 70)
        print("🤖 Enhanced Telegram Bot: Active")
        print("📊 Dashboard: http://localhost:8501")
        print("🧠 AI Engine: Ready")
        print("💰 Trading Engine: Ready")
        print("👥 Multi-Account: Ready")
        print("🚨 Alerts System: Ready")
        print("⚡ Auto Execution: Standby")
        print("=" * 70)
        print("\n💡 New Features:")
        print("• Multi-platform account management")
        print("• Advanced alert system with monitoring")
        print("• Trading signals for crypto & stocks")
        print("• Automated execution with approval queue")
        print("• Enhanced profit calculations")
        print("\n📱 Telegram Bot Commands:")
        print("• /start - المتش الرئيسية التفاعلية")
        print("• /accounts - إدارة الحسابات")
        print("• /alerts - نظام التنبيهات")
        print("• /trading - وحدة التداول")
        print("• /autoexec - التنفيذ التلقائي")
        print("\n⏹️  Press Ctrl+C to stop all services")
        
        try:
            while True:
                time.sleep(10)
                if not self.bot_running and not self.dashboard_running:
                    print("⚠️ All services stopped")
                    break
                    
        except KeyboardInterrupt:
            print("\n⏹️ Stopping Enhanced BraveBot...")
            print("✅ All services stopped")
    
    def start_dashboard(self):
        """تشغيل Dashboard (نفس الدالة السابقة)"""
        print("\n📊 Starting Dashboard...")
        
        def run_dashboard():
            try:
                cmd = [
                    sys.executable, "-m", "streamlit", "run", 
                    "dashboard/app.py",
                    "--server.port", "8501",
                    "--server.headless", "true"
                ]
                
                print(f"🚀 Running: {' '.join(cmd)}")
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                time.sleep(3)
                
                if process.poll() is None:
                    print("✅ Dashboard started!")
                    
                    try:
                        webbrowser.open("http://localhost:8501")
                        print("🌐 Browser opened!")
                    except:
                        pass
                    
                    process.wait()
                else:
                    stdout, stderr = process.communicate()
                    print(f"❌ Dashboard failed: {stderr.decode()}")
                
            except Exception as e:
                print(f"❌ Dashboard error: {e}")
        
        dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
        dashboard_thread.start()
        self.dashboard_running = True
        
        print("✅ Dashboard thread started")
        time.sleep(2)

def main():
    """الدالة الرئيسية المحسنة"""
    try:
        launcher = EnhancedBraveBotLauncher()
        launcher.run_enhanced_system()
        
    except KeyboardInterrupt:
        print("\n⏹️ Enhanced BraveBot stopped by user")
    except Exception as e:
        print(f"❌ Enhanced Launcher error: {e}")

if __name__ == "__main__":
    main()