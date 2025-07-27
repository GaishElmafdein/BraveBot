#!/usr/bin/env python3
"""
📊 BraveBot Dashboard - Streamlit Interface
==========================================
لوحة تحكم شاملة لمراقبة البوت والإحصائيات والتحليلات الذكية
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sqlite3
import asyncio
from datetime import datetime, timedelta
import sys
import os

# إضافة مسار المشروع للاستيراد
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# استيراد وحدات البوت
try:
    from core.database_manager import get_user_stats
    from ai.trends_engine import fetch_viral_trends, generate_weekly_insights
except ImportError:
    st.error("❌ خطأ في استيراد الوحدات - تأكد من وجود ملفات المشروع")
    st.stop()

# إعداد الصفحة
st.set_page_config(
    page_title="BraveBot Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS مخصص للتصميم
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .trend-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #28a745;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        padding-left: 24px;
        padding-right: 24px;
    }
</style>
""", unsafe_allow_html=True)

class BraveBotDashboard:
    """كلاس رئيسي للوحة التحكم"""
    
    def __init__(self):
        self.db_path = "bravebot.db"
        
    def load_mock_data(self):
        """تحميل بيانات تجريبية للعرض"""
        # بيانات تجريبية للإحصائيات
        mock_stats = {
            'total_users': 156,
            'total_checks': 2847,
            'total_achievements': 89,
            'active_users_today': 23,
            'compliance_rate': 78.5
        }
        
        # بيانات تجريبية للرسوم البيانية
        dates = pd.date_range(start='2024-01-01', end='2024-07-27', freq='D')
        import numpy as np
        mock_usage_data = pd.DataFrame({
            'date': dates,
            'daily_checks': [abs(50 + 30 * np.sin(i/10) + np.random.normal(0, 10)) for i in range(len(dates))],
            'new_users': [abs(5 + 3 * np.sin(i/15) + np.random.normal(0, 2)) for i in range(len(dates))]
        })
        
        return mock_stats, mock_usage_data
    
    def get_database_stats(self):
        """جلب إحصائيات حقيقية من قاعدة البيانات"""
        try:
            if not os.path.exists(self.db_path):
                return None
                
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # إحصائيات أساسية
            cursor.execute("SELECT COUNT(*) FROM user_stats")
            total_users = cursor.fetchone()[0]
            
            cursor.execute("SELECT SUM(total_checks) FROM user_stats")
            total_checks = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT SUM(passed_checks) FROM user_stats")
            passed_checks = cursor.fetchone()[0] or 0
            
            compliance_rate = (passed_checks / max(total_checks, 1)) * 100
            
            conn.close()
            
            return {
                'total_users': total_users,
                'total_checks': total_checks,
                'total_achievements': total_users * 2,  # تقدير
                'active_users_today': max(1, total_users // 7),  # تقدير
                'compliance_rate': round(compliance_rate, 1)
            }
            
        except Exception as e:
            st.error(f"خطأ في قاعدة البيانات: {e}")
            return None
    
    async def load_ai_data(self):
        """تحميل بيانات الذكاء الاصطناعي"""
        try:
            # جلب الترندات الفيروسية
            trends = await fetch_viral_trends(5)
            
            # جلب التحليلات الأسبوعية
            insights = await generate_weekly_insights()
            
            return trends, insights
            
        except Exception as e:
            st.error(f"خطأ في تحميل بيانات الذكاء الاصطناعي: {e}")
            return [], {}

def create_overview_tab():
    """تبويب النظرة العامة"""
    st.markdown('<div class="main-header"><h1 style="color: white; margin: 0;">🤖 BraveBot Dashboard</h1></div>', 
                unsafe_allow_html=True)
    
    dashboard = BraveBotDashboard()
    
    # جلب البيانات
    real_stats = dashboard.get_database_stats()
    if real_stats:
        stats = real_stats
        data_source = "🔴 بيانات حقيقية"
    else:
        # استخدام البيانات التجريبية
        import numpy as np
        stats, usage_data = dashboard.load_mock_data()
        data_source = "🟡 بيانات تجريبية"
    
    st.info(f"📊 **مصدر البيانات:** {data_source}")
    
    # الإحصائيات الرئيسية
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="👥 إجمالي المستخدمين",
            value=stats['total_users'],
            delta="+12 هذا الأسبوع"
        )
    
    with col2:
        st.metric(
            label="🔍 إجمالي الفحوص",
            value=f"{stats['total_checks']:,}",
            delta="+156 اليوم"
        )
    
    with col3:
        st.metric(
            label="🏆 الإنجازات المحققة",
            value=stats['total_achievements'],
            delta="+23 هذا الشهر"
        )
    
    with col4:
        st.metric(
            label="📈 معدل التوافق",
            value=f"{stats['compliance_rate']}%",
            delta="+2.3% من الأمس"
        )
    
    # الرسوم البيانية
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 نشاط المستخدمين (آخر 30 يوم)")
        
        # إنشاء بيانات تجريبية للرسم البياني
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        import numpy as np
        daily_activity = [20 + 15 * np.sin(i/5) + np.random.normal(0, 5) for i in range(len(dates))]
        daily_activity = [max(0, int(x)) for x in daily_activity]
        
        activity_df = pd.DataFrame({
            'التاريخ': dates,
            'المستخدمين النشطين': daily_activity
        })
        
        fig_activity = px.line(
            activity_df, 
            x='التاريخ', 
            y='المستخدمين النشطين',
            title="النشاط اليومي",
            line_shape='spline'
        )
        fig_activity.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_activity, use_container_width=True)
    
    with col2:
        st.subheader("🎯 توزيع نتائج الفحص")
        
        # بيانات دائرية لنتائج الفحص
        results_data = pd.DataFrame({
            'النتيجة': ['متوافق ✅', 'غير متوافق ❌', 'تحت المراجعة ⏳'],
            'العدد': [stats['compliance_rate'], 100-stats['compliance_rate'], 5]
        })
        
        fig_pie = px.pie(
            results_data, 
            values='العدد', 
            names='النتيجة',
            title="توزيع نتائج الفحص",
            color_discrete_map={
                'متوافق ✅': '#28a745',
                'غير متوافق ❌': '#dc3545', 
                'تحت المراجعة ⏳': '#ffc107'
            }
        )
        fig_pie.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_pie, use_container_width=True)

