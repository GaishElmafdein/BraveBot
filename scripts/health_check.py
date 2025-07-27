#!/usr/bin/env python3
"""
Health check script for Docker container
"""

import sys
import os
import sqlite3
import requests

def check_database():
    """Check if database is accessible"""
    try:
        conn = sqlite3.connect('bravebot.db', timeout=5)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        return True
    except Exception:
        return False

def check_telegram_api():
    """Check if Telegram API is reachable"""
    try:
        token = os.getenv('TELEGRAM_TOKEN')
        if not token:
            return False
        
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        return response.status_code == 200
    except Exception:
        return False

if __name__ == "__main__":
    checks = [
        ("Database", check_database()),
        ("Telegram API", check_telegram_api()),
    ]
    
    all_healthy = True
    for name, status in checks:
        if status:
            print(f"✅ {name}: OK")
        else:
            print(f"❌ {name}: FAILED")
            all_healthy = False
    
    sys.exit(0 if all_healthy else 1)
