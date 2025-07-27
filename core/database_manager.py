import os
import sqlite3
from datetime import datetime

# تحديد مسار قاعدة البيانات بشكل صحيح (في جذر المشروع)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # مسار مجلد core
PROJECT_DIR = os.path.dirname(BASE_DIR)                 # يطلع لفوق لمجلد المشروع الرئيسي
DB_PATH = os.path.join(PROJECT_DIR, "bravebot.db")      # ملف قاعدة البيانات في جذر المشروع

# ========== تهيئة قاعدة البيانات ==========
def init_db():
    """إنشاء الجداول المطلوبة لو مش موجودة"""
    # تأكد إن المسار الأساسي موجود
    os.makedirs(PROJECT_DIR, exist_ok=True)

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
            joined_date TEXT
        )
    """)

    # جدول السجلات
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            level TEXT,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()


# ========== إضافة سجل ==========
def add_log(message, level="INFO", user_id=None):
    """إضافة سجل جديد إلى جدول السجلات"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO logs (user_id, message, level, timestamp)
        VALUES (?, ?, ?, ?)
    """, (user_id, message, level, timestamp))

    conn.commit()
    conn.close()


# ========== تحديث إحصائيات المستخدم ==========
def update_user_stats(user_id, is_compliant, timestamp):
    """تحديث إحصائيات المستخدم بعد الفحص"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user_stats WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute("""
            INSERT INTO user_stats (user_id, total_checks, passed_checks, failed_checks, last_check, joined_date)
            VALUES (?, 1, ?, ?, ?, ?)
        """, (
            user_id,
            1 if is_compliant else 0,
            0 if is_compliant else 1,
            timestamp,
            datetime.now().strftime("%Y-%m-%d")
        ))
    else:
        cursor.execute("""
            UPDATE user_stats
            SET total_checks = total_checks + 1,
                passed_checks = passed_checks + ?,
                failed_checks = failed_checks + ?,
                last_check = ?
            WHERE user_id = ?
        """, (
            1 if is_compliant else 0,
            0 if is_compliant else 1,
            timestamp,
            user_id
        ))

    conn.commit()
    conn.close()


# ========== جلب إحصائيات مستخدم ==========
def get_user_stats(user_id):
    """جلب إحصائيات مستخدم واحد"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user_stats WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return {
            "user_id": user_id,
            "total_checks": 0,
            "passed_checks": 0,
            "failed_checks": 0,
            "last_check": "غير متاح",
            "joined_date": datetime.now().strftime("%Y-%m-%d")
        }

    return {
        "user_id": user[0],
        "total_checks": user[1],
        "passed_checks": user[2],
        "failed_checks": user[3],
        "last_check": user[4],
        "joined_date": user[5]
    }


# ========== جلب لوحة الصدارة ==========
def get_leaderboard(limit=5):
    """جلب أفضل المستخدمين بناءً على إجمالي الفحوصات"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, total_checks FROM user_stats
        ORDER BY total_checks DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()

    return [{"name": f"User {row[0]}", "total_checks": row[1]} for row in rows]


# ========== تصدير إحصائيات مستخدم ==========
def export_user_stats(user_id):
    """تصدير بيانات مستخدم واحد"""
    stats = get_user_stats(user_id)
    if stats["total_checks"] == 0:
        return None
    return stats


# ========== إعادة تعيين الإحصائيات ==========
def reset_user_stats(user_id):
    """إعادة تعيين بيانات المستخدم"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE user_stats
        SET total_checks = 0,
            passed_checks = 0,
            failed_checks = 0,
            last_check = NULL
        WHERE user_id = ?
    """, (user_id,))

    conn.commit()
    conn.close()
