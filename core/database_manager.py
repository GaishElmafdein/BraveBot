import sqlite3
import os
from datetime import datetime

# مسار قاعدة البيانات
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "bravebot.db")

# =========================================================
# دوال تهيئة قاعدة البيانات
# =========================================================
def init_db():
    """إنشاء الجداول لو مش موجودة"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # جدول الإحصائيات
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_stats (
        user_id INTEGER PRIMARY KEY,
        total_checks INTEGER DEFAULT 0,
        passed_checks INTEGER DEFAULT 0,
        failed_checks INTEGER DEFAULT 0,
        last_check TEXT,
        joined_date TEXT DEFAULT (datetime('now'))
    )
    """)

    # جدول السجلات
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()

# =========================================================
# دوال التعامل مع الإحصائيات
# =========================================================
def get_user_stats(user_id):
    """جلب إحصائيات مستخدم"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT total_checks, passed_checks, failed_checks, last_check, joined_date
        FROM user_stats
        WHERE user_id=?
    """, (user_id,))
    row = cursor.fetchone()

    if row is None:
        # لو المستخدم جديد نرجع قيم صفرية
        return {
            "total_checks": 0,
            "passed_checks": 0,
            "failed_checks": 0,
            "last_check": "لم يتم بعد",
            "joined_date": "غير محدد"
        }

    conn.close()
    return {
        "total_checks": row[0],
        "passed_checks": row[1],
        "failed_checks": row[2],
        "last_check": row[3] or "لم يتم بعد",
        "joined_date": row[4] or "غير محدد"
    }

def update_user_stats(user_id, is_compliant, timestamp):
    """تحديث إحصائيات المستخدم"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # هل المستخدم موجود؟
    cursor.execute("SELECT * FROM user_stats WHERE user_id=?", (user_id,))
    row = cursor.fetchone()

    if row is None:
        # لو أول مرة يدخل
        total = 1
        passed = 1 if is_compliant else 0
        failed = 0 if is_compliant else 1
        cursor.execute("""
            INSERT INTO user_stats (user_id, total_checks, passed_checks, failed_checks, last_check, joined_date)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (user_id, total, passed, failed, timestamp))
    else:
        # تحديث القيم
        total = row[1] + 1
        passed = row[2] + (1 if is_compliant else 0)
        failed = row[3] + (0 if is_compliant else 1)
        cursor.execute("""
            UPDATE user_stats
            SET total_checks=?, passed_checks=?, failed_checks=?, last_check=?
            WHERE user_id=?
        """, (total, passed, failed, timestamp, user_id))

    conn.commit()
    conn.close()

# =========================================================
# دالة جلب لوحة الصدارة
# =========================================================
def get_leaderboard(limit=5):
    """إرجاع أفضل المستخدمين حسب عدد الفحوصات"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, total_checks, passed_checks, failed_checks
        FROM user_stats
        ORDER BY total_checks DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    leaderboard = []
    for row in rows:
        leaderboard.append({
            "name": f"User {row[0]}",   # حالياً اسم افتراضي
            "total_checks": row[1],
            "passed_checks": row[2],
            "failed_checks": row[3],
        })

    return leaderboard

# =========================================================
# دالة إضافة سجل
# =========================================================
def add_log(action, user_id=None, level="INFO"):
    """تسجيل الأحداث"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO logs (user_id, action, timestamp)
        VALUES (?, ?, ?)
    """, (user_id, f"[{level}] {action}", timestamp))

    conn.commit()
    conn.close()

# =========================================================
# تصدير الدوال
# =========================================================
__all__ = [
    "init_db",
    "get_user_stats",
    "update_user_stats",
    "add_log",
    "get_leaderboard"
]
