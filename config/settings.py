"""
إعدادات التطبيق العامة
"""

import os
import sys
from pathlib import Path

# تحديد المسار الأساسي بشكل صحيح للـ EXE والكود المصدري
if getattr(sys, 'frozen', False):
    # إذا كان التطبيق مبني كـ EXE
    # استخدم مجلد المستخدم بدلاً من المجلد المؤقت
    BASE_DIR = Path(os.path.expanduser('~')) / 'TelegramManager'
else:
    # إذا كان يعمل من الكود المصدري
    BASE_DIR = Path(__file__).resolve().parent.parent

# المسارات الأساسية
DATA_DIR = BASE_DIR / 'data'
DB_DIR = DATA_DIR / 'database'
SESSION_DIR = DATA_DIR / 'sessions'

# إنشاء المجلدات إذا لم تكن موجودة
DATA_DIR.mkdir(exist_ok=True, parents=True)
DB_DIR.mkdir(exist_ok=True, parents=True)
SESSION_DIR.mkdir(exist_ok=True, parents=True)

# قاعدة البيانات
DATABASE_PATH = DB_DIR / 'telegram_manager.db'

# إعدادات التطبيق
APP_NAME = "Telegram Manager"
APP_VERSION = "1.0.0"

# بيانات API المدمجة (مخفية عن المستخدم)
DEFAULT_API_ID = "39542130"
DEFAULT_API_HASH = "a993b66c4c03987095bc69a899db3633"

# إعدادات البحث
SEARCH_LIMIT = 50  # عدد النتائج القصوى للبحث
SEARCH_TIMEOUT = 30  # مهلة البحث بالثواني

# إعدادات الواجهة
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 800
WINDOW_DEFAULT_WIDTH = 1400
WINDOW_DEFAULT_HEIGHT = 950

# الألوان - الوضع الداكن
DARK_MODE_COLORS = {
    'background': '#1e1e1e',
    'surface': '#2d2d2d',
    'primary': '#0088cc',
    'secondary': '#00a0e9',
    'text': '#ffffff',
    'text_secondary': '#b0b0b0',
    'border': '#404040',
    'success': '#4caf50',
    'error': '#f44336',
    'warning': '#ff9800',
}
