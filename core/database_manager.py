import sqlite3
import os

# تحديد مسار قاعدة البيانات بشكل مطلق
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "bravebot.db"))

# دالة إنشاء قاعدة البيانات والجداول
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)  # يتأكد إن المجلد موجود
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # إنشاء جدول المستخدمين
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

    # إنشاء جدول اللوج
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT,
        level TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()


# دالة إضافة لوج
def add_log(message, level="INFO"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO logs (message, level, timestamp) VALUES (?, ?, datetime('now'))",
        (message, level)
    )
    conn.commit()
    conn.close()


# دالة الحصول على إحصائيات مستخدم
def get_user_stats(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_stats WHERE user_id=?", (user_id,))
    row = cursor.fetchone()

    if not row:
        # لو مفيش بيانات للمستخدم نرجع داتا افتراضية
        return {
            "total_checks": 0,
            "passed_checks": 0,
            "failed_checks": 0,
            "last_check": "لم يتم بعد",
            "joined_date": "غير محدد"
        }

    return {
        "total_checks": row[1],
        "passed_checks": row[2],
        "failed_checks": row[3],
        "last_check": row[4],
        "joined_date": row[5]
    }


# دالة تحديث الإحصائيات
def update_user_stats(user_id, is_compliant, timestamp):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # لو المستخدم جديد
    cursor.execute("SELECT * FROM user_stats WHERE user_id=?", (user_id,))
    row = cursor.fetchone()

    if not row:
        cursor.execute("""
            INSERT INTO user_stats (user_id, total_checks, passed_checks, failed_checks, last_check, joined_date)
            VALUES (?, 1, ?, ?, ?, date('now'))
        """, (user_id, 1 if is_compliant else 0, 0 if is_compliant else 1, timestamp))
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
def get_leaderboard(limit=10):
    """إرجاع أفضل المستخدمين حسب إجمالي الفحوصات"""
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
            "user_id": row[0],
            "total_checks": row[1],
            "passed_checks": row[2],
            "failed_checks": row[3]
        })

    return leaderboard
