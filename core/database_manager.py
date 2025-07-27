import sqlite3
from datetime import datetime
import os

# مسار قاعدة البيانات
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bravebot.db")

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

# ===== إضافة Log جديد =====
def add_log(message, level="INFO", user_id=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO logs (user_id, message, level, timestamp)
        VALUES (?, ?, ?, ?)
    """, (user_id, message, level, timestamp))

    conn.commit()
    conn.close()

# ===== جلب الإحصائيات =====
def get_user_stats(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user_stats WHERE user_id=?", (user_id,))
    row = cursor.fetchone()

    if not row:
        # إدخال مستخدم جديد
        joined_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO user_stats (user_id, total_checks, passed_checks, failed_checks, last_check, joined_date)
            VALUES (?, 0, 0, 0, 'لم يتم بعد', ?)
        """, (user_id, joined_date))
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
        "joined_date": row[5]
    }

# ===== تحديث الإحصائيات =====
def update_user_stats(user_id, is_compliant, timestamp):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user_stats WHERE user_id=?", (user_id,))
    row = cursor.fetchone()

    if not row:
        joined_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO user_stats (user_id, total_checks, passed_checks, failed_checks, last_check, joined_date)
            VALUES (?, 0, 0, 0, 'لم يتم بعد', ?)
        """, (user_id, joined_date))
        conn.commit()
        cursor.execute("SELECT * FROM user_stats WHERE user_id=?", (user_id,))
        row = cursor.fetchone()

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

# ===== جلب أفضل المستخدمين =====
def get_leaderboard(limit=5):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, total_checks FROM user_stats
        ORDER BY total_checks DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()

    leaderboard = []
    for row in rows:
        leaderboard.append({"name": f"User {row[0]}", "total_checks": row[1]})

    conn.close()
    return leaderboard
