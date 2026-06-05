"""
REST API Server للربط مع تطبيق Android
يستخدم FastAPI لإنشاء endpoints للتطبيق
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import asyncio
from pathlib import Path
import uvicorn
import secrets

from telegram_client.client import TelegramClientManager
from telegram_client.session_manager import SessionManager
from database.db_manager import DatabaseManager
from database.models import Channel, AccountInfo
from api_config import (
    API_HOST, API_PORT, DEBUG_MODE,
    CORS_ORIGINS, CORS_ALLOW_CREDENTIALS, CORS_ALLOW_METHODS, CORS_ALLOW_HEADERS,
    APP_NAME, APP_VERSION, APP_DESCRIPTION,
    DOCS_URL, REDOC_URL, OPENAPI_URL,
    print_config
)

# إنشاء التطبيق
app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    docs_url=DOCS_URL,
    redoc_url=REDOC_URL,
    openapi_url=OPENAPI_URL
)

# إضافة CORS للسماح للتطبيق بالاتصال
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
)

# تخزين الجلسات النشطة
active_sessions: Dict[str, TelegramClientManager] = {}
# تخزين معلومات الهاتف لكل جلسة
session_phones: Dict[str, str] = {}
session_manager = SessionManager()
db_manager = DatabaseManager()


# ===== نماذج البيانات =====

class PhoneRequest(BaseModel):
    phone: str
    api_id: str
    api_hash: str


class CodeRequest(BaseModel):
    session_token: str
    code: str


class SearchRequest(BaseModel):
    session_token: str
    query: str
    limit: int = 50


class SessionResponse(BaseModel):
    session_token: str
    message: str


class AccountInfoResponse(BaseModel):
    user_id: int
    first_name: str
    last_name: Optional[str]
    username: Optional[str]
    phone: str
    is_premium: bool


class ChannelResponse(BaseModel):
    telegram_id: int
    username: Optional[str]
    title: str
    type: str
    members_count: int
    description: Optional[str]
    link: Optional[str]


class DialogsCountResponse(BaseModel):
    channels: int
    groups: int
    total: int


# ===== وظائف مساعدة =====

def get_client(session_token: str) -> TelegramClientManager:
    """الحصول على العميل من الجلسة"""
    if session_token not in active_sessions:
        raise HTTPException(status_code=401, detail="جلسة غير صالحة أو منتهية")
    return active_sessions[session_token]


# ===== Endpoints =====

@app.get("/")
async def root():
    """الصفحة الرئيسية"""
    return {
        "app": "Telegram Manager API",
        "version": "1.0.0",
        "status": "running"
    }


@app.post("/auth/send-code", response_model=SessionResponse)
async def send_code(request: PhoneRequest):
    """
    إرسال رمز التحقق إلى رقم الهاتف
    
    Returns:
        session_token: رمز الجلسة للاستخدام في الطلبات التالية
    """
    try:
        # إنشاء session token فريد
        session_token = secrets.token_urlsafe(32)
        
        # إنشاء مسار الجلسة
        session_path = session_manager.get_session_path(request.phone)
        
        # إنشاء العميل
        client = TelegramClientManager(
            api_id=request.api_id,
            api_hash=request.api_hash,
            session_path=str(session_path)
        )
        
        # الاتصال وإرسال الكود
        connected = await client.connect()
        if not connected:
            raise HTTPException(status_code=500, detail="فشل الاتصال بـ Telegram. تأكد من اتصال الإنترنت.")
        
        # التأكد من الاتصال
        await asyncio.sleep(0.5)  # انتظار صغير للتأكد
        
        try:
            await client.send_code_request(request.phone)
        except Exception as code_error:
            # محاولة إعادة الاتصال
            await client.disconnect()
            await asyncio.sleep(1)
            await client.connect()
            await client.send_code_request(request.phone)
        
        # حفظ الجلسة
        active_sessions[session_token] = client
        # حفظ رقم الهاتف مع الجلسة
        session_phones[session_token] = request.phone
        
        # حفظ بيانات الاعتماد
        session_manager.save_credentials(request.phone, request.api_id, request.api_hash)
        
        return SessionResponse(
            session_token=session_token,
            message="تم إرسال رمز التحقق بنجاح"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"خطأ: {str(e)}")


@app.post("/auth/verify-code")
async def verify_code(request: CodeRequest):
    """
    التحقق من رمز التحقق وتسجيل الدخول
    """
    try:
        client = get_client(request.session_token)
        
        # الحصول على رقم الهاتف من الجلسة
        phone = session_phones.get(request.session_token)
        if not phone:
            raise HTTPException(status_code=400, detail="رقم الهاتف غير موجود في الجلسة")
        
        # محاولة تسجيل الدخول
        await client.sign_in(phone=phone, code=request.code)
        
        return {"message": "تم تسجيل الدخول بنجاح"}
        
    except Exception as e:
        if "Two-step" in str(e):
            raise HTTPException(status_code=403, detail="يتطلب كلمة مرور للتحقق بخطوتين")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/auth/check", response_model=Dict[str, bool])
async def check_auth(session_token: str):
    """
    التحقق من حالة التفويض
    """
    try:
        client = get_client(session_token)
        is_authorized = await client.is_authorized()
        
        return {"authorized": is_authorized}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/account/info", response_model=AccountInfoResponse)
async def get_account_info(session_token: str):
    """
    الحصول على معلومات الحساب
    """
    try:
        client = get_client(session_token)
        account_info = await client.get_account_info()
        
        if not account_info:
            raise HTTPException(status_code=404, detail="لم يتم العثور على معلومات الحساب")
        
        return AccountInfoResponse(
            user_id=account_info.user_id,
            first_name=account_info.first_name,
            last_name=account_info.last_name,
            username=account_info.username,
            phone=account_info.phone,
            is_premium=account_info.is_premium
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/dialogs/count", response_model=DialogsCountResponse)
async def get_dialogs_count(session_token: str):
    """
    الحصول على عدد القنوات والمجموعات
    """
    try:
        client = get_client(session_token)
        counts = await client.get_dialogs_count()
        
        return DialogsCountResponse(
            channels=counts['channels'],
            groups=counts['groups'],
            total=counts['total']
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/search/channels", response_model=List[ChannelResponse])
async def search_channels(request: SearchRequest):
    """
    البحث في القنوات والمجموعات
    """
    try:
        client = get_client(request.session_token)
        
        # البحث
        channels = await client.search_public_channels(
            keyword=request.query,
            limit=request.limit
        )
        
        # حفظ النتائج في قاعدة البيانات
        for channel in channels:
            db_manager.add_channel(channel)
        
        # حفظ سجل البحث
        db_manager.add_search_history(request.query, len(channels))
        
        # تحويل إلى response
        return [
            ChannelResponse(
                telegram_id=ch.telegram_id,
                username=ch.username,
                title=ch.title,
                type=ch.type,
                members_count=ch.members_count,
                description=ch.description,
                link=ch.link
            )
            for ch in channels
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"خطأ: {str(e)}")


@app.get("/channels/history", response_model=List[ChannelResponse])
async def get_channels_history(skip: int = 0, limit: int = 50):
    """
    الحصول على سجل القنوات المحفوظة
    """
    try:
        channels = db_manager.get_all_channels(skip=skip, limit=limit)
        
        return [
            ChannelResponse(
                telegram_id=ch.telegram_id,
                username=ch.username,
                title=ch.title,
                type=ch.type,
                members_count=ch.members_count,
                description=ch.description,
                link=ch.link
            )
            for ch in channels
        ]
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/auth/logout")
async def logout(session_token: str):
    """
    تسجيل الخروج وإنهاء الجلسة
    """
    try:
        if session_token in active_sessions:
            client = active_sessions[session_token]
            await client.disconnect()
            del active_sessions[session_token]
            
        # حذف معلومات الهاتف
        if session_token in session_phones:
            del session_phones[session_token]
        
        return {"message": "تم تسجيل الخروج بنجاح"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.on_event("startup")
async def startup_event():
    """تهيئة عند بدء التشغيل"""
    print("\n🚀 Starting API Server...")
    print_config()
    print(f"📡 Server URL: http://{API_HOST}:{API_PORT}")
    print(f"📚 API Docs: http://localhost:{API_PORT}{DOCS_URL}")
    print("✅ API Server started successfully!\n")


@app.on_event("shutdown")
async def shutdown_event():
    """تنظيف عند الإيقاف"""
    print("🛑 Shutting down API Server...")
    
    # قطع اتصال جميع الجلسات النشطة
    for client in active_sessions.values():
        try:
            await client.disconnect()
        except:
            pass
    
    active_sessions.clear()
    session_phones.clear()


if __name__ == "__main__":
    # تشغيل الخادم
    uvicorn.run(
        "api_server:app",
        host=API_HOST,
        port=API_PORT,
        reload=DEBUG_MODE,
        log_level="info"
    )
