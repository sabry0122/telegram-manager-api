"""
API Server Configuration
تكوين خادم API - يمكن تعديله بسهولة
"""

# ===== إعدادات الخادم =====
API_HOST = "0.0.0.0"  # للسماح بالاتصالات من جميع الأجهزة على الشبكة
API_PORT = 8000
DEBUG_MODE = True  # للتطوير، غيره إلى False للإنتاج

# ===== إعدادات CORS =====
# للتطوير: السماح لجميع المصادر
CORS_ORIGINS = ["*"]
# للإنتاج: حدد نطاقات محددة
# CORS_ORIGINS = ["https://yourdomain.com", "https://api.yourdomain.com"]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]

# ===== إعدادات Session =====
# مدة صلاحية Session بالثواني (1 ساعة)
SESSION_TIMEOUT = 3600

# ===== إعدادات Telegram API =====
# هذه معرفات تجريبية - يجب استبدالها بمعرفاتك الخاصة من https://my.telegram.org
DEFAULT_API_ID = "39542130"
DEFAULT_API_HASH = "a993b66c4c03987095bc69a899db3633"

# ===== إعدادات قاعدة البيانات =====
DATABASE_PATH = "data/database/telegram_manager.db"

# ===== إعدادات Logging =====
LOG_LEVEL = "info"  # debug, info, warning, error
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ===== إعدادات Rate Limiting (للإنتاج) =====
ENABLE_RATE_LIMITING = False  # تفعيله في الإنتاج
RATE_LIMIT_CALLS = 10  # عدد الطلبات
RATE_LIMIT_PERIOD = 60  # في فترة زمنية (ثواني)

# ===== إعدادات الأمان =====
# للإنتاج: استخدم JWT tokens
USE_JWT_AUTH = False  # للتطوير
JWT_SECRET_KEY = "your-secret-key-change-this-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# ===== معلومات التطبيق =====
APP_NAME = "Telegram Manager API"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "REST API للربط مع تطبيق Android"

# ===== توثيق API =====
DOCS_URL = "/docs"  # واجهة Swagger UI
REDOC_URL = "/redoc"  # واجهة ReDoc البديلة
OPENAPI_URL = "/openapi.json"  # مواصفات OpenAPI

# ===== ملاحظات الأمان =====
"""
⚠️ تحذيرات للإنتاج:

1. غير DEFAULT_API_ID و DEFAULT_API_HASH بمعرفاتك الخاصة
2. فعل JWT_AUTH وغير JWT_SECRET_KEY
3. حدد CORS_ORIGINS بدقة
4. غير DEBUG_MODE إلى False
5. فعل RATE_LIMITING
6. استخدم HTTPS فقط
7. استخدم متغيرات البيئة للأسرار
8. راجع إعدادات الأمان

للحصول على API credentials الخاصة بك:
1. اذهب إلى: https://my.telegram.org
2. سجل الدخول برقمك
3. اذهب إلى "API Development Tools"
4. أنشئ تطبيق جديد
5. احصل على API_ID و API_HASH
6. استبدلهما هنا
"""

# ===== دالة للحصول على الإعدادات =====
def get_config():
    """
    الحصول على جميع الإعدادات كقاموس
    """
    return {
        "api_host": API_HOST,
        "api_port": API_PORT,
        "debug_mode": DEBUG_MODE,
        "cors_origins": CORS_ORIGINS,
        "session_timeout": SESSION_TIMEOUT,
        "app_name": APP_NAME,
        "app_version": APP_VERSION,
    }


def print_config():
    """
    طباعة الإعدادات الحالية
    """
    print("\n" + "="*50)
    print("⚙️  API Server Configuration")
    print("="*50)
    print(f"Host: {API_HOST}")
    print(f"Port: {API_PORT}")
    print(f"Debug Mode: {DEBUG_MODE}")
    print(f"CORS Origins: {CORS_ORIGINS}")
    print(f"Session Timeout: {SESSION_TIMEOUT}s")
    print(f"Rate Limiting: {'Enabled' if ENABLE_RATE_LIMITING else 'Disabled'}")
    print(f"JWT Auth: {'Enabled' if USE_JWT_AUTH else 'Disabled'}")
    print("="*50)
    
    if DEBUG_MODE:
        print("\n⚠️  Warning: Debug mode is ON!")
        print("   This is OK for development but MUST be OFF in production.")
    
    if DEFAULT_API_ID == "39542130":
        print("\n⚠️  Warning: Using default API credentials!")
        print("   Get your own from: https://my.telegram.org")
    
    print()


if __name__ == "__main__":
    print_config()
