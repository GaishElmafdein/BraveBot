import sqlite3
import os
from datetime import datetime

# مسار قاعدة البيانات
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "bravebot.db")

# ===== تهيئة قاعدة البيانات =====
def init_db():
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

# ===== استرجاع الإحصائيات =====
def get_user_stats(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user_stats WHERE user_id=?", (user_id,))
    row = cursor.fetchone()

    # إنشاء سجل لو مش موجود
    if not row:
        cursor.execute("""
            INSERT INTO user_stats (user_id, total_checks, passed_checks, failed_checks, last_check, joined_date)
            VALUES (?, 0, 0, 0, NULL, ?)
        """, (user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        cursor.execute("SELECT * FROM user_stats WHERE user_id=?", (user_id,))
        row = cursor.fetchone()

    conn.close()

    return {
        "user_id": row[0],
        "total_checks": row[1],
        "passed_checks": row[2],
        "failed_checks": row[3],
        "last_check": row[4],
        "joined_date": row[5],
    }

# ===== تحديث الإحصائيات =====
def update_user_stats(user_id, is_compliant, timestamp):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = get_user_stats(user_id)

    total = stats["total_checks"] + 1
    passed = stats["passed_checks"] + (1 if is_compliant else 0)
    failed = stats["failed_checks"] + (0 if is_compliant else 1)

    cursor.execute("""
        UPDATE user_stats
        SET total_checks=?, passed_checks=?, failed_checks=?, last_check=?
        WHERE user_id=?
    """, (total, passed, failed, timestamp, user_id))

    conn.commit()
    conn.close()

# ===== سجل النشاط =====
def add_log(message, level="INFO", user_id=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO logs (user_id, message, level, timestamp)
        VALUES (?, ?, ?, ?)
    """, (user_id, message, level, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()

# ===== أفضل المستخدمين =====
def get_leaderboard(limit=5):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, total_checks FROM user_stats
        ORDER BY total_checks DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()

    return [{"name": f"User {row[0]}", "total_checks": row[1]} for row in rows]

# ===== تصدير بيانات المستخدم =====
def export_user_stats(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, total_checks, passed_checks, failed_checks, last_check, joined_date
        FROM user_stats WHERE user_id=?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "user_id": row[0],
            "total_checks": row[1],
            "passed_checks": row[2],
            "failed_checks": row[3],
            "last_check": row[4],
            "joined_date": row[5],
        }
    return None

# ===== إعادة تعيين بيانات المستخدم =====
def reset_user_stats(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE user_stats
        SET total_checks=0, passed_checks=0, failed_checks=0, last_check=NULL
        WHERE user_id=?
    """, (user_id,))

    conn.commit()
    conn.close()
