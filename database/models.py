"""
نماذج البيانات
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Channel:
    """نموذج القناة أو المجموعة"""
    id: Optional[int] = None
    telegram_id: Optional[int] = None
    username: Optional[str] = None
    title: str = ""
    type: str = ""  # 'channel' or 'group'
    members_count: int = 0
    description: Optional[str] = None
    link: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self):
        """تحويل إلى قاموس"""
        return {
            'id': self.id,
            'telegram_id': self.telegram_id,
            'username': self.username,
            'title': self.title,
            'type': self.type,
            'members_count': self.members_count,
            'description': self.description,
            'link': self.link,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }


@dataclass
class SearchHistory:
    """نموذج سجل البحث"""
    id: Optional[int] = None
    keyword: str = ""
    results_count: int = 0
    search_date: Optional[datetime] = None

    def to_dict(self):
        """تحويل إلى قاموس"""
        return {
            'id': self.id,
            'keyword': self.keyword,
            'results_count': self.results_count,
            'search_date': self.search_date,
        }


@dataclass
class AccountInfo:
    """معلومات الحساب"""
    user_id: Optional[int] = None
    first_name: str = ""
    last_name: Optional[str] = None
    username: Optional[str] = None
    phone: str = ""
    is_premium: bool = False
