"""
إدارة جلسات تليجرام مع التشفير
"""

import os
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet
from config.settings import SESSION_DIR


class SessionManager:
    """مدير الجلسات مع التشفير"""

    def __init__(self):
        self.session_dir = SESSION_DIR
        self.key_file = self.session_dir / '.key'
        self.key = self._load_or_create_key()
        self.cipher = Fernet(self.key)

    def _load_or_create_key(self) -> bytes:
        """تحميل أو إنشاء مفتاح التشفير"""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            return key

    def get_session_path(self, phone: str) -> Path:
        """الحصول على مسار ملف الجلسة"""
        # إزالة الرموز غير المرغوبة من رقم الهاتف
        clean_phone = ''.join(c for c in phone if c.isdigit())
        return self.session_dir / f'session_{clean_phone}.session'

    def encrypt_data(self, data: bytes) -> bytes:
        """تشفير البيانات"""
        return self.cipher.encrypt(data)

    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """فك تشفير البيانات"""
        return self.cipher.decrypt(encrypted_data)

    def save_credentials(self, phone: str, api_id: str, api_hash: str):
        """حفظ بيانات الاعتماد بشكل مشفر"""
        # تنظيف رقم الهاتف
        clean_phone = ''.join(c for c in phone if c.isdigit())
        credentials_file = self.session_dir / f'cred_{clean_phone}.enc'
        data = f'{api_id}|{api_hash}'.encode()
        encrypted = self.encrypt_data(data)
        
        with open(credentials_file, 'wb') as f:
            f.write(encrypted)
        
        print(f"✓ تم حفظ بيانات الاعتماد: {credentials_file}")

    def load_credentials(self, phone: str) -> Optional[tuple]:
        """تحميل بيانات الاعتماد"""
        # تنظيف رقم الهاتف
        clean_phone = ''.join(c for c in phone if c.isdigit())
        credentials_file = self.session_dir / f'cred_{clean_phone}.enc'
        
        if not credentials_file.exists():
            print(f"✗ لا توجد بيانات اعتماد محفوظة: {credentials_file}")
            return None
        
        try:
            with open(credentials_file, 'rb') as f:
                encrypted = f.read()
            
            decrypted = self.decrypt_data(encrypted)
            data = decrypted.decode()
            api_id, api_hash = data.split('|')
            print(f"✓ تم تحميل بيانات الاعتماد بنجاح")
            return api_id, api_hash
        except Exception as e:
            print(f"✗ خطأ في تحميل بيانات الاعتماد: {e}")
            return None

    def session_exists(self, phone: str) -> bool:
        """التحقق من وجود جلسة محفوظة"""
        clean_phone = ''.join(c for c in phone if c.isdigit())
        session_path = self.session_dir / f'session_{clean_phone}.session'
        credentials_file = self.session_dir / f'cred_{clean_phone}.enc'
        return session_path.exists() and credentials_file.exists()

    def delete_session(self, phone: str):
        """حذف الجلسة وبيانات الاعتماد"""
        clean_phone = ''.join(c for c in phone if c.isdigit())
        session_path = self.session_dir / f'session_{clean_phone}.session'
        credentials_file = self.session_dir / f'cred_{clean_phone}.enc'
        
        if session_path.exists():
            os.remove(session_path)
            print(f"✓ تم حذف ملف الجلسة")
        if credentials_file.exists():
            os.remove(credentials_file)
            print(f"✓ تم حذف بيانات الاعتماد")
