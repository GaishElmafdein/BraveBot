#!/usr/bin/env python3
"""
📄 PDF Report Generator
=======================
مولد التقارير الأسبوعية بصيغة PDF
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime, timedelta
import io
import base64
from pathlib import Path
import logging

# إعداد اللوغ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFReportGenerator:
    """مولد تقارير PDF الأسبوعية"""
    
    def __init__(self, output_dir: str = "reports/weekly"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # إعداد الخطوط العربية
        self.styles = getSampleStyleSheet()
        self._setup_arabic_styles()
    
    def _setup_arabic_styles(self):
        """إعداد أنماط الخط العربي"""
        
        # تعريف أنماط جديدة
        self.arabic_title = ParagraphStyle(
            'ArabicTitle',
            parent=self.styles['Title'],
            fontName='Helvetica-Bold',
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        self.arabic_heading = ParagraphStyle(
            'ArabicHeading',
            parent=self.styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=14,
            alignment=TA_RIGHT,
            spaceAfter=12
        )
        
        self.arabic_normal = ParagraphStyle(
            'ArabicNormal',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            alignment=TA_RIGHT,
            spaceAfter=6
        )
    
    def generate_weekly_report(self, user_data: dict, trends_data: list, 
                             price_data: dict = None) -> str:
        """توليد التقرير الأسبوعي"""
        
        user_id = user_data.get('user_id', 'unknown')
        report_date = datetime.now().strftime('%Y-%m-%d')
        filename = f"weekly_report_{user_id}_{report_date}.pdf"
        filepath = self.output_dir / filename
        
        # إنشاء المستند
        doc = SimpleDocTemplate(str(filepath), pagesize=A4)
        story = []
        
        # العنوان الرئيسي
        title = Paragraph("🤖 BraveBot - التقرير الأسبوعي", self.arabic_title)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # معلومات المستخدم
        story.extend(self._create_user_section(user_data))
        
        # ملخص الترندات
        story.extend(self._create_trends_summary(trends_data))
        
        # تحليل الأسعار (إذا كان متاحاً)
        if price_data:
            story.extend(self._create_price_analysis(price_data))
        
        # التوصيات الشخصية
        story.extend(self._create_recommendations_section(user_data, trends_data))
        
        # الرسوم البيانية
        story.extend(self._create_charts_section(trends_data))
        
        # الخاتمة
        story.extend(self._create_footer_section())
        
        # بناء المستند
        doc.build(story)
        
        logger.info(f"تم إنشاء التقرير: {filepath}")
        return str(filepath)
    
    def _create_user_section(self, user_data: dict) -> list:
        """قسم معلومات المستخدم"""
        
        elements = []
        
        # عنوان القسم
        heading = Paragraph("📊 معلومات المستخدم", self.arabic_heading)
        elements.append(heading)
        
        # جدول المعلومات
        user_info = [
            ['الاسم', user_data.get('name', 'غير محدد')],
            ['تاريخ التقرير', datetime.now().strftime('%d/%m/%Y')],
            ['الاهتمامات', ', '.join(user_data.get('interests', []))],
            ['إجمالي التفاعلات', str(user_data.get('total_interactions', 0))]
        ]
        
        table = Table(user_info, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_trends_summary(self, trends_data: list) -> list:
        """ملخص الترندات"""
        
        elements = []
        
        heading = Paragraph("🔥 ملخص الترندات الأسبوعي", self.arabic_heading)
        elements.append(heading)
        
        if not trends_data:
            no_data = Paragraph("لا توجد بيانات ترندات متاحة", self.arabic_normal)
            elements.append(no_data)
            elements.append(Spacer(1, 20))
            return elements
        
        # أفضل 5 ترندات
        top_trends = sorted(trends_data, key=lambda x: x.get('viral_score', 0), reverse=True)[:5]
        
        trends_table_data = [['الترتيب', 'الكلمة المفتاحية', 'نقاط الانتشار', 'الفئة']]
        
        for i, trend in enumerate(top_trends, 1):
            trends_table_data.append([
                str(i),
                trend.get('keyword', 'غير محدد'),
                f"{trend.get('viral_score', 0)}/100",
                trend.get('category', '').replace('🔥', '').replace('📈', '').replace('📊', '').strip()
            ])
        
        trends_table = Table(trends_table_data, colWidths=[0.8*inch, 2.5*inch, 1.2*inch, 1.5*inch])
        trends_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.lightblue, colors.white])
        ]))
        
        elements.append(trends_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_price_analysis(self, price_data: dict) -> list:
        """تحليل الأسعار"""
        
        elements = []
        
        heading = Paragraph("💰 تحليل الأسعار الأسبوعي", self.arabic_heading)
        elements.append(heading)
        
        # ملخص الأسعار
        price_summary = price_data.get('price_analysis', {})
        
        price_info = [
            ['أقل سعر', f"${price_summary.get('min_price', 0):.2f}"],
            ['أعلى سعر', f"${price_summary.get('max_price', 0):.2f}"],
            ['متوسط السعر', f"${price_summary.get('avg_price', 0):.2f}"],
            ['إجمالي المنتجات', str(price_data.get('total_products', 0))]
        ]
        
        price_table = Table(price_info, colWidths=[2*inch, 2*inch])
        price_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.green),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen)
        ]))
        
        elements.append(price_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_recommendations_section(self, user_data: dict, trends_data: list) -> list:
        """قسم التوصيات"""
        
        elements = []
        
        heading = Paragraph("💡 التوصيات الشخصية", self.arabic_heading)
        elements.append(heading)
        
        # توصيات عامة
        recommendations = [
            "• راقب الترندات عالية الانتشار للاستفادة منها",
            "• انشر محتوى متعلق بالترندات الساخنة",
            "• تابع أسعار المنتجات التي تهمك",
            "• استخدم أدوات التحليل المتقدمة في Dashboard"
        ]
        
        for rec in recommendations:
            rec_para = Paragraph(rec, self.arabic_normal)
            elements.append(rec_para)
        
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_charts_section(self, trends_data: list) -> list:
        """قسم الرسوم البيانية"""
        
        elements = []
        
        heading = Paragraph("📈 الرسوم البيانية", self.arabic_heading)
        elements.append(heading)
        
        try:
            # إنشاء رسم بياني لنقاط الانتشار
            chart_path = self._create_viral_score_chart(trends_data)
            
            if chart_path and chart_path.exists():
                # إضافة الرسم البياني للتقرير
                img = Image(str(chart_path), width=6*inch, height=4*inch)
                elements.append(img)
                elements.append(Spacer(1, 10))
                
                # حذف الملف المؤقت
                chart_path.unlink()
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء الرسم البياني: {e}")
            error_text = Paragraph("خطأ في تحميل الرسم البياني", self.arabic_normal)
            elements.append(error_text)
        
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_viral_score_chart(self, trends_data: list) -> Path:
        """إنشاء رسم بياني لنقاط الانتشار"""
        
        if not trends_data:
            return None
        
        # تحضير البيانات
        keywords = [trend.get('keyword', 'غير محدد')[:15] + '...' if len(trend.get('keyword', '')) > 15 
                   else trend.get('keyword', 'غير محدد') for trend in trends_data[:10]]
        scores = [trend.get('viral_score', 0) for trend in trends_data[:10]]
        
        # إنشاء الرسم البياني
        plt.figure(figsize=(10, 6))
        plt.style.use('seaborn-v0_8')
        
        bars = plt.bar(keywords, scores, color='skyblue', edgecolor='navy')
        
        # تنسيق الرسم
        plt.title('نقاط الانتشار للترندات الأسبوعية', fontsize=16, pad=20)
        plt.xlabel('الكلمات المفتاحية', fontsize=12)
        plt.ylabel('نقاط الانتشار', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # إضافة قيم على الأعمدة
        for bar, score in zip(bars, scores):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{score}', ha='center', va='bottom', fontsize=10)
        
        # حفظ الرسم
        chart_path = self.output_dir / "temp_chart.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _create_footer_section(self) -> list:
        """قسم الخاتمة"""
        
        elements = []
        
        elements.append(Spacer(1, 30))
        
        footer_text = f"""
        ---
        🤖 هذا التقرير تم إنشاؤه تلقائياً بواسطة BraveBot Dashboard
        📅 تاريخ الإنشاء: {datetime.now().strftime('%d/%m/%Y - %H:%M')}
        
        للمزيد من المعلومات والتحليلات المتقدمة، قم بزيارة Dashboard الخاص بك
        """
        
        footer = Paragraph(footer_text, self.arabic_normal)
        elements.append(footer)
        
        return elements

# إنشاء instance عالمي
pdf_generator = PDFReportGenerator()