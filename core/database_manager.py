import os
import sqlite3
from datetime import datetime
import json

# تحديد مسار قاعدة البيانات بشكل صحيح (في جذر المشروع)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # مسار مجلد core
PROJECT_DIR = os.path.dirname(BASE_DIR)                 # يطلع لفوق لمجلد المشروع الرئيسي
DB_PATH = os.path.join(PROJECT_DIR, "bravebot.db")      # ملف قاعدة البيانات في جذر المشروع

# ========== تهيئة قاعدة البيانات ==========
def init_database():
    """تهيئة قاعدة البيانات"""
    try:
        conn = sqlite3.connect('bot_data.db')
        cursor = conn.cursor()
        
        # إنشاء جدول المستخدمين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                compliance_checks INTEGER DEFAULT 0,
                achievements TEXT DEFAULT '[]'
            )
        ''')
        
        # إنشاء جدول السجلات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                level TEXT DEFAULT 'INFO',
                message TEXT,
                user_id INTEGER,
                details TEXT
            )
        ''')
        
        # إنشاء جدول البيانات المؤقتة
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False

# ========== إضافة سجل ==========
def add_log(message, level="INFO", user_id=None, details=None):
    """إضافة سجل جديد"""
    try:
        conn = sqlite3.connect('bot_data.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO logs (message, level, user_id, details)
            VALUES (?, ?, ?, ?)
        ''', (message, level, user_id, details))
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Logging error: {e}")
        return False

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


def init_database():
    """تهيئة قاعدة البيانات"""
    try:
        conn = sqlite3.connect('bot_data.db')
        cursor = conn.cursor()
        
        # إنشاء جدول المستخدمين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                compliance_checks INTEGER DEFAULT 0,
                achievements TEXT DEFAULT '[]'
            )
        ''')
        
        # إنشاء جدول السجلات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                level TEXT DEFAULT 'INFO',
                message TEXT,
                user_id INTEGER,
                details TEXT
            )
        ''')
        
        # إنشاء جدول البيانات المؤقتة
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False

def add_log(message, level="INFO", user_id=None, details=None):
    """إضافة سجل جديد"""
    try:
        conn = sqlite3.connect('bot_data.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO logs (message, level, user_id, details)
            VALUES (?, ?, ?, ?)
        ''', (message, level, user_id, details))
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Logging error: {e}")
        return False

def get_user_stats(user_id):
    """جلب إحصائيات المستخدم"""
    try:
        conn = sqlite3.connect('bot_data.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT compliance_checks, achievements, created_at, last_active
            FROM users WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'compliance_checks': result[0],
                'achievements': json.loads(result[1]) if result[1] else [],
                'created_at': result[2],
                'last_active': result[3]
            }
        else:
            return {
                'compliance_checks': 0,
                'achievements': [],
                'created_at': None,
                'last_active': None
            }
            
    except Exception as e:
        print(f"Get user stats error: {e}")
        return {'compliance_checks': 0, 'achievements': []}

def get_all_users_stats():
    """جلب إحصائيات جميع المستخدمين"""
    try:
        conn = sqlite3.connect('bot_data.db')
        cursor = conn.cursor()
        
        # إجمالي المستخدمين
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        # إجمالي فحوص الامتثال
        cursor.execute('SELECT SUM(compliance_checks) FROM users')
        total_checks = cursor.fetchone()[0] or 0
        
        # المستخدمين النشطين (آخر 30 يوم)
        cursor.execute('''
            SELECT COUNT(*) FROM users 
            WHERE last_active > datetime('now', '-30 days')
        ''')
        active_users = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_users': total_users,
            'total_compliance_checks': total_checks,
            'active_users_30d': active_users,
            'average_checks_per_user': total_checks / total_users if total_users > 0 else 0
        }
        
    except Exception as e:
        print(f"Get all users stats error: {e}")
        return {
            'total_users': 0,
            'total_compliance_checks': 0,
            'active_users_30d': 0,
            'average_checks_per_user': 0
        }
