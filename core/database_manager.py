import sqlite3
from datetime import datetime

# مسار قاعدة البيانات
DB_PATH = "data/bravebot.db"

# ===== تهيئة قاعدة البيانات =====
def init_db():
    """
    إنشاء الجداول لو مش موجودة
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # جدول إحصائيات المستخدمين
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_stats (
            user_id INTEGER PRIMARY KEY,
            total_checks INTEGER DEFAULT 0,
            passed_checks INTEGER DEFAULT 0,
            last_check TEXT
        )
    """)

    conn.commit()
    conn.close()

# ===== تحديث إحصائيات المستخدم =====
def update_user_stats(user_id: int, passed: bool, timestamp: str):
    """
    تحديث عدد الفحوصات للمستخدم + آخر فحص
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # لو المستخدم مش موجود أضفه
    cur.execute("""
        INSERT OR IGNORE INTO user_stats (user_id, total_checks, passed_checks, last_check)
        VALUES (?, 0, 0, ?)
    """, (user_id, timestamp))

    # تحديث الإحصائيات
    cur.execute("""
        UPDATE user_stats
        SET total_checks = total_checks + 1,
            passed_checks = passed_checks + ?,
            last_check = ?
        WHERE user_id = ?
    """, (1 if passed else 0, timestamp, user_id))

    conn.commit()
    conn.close()

# ===== جلب إحصائيات المستخدم =====
def get_user_stats(user_id: int):
    """
    استرجاع بيانات الإحصائيات لمستخدم معين
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT total_checks, passed_checks, last_check
        FROM user_stats WHERE user_id = ?
    """, (user_id,))
    row = cur.fetchone()
    conn.close()

    if row:
        total, passed, last_check = row
        return {
            "total_checks": total,
            "passed_checks": passed,
            "failed_checks": total - passed,
            "last_check": last_check
        }
    else:
        return {
            "total_checks": 0,
            "passed_checks": 0,
            "failed_checks": 0,
            "last_check": "لم يتم بعد"
        }

# ===== تسجيل الأحداث =====
def add_log(message: str):
    """
    دالة لتسجيل أي حدث مهم (حاليًا تطبع في الـ console)
    """
    print(f"[LOG] {datetime.now()} - {message}")

# ===== إرجاع أفضل المستخدمين (Leaderboard) =====
def get_leaderboard(limit=10):
    """
    إرجاع أفضل المستخدمين حسب إجمالي الفحوصات
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT user_id, total_checks
            FROM user_stats
            ORDER BY total_checks DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()

        leaderboard = []
        for row in rows:
            leaderboard.append({
                "user_id": row[0],
                "total_checks": row[1]
            })

        return leaderboard

    except Exception as e:
        print(f"Error fetching leaderboard: {e}")
        return []

    finally:
        conn.close()