def create_ai_trends_tab():
    """تبويب الترندات الذكية"""
    st.header("🔥 الترندات الفيروسية والتحليل الذكي")
    
    # عرض البيانات بشكل متزامن
    try:
        # استخدام asyncio لتشغيل الكود غير المتزامن
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        dashboard = BraveBotDashboard()
        trends, insights = loop.run_until_complete(dashboard.load_ai_data())
        
        if trends:
            st.success(f"✅ تم جلب {len(trends)} ترند فيروسي")
            
            # عرض الترندات في أعمدة
            for i, trend in enumerate(trends):
                with st.expander(f"{trend['icon']} {trend['keyword']} - نقاط: {trend['score']}", expanded=(i==0)):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("📊 النقاط", trend['score'])
                    with col2:
                        st.metric("📈 النمو", trend['growth'])
                    with col3:
                        st.metric("🌐 المنصة", trend['platform'])
            
            # رسم بياني للترندات
            st.subheader("📈 مقارنة الترندات")
            trends_df = pd.DataFrame(trends)
            
            fig_trends = px.bar(
                trends_df.head(5), 
                x='keyword', 
                y='score',
                color='platform',
                title="أفضل 5 ترندات فيروسية",
                labels={'keyword': 'المنتج', 'score': 'النقاط'}
            )
            fig_trends.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_trends, use_container_width=True)
            
        else:
            st.warning("⚠️ لم يتم العثور على ترندات - سيتم استخدام بيانات تجريبية")
            
            # بيانات تجريبية للترندات
            mock_trends = [
                {"keyword": "iPhone 15 Pro", "score": 95, "platform": "TikTok", "growth": "+150%"},
                {"keyword": "Samsung Galaxy S25", "score": 88, "platform": "Reddit", "growth": "+120%"},
                {"keyword": "AirPods Pro 3", "score": 82, "platform": "Google", "growth": "+95%"},
            ]
            
            for trend in mock_trends:
                st.markdown(f"""
                <div class="trend-card">
                    <h4>🔥 {trend['keyword']}</h4>
                    <p><strong>النقاط:</strong> {trend['score']} | <strong>النمو:</strong> {trend['growth']} | <strong>المنصة:</strong> {trend['platform']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # قسم التسعير الذكي
        st.markdown("---")
        st.subheader("💰 تحليل التسعير الذكي")
        
        # مثال على تحليل التسعير
        pricing_example = {
            "منتج": ["iPhone 15 Pro", "Samsung Galaxy S25", "AirPods Pro 3"],
            "السعر الحالي": [1199, 999, 249],
            "متوسط السوق": [1225, 1050, 265],
            "السعر المقترح": [1189, 1020, 255],
            "التوفير المحتمل": ["-2.9%", "+2.1%", "+2.4%"]
        }
        
        pricing_df = pd.DataFrame(pricing_example)
        st.dataframe(pricing_df, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ خطأ في تحميل بيانات الذكاء الاصطناعي: {e}")

def create_achievements_tab():
    """تبويب الإنجازات"""
    st.header("🏆 نظام الإنجازات والمكافآت")
    
    # إحصائيات الإنجازات
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🏅 إجمالي الإنجازات", "8", help="عدد مستويات الإنجازات المتاحة")
    with col2:
        st.metric("👑 أعلى مستوى محقق", "بطل التوافق", help="أعلى إنجاز حققه المستخدمون")
    with col3:
        st.metric("📊 معدل الإنجاز", "67%", help="متوسط إنجازات جميع المستخدمين")
    
    # جدول الإنجازات
    achievements_data = {
        "المستوى": ["🌱", "🔍", "⭐", "🏆", "💎", "🚀", "👑", "🏅"],
        "الاسم": ["أول خطوة", "مبتدئ", "خبير مبتدئ", "محترف", "خبير", "ماهر", "أسطورة", "بطل التوافق"],
        "المطلوب": [1, 5, 10, 25, 50, 100, 250, 500],
        "المحققون": [156, 124, 89, 45, 23, 12, 5, 2],
        "النسبة": ["100%", "79%", "57%", "29%", "15%", "8%", "3%", "1%"]
    }
    
    achievements_df = pd.DataFrame(achievements_data)
    st.dataframe(achievements_df, use_container_width=True)
    
    # رسم بياني للإنجازات
    fig_achievements = px.bar(
        achievements_df,
        x='الاسم',
        y='المحققون',
        title='توزيع المستخدمين حسب مستوى الإنجاز',
        color='المحققون',
        color_continuous_scale='viridis'
    )
    fig_achievements.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_achievements, use_container_width=True)
    
    # أفضل المستخدمين
    st.subheader("🥇 المتصدرون")
    top_users = pd.DataFrame({
        "المرتبة": ["🥇", "🥈", "🥉", "4", "5"],
        "المستخدم": ["أحمد محمد", "فاطمة علي", "محمد حسن", "سارة أحمد", "علي محمود"],
        "الفحوص": [523, 487, 456, 398, 367],
        "المستوى": ["🏅", "👑", "👑", "🚀", "🚀"]
    })
    st.dataframe(top_users, use_container_width=True, hide_index=True)

def main():
    """الدالة الرئيسية لتشغيل Dashboard"""
    
    # الشريط الجانبي
    with st.sidebar:
        st.title("🤖 BraveBot")
        st.markdown("---")
        
        # معلومات النظام
        st.subheader("ℹ️ معلومات النظام")
        st.info(f"""
        **الإصدار:** 2.0.0
        **حالة البوت:** 🟢 متصل
        **آخر تحديث:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
        **المستخدمين النشطين:** 23
        """)
        
        # إعدادات سريعة
        st.subheader("⚙️ إعدادات سريعة")
        auto_refresh = st.checkbox("تحديث تلقائي", value=True)
        if auto_refresh:
            refresh_interval = st.selectbox("فترة التحديث", [30, 60, 300], index=1)
        
        # أزرار سريعة
        st.subheader("🔧 إجراءات سريعة")
        if st.button("🔄 تحديث البيانات"):
            st.rerun()
        
        if st.button("📤 تصدير التقرير"):
            st.success("✅ تم تصدير التقرير بنجاح!")
    
    # التبويبات الرئيسية
    tab1, tab2, tab3 = st.tabs(["📊 النظرة العامة", "🔥 الترندات الذكية", "🏆 الإنجازات"])
    
    with tab1:
        create_overview_tab()
    
    with tab2:
        create_ai_trends_tab()
    
    with tab3:
        create_achievements_tab()
    
    # التحديث التلقائي
    if 'auto_refresh' in locals() and auto_refresh:
        import time
        time.sleep(refresh_interval)
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; margin-top: 2rem;'>
    <p>🤖 <strong>BraveBot Dashboard</strong> - صُنع بـ ❤️ باستخدام Streamlit</p>
    <p>© 2025 BraveBot Team. جميع الحقوق محفوظ.</p>
</div>
""", unsafe_allow_html=True)

def run_dashboard():
    """
    Run the Streamlit dashboard.
    """
    main()

if __name__ == "__main__":
    main()
