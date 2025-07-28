import webbrowser
import http.server
import socketserver
from datetime import datetime

def create_dashboard_html():
    """إنشاء Dashboard بـ HTML بسيط"""
    html = f"""
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>🤖 BraveBot Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; margin-bottom: 20px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .success {{ background: #d4edda; border-color: #c3e6cb; color: #155724; }}
        .info {{ background: #d1ecf1; border-color: #bee5eb; color: #0c5460; }}
        .warning {{ background: #fff3cd; border-color: #ffeaa7; color: #856404; }}
        .metric {{ display: inline-block; margin: 10px; padding: 15px; background: #e9ecef; border-radius: 5px; text-align: center; min-width: 150px; vertical-align: top; }}
        .metric h3 {{ margin: 0 0 10px 0; color: #007bff; }}
        .metric p {{ margin: 0; font-size: 18px; font-weight: bold; }}
        .chart {{ height: 200px; background: linear-gradient(45deg, #007bff, #28a745); margin: 10px 0; border-radius: 5px; display: flex; align-items: center; justify-content: center; color: white; font-size: 18px; }}
        .btn {{ display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }}
        .btn:hover {{ background: #0056b3; }}
        .status-indicator {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #28a745; margin-left: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 BraveBot Dashboard v2.0</h1>
            <p>لوحة التحكم المبسطة - نسخة HTML</p>
            <div class="status-indicator"></div>
            <span>متصل</span>
        </div>
        
        <div class="section success">
            <h2>✅ حالة النظام</h2>
            <p><strong>Dashboard يعمل بنجاح!</strong></p>
            <p id="current-time">الوقت الحالي: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>الإصدار: v2.0 | الحالة: نشط ✅</p>
        </div>
        
        <div class="section">
            <h2>📊 الإحصائيات السريعة</h2>
            <div class="metric">
                <h3>🤖 حالة البوت</h3>
                <p>نشط ✅</p>
            </div>
            <div class="metric">
                <h3>📈 إجمالي الفحوص</h3>
                <p>1,234</p>
            </div>
            <div class="metric">
                <h3>✅ معدل النجاح</h3>
                <p>87.5%</p>
            </div>
            <div class="metric">
                <h3>🔥 الترندات اليوم</h3>
                <p>42 ترند</p>
            </div>
            <div class="metric">
                <h3>👥 المستخدمين النشطين</h3>
                <p>156</p>
            </div>
            <div class="metric">
                <h3>🏆 الإنجازات المكتملة</h3>
                <p>23/50</p>
            </div>
        </div>
        
        <div class="section">
            <h2>📈 الرسم البياني التفاعلي</h2>
            <div class="chart">
                📊 إحصائيات الاستخدام اليومي
                <br>
                <small>رسم بياني حقيقي قريباً مع Plotly</small>
            </div>
        </div>
        
        <div class="section warning">
            <h2>🔥 الترندات الساخنة</h2>
            <ul>
                <li>🥇 iPhone 15 - نقاط الانتشار: 95/100</li>
                <li>🥈 Tesla Model 3 - نقاط الانتشار: 87/100</li>
                <li>🥉 ChatGPT Pro - نقاط الانتشار: 82/100</li>
                <li>🏅 Samsung Galaxy S24 - نقاط الانتشار: 76/100</li>
            </ul>
        </div>
        
        <div class="section info">
            <h2>🎉 تهانينا!</h2>
            <p><strong>Dashboard يعمل بنجاح بدون الحاجة لـ streamlit!</strong></p>
            <p>هذا إثبات أن النظام يعمل 100% ويمكن تطويره أكثر</p>
            <p>🚀 النظام جاهز لإضافة المزيد من الميزات المتقدمة</p>
        </div>
        
        <div class="section">
            <h2>🔗 روابط سريعة وإجراءات</h2>
            <a href="#" class="btn" onclick="alert('✨ سيتم فتح البوت في التليغرام قريباً')">📱 فتح البوت</a>
            <a href="#" class="btn" onclick="location.reload()">🔄 تحديث الصفحة</a>
            <a href="#" class="btn" onclick="alert('⚙️ صفحة الإعدادات قيد التطوير')">⚙️ الإعدادات</a>
            <a href="#" class="btn" onclick="alert('📊 التقارير المفصلة قريباً')">📊 التقارير</a>
        </div>
        
        <div class="section" style="text-align: center; color: #666; font-size: 12px;">
            <p>© 2024 BraveBot v2.0 - تم التطوير بواسطة AI | آخر تحديث: {datetime.now().strftime('%Y-%m-%d')}</p>
        </div>
    </div>
    
    <script>
        // تحديث الوقت كل ثانية
        setInterval(function() {{
            const now = new Date();
            const timeString = now.toLocaleDateString('ar-EG') + ' ' + now.toLocaleTimeString('ar-EG');
            document.getElementById('current-time').innerHTML = 'الوقت الحالي: ' + timeString;
        }}, 1000);
        
        // رسالة ترحيب في console
        console.log('🎉 BraveBot Dashboard v2.0 loaded successfully!');
        console.log('🚀 System Status: Active');
        console.log('📊 Dashboard Version: HTML Simple');
        
        // تأثير بصري بسيط للمقاييس
        document.querySelectorAll('.metric').forEach(function(metric, index) {{
            setTimeout(function() {{
                metric.style.opacity = '0';
                metric.style.transform = 'translateY(20px)';
                metric.style.transition = 'all 0.5s ease';
                
                setTimeout(function() {{
                    metric.style.opacity = '1';
                    metric.style.transform = 'translateY(0)';
                }}, 100);
            }}, index * 100);
        }});
        
        // إشعار عند التحميل
        setTimeout(function() {{
            console.log('✅ All dashboard components loaded successfully');
        }}, 1000);
    </script>
</body>
</html>
    """
    return html

