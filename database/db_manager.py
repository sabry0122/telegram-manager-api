"""
مدير قاعدة البيانات SQLite
"""

import sqlite3
from typing import List, Optional
from datetime import datetime
from config.settings import DATABASE_PATH
from database.models import Channel, SearchHistory


class DatabaseManager:
    """مدير قاعدة البيانات"""

    def __init__(self):
        self.db_path = str(DATABASE_PATH)
        self.init_database()

    def get_connection(self):
        """إنشاء اتصال جديد بقاعدة البيانات"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """إنشاء الجداول الأساسية"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # جدول القنوات والمجموعات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                username TEXT,
                title TEXT NOT NULL,
                type TEXT NOT NULL,
                members_count INTEGER DEFAULT 0,
                description TEXT,
                link TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # جدول سجل البحث
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT NOT NULL,
                results_count INTEGER DEFAULT 0,
                search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # إنشاء الفهارس لتسريع البحث
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_channels_telegram_id 
            ON channels(telegram_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_channels_username 
            ON channels(username)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_channels_title 
            ON channels(title)
        ''')

        conn.commit()
        conn.close()

    def add_channel(self, channel: Channel) -> bool:
        """إضافة أو تحديث قناة"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO channels 
                (telegram_id, username, title, type, members_count, description, link, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                channel.telegram_id,
                channel.username,
                channel.title,
                channel.type,
                channel.members_count,
                channel.description,
                channel.link,
                datetime.now()
            ))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding channel: {e}")
            return False

    def add_channels_bulk(self, channels: List[Channel]) -> int:
        """إضافة عدة قنوات دفعة واحدة"""
        added_count = 0
        for channel in channels:
            if self.add_channel(channel):
                added_count += 1
        return added_count

    def get_channel_by_telegram_id(self, telegram_id: int) -> Optional[Channel]:
        """الحصول على قناة بواسطة معرف تليجرام"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM channels WHERE telegram_id = ?', (telegram_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return Channel(
                id=row['id'],
                telegram_id=row['telegram_id'],
                username=row['username'],
                title=row['title'],
                type=row['type'],
                members_count=row['members_count'],
                description=row['description'],
                link=row['link'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
        return None

    def search_channels(self, keyword: str) -> List[Channel]:
        """البحث في القنوات المحفوظة"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM channels 
            WHERE title LIKE ? OR description LIKE ? OR username LIKE ?
            ORDER BY members_count DESC
        ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

        rows = cursor.fetchall()
        conn.close()

        channels = []
        for row in rows:
            channels.append(Channel(
                id=row['id'],
                telegram_id=row['telegram_id'],
                username=row['username'],
                title=row['title'],
                type=row['type'],
                members_count=row['members_count'],
                description=row['description'],
                link=row['link'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            ))
        return channels

    def get_all_channels(self, limit: int = 100) -> List[Channel]:
        """الحصول على جميع القنوات"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM channels 
            ORDER BY updated_at DESC 
            LIMIT ?
        ''', (limit,))

        rows = cursor.fetchall()
        conn.close()

        channels = []
        for row in rows:
            channels.append(Channel(
                id=row['id'],
                telegram_id=row['telegram_id'],
                username=row['username'],
                title=row['title'],
                type=row['type'],
                members_count=row['members_count'],
                description=row['description'],
                link=row['link'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            ))
        return channels

    def add_search_history(self, keyword: str, results_count: int) -> bool:
        """إضافة سجل بحث"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO search_history (keyword, results_count)
                VALUES (?, ?)
            ''', (keyword, results_count))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding search history: {e}")
            return False

    def get_search_history(self, limit: int = 50) -> List[SearchHistory]:
        """الحصول على سجل البحث"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM search_history 
            ORDER BY search_date DESC 
            LIMIT ?
        ''', (limit,))

        rows = cursor.fetchall()
        conn.close()

        history = []
        for row in rows:
            history.append(SearchHistory(
                id=row['id'],
                keyword=row['keyword'],
                results_count=row['results_count'],
                search_date=row['search_date']
            ))
        return history

    def get_statistics(self) -> dict:
        """الحصول على إحصائيات"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # عدد القنوات
        cursor.execute('SELECT COUNT(*) FROM channels WHERE type = "channel"')
        channels_count = cursor.fetchone()[0]

        # عدد المجموعات
        cursor.execute('SELECT COUNT(*) FROM channels WHERE type = "group"')
        groups_count = cursor.fetchone()[0]

        # عدد عمليات البحث
        cursor.execute('SELECT COUNT(*) FROM search_history')
        searches_count = cursor.fetchone()[0]

        conn.close()

        return {
            'channels_count': channels_count,
            'groups_count': groups_count,
            'searches_count': searches_count,
            'total_saved': channels_count + groups_count
        }
