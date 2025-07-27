import sqlite3
from datetime import datetime

DB_PATH = "data/bravebot.db"  # نفس مسار قاعدة البيانات اللي عندك

# ===== دالة إرجاع أفضل المستخدمين =====
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

        # تحويل النتائج لقائمة قواميس
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
