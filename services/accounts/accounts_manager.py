#!/usr/bin/env python3
"""
👥 Multi-Account Manager
========================
إدارة الحسابات المتعددة لـ Amazon/eBay/Trading
"""

import os
import json
import sqlite3
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from cryptography.fernet import Fernet
from dataclasses import dataclass, asdict

@dataclass
class Account:
    id: str
    name: str
    platform: str  # amazon, ebay, binance, coinbase, etc.
    credentials: Dict[str, str]  # encrypted
    is_active: bool
    created_at: datetime
    last_used: datetime
    metadata: Dict[str, Any]

class AccountsManager:
    def __init__(self, db_path: str = "bravebot.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        self._init_database()
    
    def _get_or_create_encryption_key(self) -> bytes:
        """إنشاء أو استرداد مفتاح التشفير"""
        key_file = "encryption.key"
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def _init_database(self):
        """إنشاء جداول الحسابات"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    encrypted_credentials TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP,
                    metadata TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS account_usage_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN,
                    details TEXT,
                    FOREIGN KEY (account_id) REFERENCES accounts (id)
                )
            """)
            
            conn.commit()
    
    def add_account(
        self,
        name: str,
        platform: str,
        credentials: Dict[str, str],
        metadata: Dict[str, Any] = None
    ) -> str:
        """إضافة حساب جديد"""
        
        account_id = f"{platform}_{name}_{int(datetime.now().timestamp())}"
        
        # تشفير الاعتمادات
        encrypted_creds = self.cipher.encrypt(
            json.dumps(credentials).encode()
        )
        
        account = Account(
            id=account_id,
            name=name,
            platform=platform,
            credentials=credentials,  # سيتم تشفيرها
            is_active=True,
            created_at=datetime.now(),
            last_used=datetime.now(),
            metadata=metadata or {}
        )
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO accounts 
                (id, name, platform, encrypted_credentials, is_active, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                account_id,
                name,
                platform,
                encrypted_creds.decode(),
                True,
                json.dumps(metadata or {})
            ))
            conn.commit()
        
        self.logger.info(f"Account added: {account_id} ({platform})")
        return account_id
    
    def get_account(self, account_id: str) -> Optional[Account]:
        """جلب حساب معين"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM accounts WHERE id = ? AND is_active = 1
            """, (account_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # فك تشفير الاعتمادات
            try:
                decrypted_creds = self.cipher.decrypt(row[3].encode())
                credentials = json.loads(decrypted_creds.decode())
            except Exception:
                self.logger.error(f"Failed to decrypt credentials for {account_id}")
                return None
            
            return Account(
                id=row[0],
                name=row[1],
                platform=row[2],
                credentials=credentials,
                is_active=bool(row[4]),
                created_at=datetime.fromisoformat(row[5]),
                last_used=datetime.fromisoformat(row[6]) if row[6] else None,
                metadata=json.loads(row[7]) if row[7] else {}
            )
    
    def get_accounts_by_platform(self, platform: str) -> List[Account]:
        """جلب جميع حسابات منصة معينة"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM accounts 
                WHERE platform = ? AND is_active = 1
                ORDER BY last_used DESC
            """, (platform,))
            
            accounts = []
            for row in cursor.fetchall():
                try:
                    decrypted_creds = self.cipher.decrypt(row[3].encode())
                    credentials = json.loads(decrypted_creds.decode())
                    
                    accounts.append(Account(
                        id=row[0],
                        name=row[1],
                        platform=row[2],
                        credentials=credentials,
                        is_active=bool(row[4]),
                        created_at=datetime.fromisoformat(row[5]),
                        last_used=datetime.fromisoformat(row[6]) if row[6] else None,
                        metadata=json.loads(row[7]) if row[7] else {}
                    ))
                except Exception:
                    continue
            
            return accounts
    
    def update_last_used(self, account_id: str):
        """تحديث آخر استخدام للحساب"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE accounts 
                SET last_used = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (account_id,))
            conn.commit()
    
    def log_account_usage(
        self,
        account_id: str,
        action: str,
        success: bool,
        details: str = None
    ):
        """تسجيل استخدام الحساب"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO account_usage_logs 
                (account_id, action, success, details)
                VALUES (?, ?, ?, ?)
            """, (account_id, action, success, details))
            conn.commit()
        
        # تحديث آخر استخدام
        self.update_last_used(account_id)
    
    def get_account_stats(self, account_id: str) -> Dict[str, Any]:
        """إحصائيات الحساب"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # إجمالي الاستخدام
            cursor.execute("""
                SELECT COUNT(*) as total_uses,
                       SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_uses,
                       MAX(timestamp) as last_activity
                FROM account_usage_logs 
                WHERE account_id = ?
            """, (account_id,))
            
            stats = cursor.fetchone()
            
            return {
                'total_uses': stats[0] if stats else 0,
                'successful_uses': stats[1] if stats else 0,
                'success_rate': (stats[1] / stats[0] * 100) if stats and stats[0] > 0 else 0,
                'last_activity': stats[2] if stats else None
            }
    
    def deactivate_account(self, account_id: str) -> bool:
        """إلغاء تفعيل حساب"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE accounts 
                SET is_active = 0
                WHERE id = ?
            """, (account_id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                self.logger.info(f"Account deactivated: {account_id}")
                return True
            
            return False
    
    def get_all_platforms(self) -> List[str]:
        """جلب جميع المنصات المتاحة"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT platform 
                FROM accounts 
                WHERE is_active = 1
            """)
            
            return [row[0] for row in cursor.fetchall()]

# تصدير الفئة
__all__ = ['AccountsManager', 'Account']