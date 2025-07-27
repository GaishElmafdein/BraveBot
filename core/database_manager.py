import sqlite3

DB_PATH = "bravebot.db"

# ================== تهيئة قاعدة البيانات ==================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
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

# ================== تحديث إحصائيات المستخدم ==================
def update_user_stats(user_id: int, passed: bool, timestamp: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # تأكد لو المستخدم مش موجود أضفه
    cur.execute("""
        INSERT INTO user_stats (user_id, total_checks, passed_checks, last_check)
        VALUES (?, 0, 0, ?)
        ON CONFLICT(user_id) DO NOTHING
    """, (user_id, timestamp))

    # حدث الإحصائيات
    cur.execute("""
        UPDATE user_stats
        SET total_checks = total_checks + 1,
            passed_checks = passed_checks + ?,
            last_check = ?
        WHERE user_id = ?
    """, (1 if passed else 0, timestamp, user_id))

    conn.commit()
    conn.close()

# ================== جلب إحصائيات المستخدم ==================
def get_user_stats(user_id: int):
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
