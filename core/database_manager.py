import sqlite3
from pathlib import Path

DB_PATH = Path("bravebot.db")

# إنشاء الجداول لو مش موجودة
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # جدول المنتجات
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        platform TEXT,
        price REAL,
        url TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # جدول اللوجز (لـ compliance وغيره)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT,
        level TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

# إضافة منتج
def add_product(name, platform, price, url):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO products (name, platform, price, url) VALUES (?, ?, ?, ?)",
                (name, platform, price, url))
    conn.commit()
    conn.close()

# قراءة كل المنتجات
def get_products():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM products ORDER BY timestamp DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

# تسجيل أي حدث في اللوج
def add_log(message, level="INFO"):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO logs (message, level) VALUES (?, ?)", (message, level))
    conn.commit()
    conn.close()

# قراءة اللوجز
def get_logs(limit=50):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows

# استدعاء إنشاء الجداول أول ما الملف يشتغل
init_db()
