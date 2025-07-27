import sqlite3
import os

# تحديد مسار قاعدة البيانات
DB_PATH = os.path.join(os.getcwd(), "bravebot.db")

def init_db():
    """إنشاء الجداول لو مش موجودة"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # جدول إحصائيات المستخدمين
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_stats (
        user_id INTEGER PRIMARY KEY,
        total_checks INTEGER DEFAULT 0,
        passed_checks INTEGER DEFAULT 0,
        failed_checks INTEGER DEFAULT 0,
        last_check TEXT,
        joined_date TEXT
    )
    """)

    conn.commit()
    conn.close()

def get_user_stats(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_stats WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if not row:
        # لو مفيش بيانات، يرجع صفر
        return {
            "user_id": user_id,
            "total_checks": 0,
            "passed_checks": 0,
            "failed_checks": 0,
            "last_check": "لم يتم بعد",
            "joined_date": "غير محدد"
        }

    return {
        "user_id": row[0],
        "total_checks": row[1],
        "passed_checks": row[2],
        "failed_checks": row[3],
        "last_check": row[4],
        "joined_date": row[5]
    }

def update_user_stats(user_id, is_compliant, timestamp):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # جلب الإحصائيات الحالية
    cursor.execute("SELECT * FROM user_stats WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if not row:
        # إضافة مستخدم جديد
        total = 1
        passed = 1 if is_compliant else 0
        failed = 0 if is_compliant else 1
        cursor.execute("""
            INSERT INTO user_stats (user_id, total_checks, passed_checks, failed_checks, last_check, joined_date)
            VALUES (?, ?, ?, ?, ?, DATE('now'))
        """, (user_id, total, passed, failed, timestamp))
    else:
        # تحديث البيانات
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
