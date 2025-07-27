# 🤖 BraveBot - فاحص المنتجات الذكي

<div align="center">

![BraveBot Logo](https://img.shields.io/badge/BraveBot-v2.0-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-green?style=for-the-badge&logo=python)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?style=for-the-badge&logo=telegram)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**بوت تليجرام ذكي لفحص توافق المنتجات مع نظام إنجازات متقدم**

[🚀 التجربة المباشرة](https://t.me/YourBotUsername) • [📖 الدوكيومنتيشن](#) • [🐛 الإبلاغ عن خطأ](#)

</div>

---

## 📋 فهرس المحتويات

- [✨ الميزات الرئيسية](#-الميزات-الرئيسية)
- [🏆 نظام الإنجازات](#-نظام-الإنجازات)
- [🛠️ التكنولوجيا المستخدمة](#️-التكنولوجيا-المستخدمة)
- [⚡ التثبيت السريع](#-التثبيت-السريع)
- [🔧 الإعداد المحلي](#-الإعداد-المحلي)
- [🚀 النشر على Railway](#-النشر-على-railway)
- [📊 نظام المراقبة](#-نظام-المراقبة)
- [🔄 النسخ الاحتياطية](#-النسخ-الاحتياطية)
- [📸 صور من البوت](#-صور-من-البوت)
- [🤝 المساهمة](#-المساهمة)

---

## ✨ الميزات الرئيسية

### 🔍 **فحص المنتجات الذكي**
- فحص توافق المنتجات مع معايير محددة
- تحليل الأسعار والمواصفات
- نتائج فورية مع أسباب مفصلة

### 🏅 **نظام الإنجازات المتقدم**
- 8 مستويات إنجازات تدريجية
- شريط تقدم تفاعلي
- إشعارات فورية عند تحقيق إنجاز جديد

### 📊 **إحصائيات شاملة**
- تتبع شامل لجميع الأنشطة
- معدلات النجاح والفشل
- إحصائيات زمنية مفصلة

### 🛡️ **الأمان والموثوقية**
- نسخ احتياطية تلقائية
- مراقبة صحة البوت 24/7
- تشفير البيانات الحساسة

### 🔄 **التحديثات التلقائية**
- CI/CD pipeline احترافي
- تحديثات سلسة بدون انقطاع
- تقارير أسبوعية للمستخدمين

---

## 🏆 نظام الإنجازات

| المستوى | الاسم | المتطلب | الوصف |
|---------|-------|---------|--------|
| 🌱 | أول خطوة | 1 فحص | بداية رحلتك مع البوت |
| 🔍 | مبتدئ | 5 فحوص | تعلم أساسيات الفحص |
| ⭐ | خبير مبتدئ | 10 فحوص | تطوير مهاراتك |
| 🏆 | محترف | 25 فحص | إتقان استخدام البوت |
| 💎 | خبير | 50 فحص | خبرة متقدمة |
| 🚀 | ماهر | 100 فحص | مستوى عالٍ من الخبرة |
| 👑 | أسطورة | 250 فحص | إنجاز استثنائي |
| 🏅 | بطل التوافق | 500 فحص | قمة الإتقان |

---

## 🛠️ التكنولوجيا المستخدمة

### 🐍 **Backend**
- **Python 3.11+** - لغة البرمجة الأساسية
- **python-telegram-bot** - مكتبة بوت التليجرام
- **SQLite** - قاعدة البيانات المحلية
- **asyncio** - البرمجة غير المتزامنة

### 🔧 **أدوات التطوير**
- **pytest** - اختبار الكود
- **black** - تنسيق الكود
- **flake8** - فحص جودة الكود
- **bandit** - فحص الأمان

### ☁️ **البنية التحتية**
- **Railway** - منصة النشر
- **GitHub Actions** - CI/CD
- **Docker** - التحويل إلى حاويات

### 📊 **المراقبة والتحليل**
- **psutil** - مراقبة الموارد
- **aiohttp** - طلبات HTTP غير متزامنة
- **pandas** - تحليل البيانات

---

## ⚡ التثبيت السريع

### 🚀 **النسخة السحابية (موصى بها)**

1. **انقر هنا للبدء مباشرة:**
   ```
   👉 https://t.me/YourBotUsername
   ```

2. **أرسل الأمر التالي:**
   ```
   /start
   ```

### 💻 **التشغيل المحلي**

```bash
# نسخ المشروع
git clone https://github.com/GaishElmafdein/BraveBot.git
cd BraveBot

# إنشاء بيئة افتراضية
python -m venv venv
source venv/bin/activate  # Linux/Mac
# أو
venv\\Scripts\\activate  # Windows

# تثبيت المتطلبات
pip install -r requirements.txt

# إعداد متغيرات البيئة
cp .env.example .env
# أضف TELEGRAM_TOKEN الخاص بك

# تشغيل البوت
python main.py
```

---

## 🔧 الإعداد المحلي

### 1️⃣ **إنشاء بوت تليجرام**

1. أرسل `/newbot` إلى [@BotFather](https://t.me/BotFather)
2. اتبع التعليمات واحصل على `TELEGRAM_TOKEN`
3. احفظ التوكن في ملف `.env`

### 2️⃣ **إعداد قاعدة البيانات**

```bash
# إنشاء قاعدة البيانات تلقائياً عند أول تشغيل
python -c "from core.database_manager import init_db; init_db()"
```

### 3️⃣ **إعداد الإعدادات**

```yaml
# config/config.yaml
max_price: 10000
min_price: 0.01
admin_ids: [123456789]  # ضع معرف التليجرام الخاص بك
rate_limit:
  checks_per_hour: 50
  checks_per_day: 200
```

### 4️⃣ **اختبار البوت**

```bash
# تشغيل الاختبارات
pytest tests/ -v

# فحص جودة الكود
black . && flake8 .

# فحص الأمان
bandit -r . -f json
```

---

## 🚀 النشر على Railway

### 📋 **المتطلبات**
- حساب [Railway](https://railway.app)
- حساب [GitHub](https://github.com)
- بوت تليجرام جاهز

### 🔄 **خطوات النشر**

1. **Fork المشروع إلى حسابك على GitHub**

2. **اربط Railway بـ GitHub:**
   ```bash
   # في Railway Dashboard
   New Project → Deploy from GitHub → اختر BraveBot
   ```

3. **إضافة متغيرات البيئة:**
   ```env
   TELEGRAM_TOKEN=your_bot_token_here
   DATABASE_URL=sqlite:///bravebot.db
   ```

4. **النشر التلقائي:**
   - كل push للـ main branch سيتم النشر تلقائياً
   - GitHub Actions ستقوم بالاختبار أولاً

### 🔐 **إعداد Secrets في GitHub**

```bash
# في GitHub Repository → Settings → Secrets
TELEGRAM_TOKEN=your_bot_token
RAILWAY_TOKEN=your_railway_token
```

---

## 📊 نظام المراقبة

### 🏥 **Health Checks**

البوت يراقب نفسه تلقائياً كل دقيقة:

```python
# تشغيل مراقب الصحة
python scripts/health_monitor.py
```

**المراقبة تشمل:**
- ✅ حالة Telegram API
- 🗃️ سلامة قاعدة البيانات  
- 💾 استخدام الذاكرة والمعالج
- 📡 سرعة الاستجابة

### 📧 **التنبيهات**

```json
{
  "telegram_chat_id": "123456789",
  "email_notifications": {
    "enabled": true,
    "recipient": "admin@example.com"
  }
}
```

### 📈 **إحصائيات الأداء**

- **Uptime:** 99.9%
- **متوسط الاستجابة:** <0.5 ثانية
- **المستخدمين النشطين:** يومياً
- **الفحوصات:** شهرياً

---

## 🔄 النسخ الاحتياطية

### ⚙️ **النسخ التلقائي**

```bash
# تشغيل نظام النسخ الاحتياطي
python scripts/backup_system.py
```

**الميزات:**
- 🗜️ ضغط تلقائي لتوفير المساحة
- 🔐 تشفير البيانات الحساسة
- ☁️ رفع إلى GitHub Releases
- 🧹 تنظيف النسخ القديمة تلقائياً

### 📅 **جدولة النسخ**

```json
{
  "backup_schedule": {
    "daily": true,
    "weekly": true,
    "monthly": true,
    "time": "02:00"
  }
}
```

### 🔄 **استرداد النسخ الاحتياطية**

```bash
# استرداد نسخة احتياطية محددة
python scripts/restore_backup.py --backup-file=backup_20250127.db.gz
```

---

## 📸 صور من البوت

### 🏠 **الشاشة الرئيسية**
```
🎉 أهلاً وسهلاً أحمد!

🤖 BraveBot - فاحص المنتجات الذكي
✨ مصمم خصيصاً لاستخدامك الشخصي!

🔍 /compliance - فحص منتج جديد
📊 /stats - إحصائياتك وإنجازاتك
🏅 /achievements - جميع الإنجازات
```

### 📊 **صفحة الإحصائيات**
```
📊 إحصائيات أحمد
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 مستواك الحالي: 🏆 محترف

📈 الأرقام:
🔍 إجمالي الفحوصات: 27
✅ المقبولة: 22 (81.5%)
❌ المرفوضة: 5 (18.5%)
📊 معدل النجاح الإجمالي: 81.5%

🎯 الهدف التالي: 💎 خبير
📊 ████████░░ 54%
🔄 باقي 23 فحص للوصول
```

### 🏆 **صفحة الإنجازات**
```
🏅 جميع إنجازاتك
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ الإنجازات المكتملة (4):
🌱 أول خطوة - أول فحص للمنتج
🔍 مبتدئ - 5 فحوصات
⭐ خبير مبتدئ - 10 فحوصات
🏆 محترف - 25 فحص

🎯 الهدف التالي:
💎 خبير - 50 فحص
📊 التقدم: ████████░░ 54%
🔄 باقي 23 فحص للوصول
```

---

## 🧪 الاختبارات

### 🔬 **تشغيل جميع الاختبارات**

```bash
# اختبارات شاملة مع تغطية الكود
pytest tests/ -v --cov=. --cov-report=html

# اختبارات سريعة فقط
pytest tests/test_core.py -v

# اختبار مكونات محددة
pytest tests/test_ai.py::test_compliance_checker -v
```

### 📊 **تقرير التغطية**

```bash
# عرض تقرير التغطية في المتصفح
open htmlcov/index.html
```

**هدف التغطية:** >90%

---

## 🚀 سكريبت التشغيل السريع

### 🖥️ **Windows**
```batch
@echo off
echo 🚀 Starting BraveBot...
cd /d %~dp0
call venv\\Scripts\\activate
python main.py
pause
```

### 🐧 **Linux/Mac**
```bash
#!/bin/bash
echo "🚀 Starting BraveBot..."
cd "$(dirname "$0")"
source venv/bin/activate
python main.py
```

---

## 🔧 أوامر البوت الكاملة

| الأمر | الوصف | مثال |
|-------|--------|------|
| `/start` | بدء استخدام البوت | `/start` |
| `/compliance` | فحص منتج جديد | `/compliance` |
| `/stats` | عرض إحصائياتك | `/stats` |
| `/achievements` | جميع الإنجازات | `/achievements` |
| `/settings` | إعدادات الحساب | `/settings` |
| `/help` | دليل الاستخدام | `/help` |
| `/export` | تصدير بياناتك | `/export` |
| `/reset` | إعادة تعيين الإحصائيات | `/reset` |
| `/cancel` | إلغاء العملية الحالية | `/cancel` |

---

## 🤝 المساهمة

### 🎯 **كيفية المساهمة**

1. **Fork المشروع**
2. **أنشئ فرع جديد:** `git checkout -b feature/amazing-feature`
3. **أضف تحسيناتك:** `git commit -m 'Add amazing feature'`
4. **ارفع التحديث:** `git push origin feature/amazing-feature`
5. **افتح Pull Request**

### 📋 **Guidelines للمساهمة**

- ✅ اكتب كود نظيف ومفهوم
- ✅ أضف اختبارات للميزات الجديدة
- ✅ تأكد من تمرير جميع الاختبارات
- ✅ اتبع نمط الكود الموجود
- ✅ أضف وثائق للميزات الجديدة

### 🐛 **الإبلاغ عن الأخطاء**

```markdown
**وصف الخطأ:**
وصف واضح ومختصر للخطأ

**خطوات الاستنساخ:**
1. اذهب إلى '...'
2. انقر على '....'
3. اكتب '....'
4. اظهر الخطأ

**السلوك المتوقع:**
وصف واضح لما كنت تتوقع حدوثه

**لقطات الشاشة:**
إن أمكن، أضف لقطات شاشة لتوضيح المشكلة
```

---

## 📄 الترخيص

هذا المشروع مرخص تحت [MIT License](LICENSE) - راجع ملف LICENSE للتفاصيل.

---

## 👨‍💻 المطور

**Gaish Elmafdein**
- 🌐 GitHub: [@GaishElmafdein](https://github.com/GaishElmafdein)
- 📧 Email: [your.email@example.com](mailto:your.email@example.com)
- 💼 LinkedIn: [في الملف الشخصي](https://linkedin.com/in/yourprofile)

---

## 🙏 شكر وتقدير

- **python-telegram-bot** - للمكتبة الرائعة
- **Railway** - لمنصة النشر المجانية
- **GitHub** - لاستضافة الكود والـ CI/CD
- **جميع المساهمين** - لجعل البوت أفضل

---

## 📈 إحصائيات المشروع

![GitHub Stars](https://img.shields.io/github/stars/GaishElmafdein/BraveBot?style=social)
![GitHub Forks](https://img.shields.io/github/forks/GaishElmafdein/BraveBot?style=social)
![GitHub Issues](https://img.shields.io/github/issues/GaishElmafdein/BraveBot)
![GitHub Pull Requests](https://img.shields.io/github/issues-pr/GaishElmafdein/BraveBot)

---

<div align="center">

**🌟 إذا أعجبك المشروع، لا تنس إعطاءه نجمة! 🌟**

**صُنع بـ ❤️ من أجل مجتمع المطورين العرب**

</div>