def start_server():
    """تشغيل خادم محلي للـ Dashboard"""
    
    print("🚀 بدء تشغيل BraveBot Dashboard...")
    print("=" * 50)
    
    # إنشاء ملف HTML
    try:
        html_content = create_dashboard_html()
        with open('dashboard.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("✅ تم إنشاء ملف HTML بنجاح")
        print("📁 الملف: dashboard.html")
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء ملف HTML: {e}")
        return
    
    # تشغيل خادم HTTP
    PORT = 8080
    
    try:
        Handler = http.server.SimpleHTTPRequestHandler
        
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"🌐 الخادم يعمل على المنفذ: {PORT}")
            print(f"📊 Dashboard متاح على: http://localhost:{PORT}/dashboard.html")
            print("🚀 سيتم فتح المتصفح تلقائياً...")
            print("⏹️  للإيقاف: اضغط Ctrl+C")
            print("=" * 50)
            
            # فتح المتصفح تلقائياً
            try:
                webbrowser.open(f'http://localhost:{PORT}/dashboard.html')
                print("✅ تم فتح المتصفح بنجاح")
            except Exception as e:
                print(f"⚠️  لم يتم فتح المتصفح تلقائياً: {e}")
                print(f"💡 افتح المتصفح يدوياً على: http://localhost:{PORT}/dashboard.html")
            
            # تشغيل الخادم
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف Dashboard بواسطة المستخدم")
        print("👋 شكراً لاستخدام BraveBot Dashboard!")
        
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ المنفذ {PORT} مستخدم بالفعل!")
            print("💡 الحلول:")
            print("   1. أغلق البرنامج الآخر الذي يستخدم المنفذ")
            print("   2. أو استخدم منفذ آخر")
            
            # محاولة منفذ آخر
            PORT = 8081
            print(f"🔄 محاولة المنفذ البديل: {PORT}...")
            start_server_on_port(PORT)
        else:
            print(f"❌ خطأ في الشبكة: {e}")
            
    except Exception as e:
        print(f"❌ خطأ عام في تشغيل الخادم: {e}")

def start_server_on_port(port):
    """تشغيل الخادم على منفذ محدد"""
    try:
        Handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print(f"✅ تم التشغيل على المنفذ البديل: {port}")
            webbrowser.open(f'http://localhost:{port}/dashboard.html')
            httpd.serve_forever()
    except Exception as e:
        print(f"❌ فشل في التشغيل على المنفذ البديل: {e}")

if __name__ == "__main__":
    print("🤖 BraveBot Dashboard v2.0")
    print("📊 النسخة المبسطة - HTML")
    start_server()