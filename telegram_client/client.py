"""
عميل تليجرام باستخدام Telethon
"""

from telethon import TelegramClient, events, errors
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import Channel as TGChannel, Chat, User
from typing import List, Optional, Callable
import asyncio
from database.models import Channel, AccountInfo


class TelegramClientManager:
    """مدير عميل تليجرام"""

    def __init__(self, api_id: str, api_hash: str, session_path: str):
        self.api_id = int(api_id)
        self.api_hash = api_hash
        self.session_path = session_path
        self.client: Optional[TelegramClient] = None
        self.is_connected = False

    async def connect(self):
        """الاتصال بتليجرام"""
        try:
            if self.client is None:
                self.client = TelegramClient(
                    str(self.session_path),
                    self.api_id,
                    self.api_hash,
                    loop=asyncio.get_event_loop()  # استخدام الـ loop الحالي
                )
            
            if not self.is_connected:
                await self.client.connect()
                self.is_connected = True
            
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            import traceback
            traceback.print_exc()
            self.is_connected = False
            return False

    async def send_code_request(self, phone: str) -> bool:
        """طلب رمز التحقق"""
        try:
            await self.client.send_code_request(phone)
            return True
        except Exception as e:
            print(f"Code request error: {e}")
            raise

    async def sign_in(self, phone: str, code: str) -> bool:
        """تسجيل الدخول"""
        try:
            await self.client.sign_in(phone, code)
            return True
        except errors.SessionPasswordNeededError:
            # يتطلب كلمة مرور للتحقق بخطوتين
            raise Exception("Two-step verification password required")
        except Exception as e:
            print(f"Sign in error: {e}")
            raise

    async def sign_in_with_password(self, password: str) -> bool:
        """تسجيل الدخول بكلمة المرور (للتحقق بخطوتين)"""
        try:
            await self.client.sign_in(password=password)
            return True
        except Exception as e:
            print(f"Password sign in error: {e}")
            raise

    async def is_authorized(self) -> bool:
        """التحقق من حالة التفويض"""
        try:
            return await self.client.is_user_authorized()
        except:
            return False

    async def get_account_info(self) -> Optional[AccountInfo]:
        """الحصول على معلومات الحساب"""
        try:
            me = await self.client.get_me()
            return AccountInfo(
                user_id=me.id,
                first_name=me.first_name or "",
                last_name=me.last_name,
                username=me.username,
                phone=me.phone or "",
                is_premium=me.premium if hasattr(me, 'premium') else False
            )
        except Exception as e:
            print(f"Error getting account info: {e}")
            return None

    async def get_dialogs_count(self) -> dict:
        """الحصول على عدد القنوات والمجموعات"""
        try:
            dialogs = await self.client.get_dialogs()
            
            channels_count = 0
            groups_count = 0
            
            for dialog in dialogs:
                if isinstance(dialog.entity, TGChannel):
                    if dialog.entity.broadcast:
                        channels_count += 1
                    else:
                        groups_count += 1
                elif isinstance(dialog.entity, Chat):
                    groups_count += 1
            
            return {
                'channels': channels_count,
                'groups': groups_count,
                'total': channels_count + groups_count
            }
        except Exception as e:
            print(f"Error getting dialogs count: {e}")
            return {'channels': 0, 'groups': 0, 'total': 0}

    async def search_public_channels(
        self, 
        keyword: str, 
        limit: int = 50,
        progress_callback: Optional[Callable] = None
    ) -> List[Channel]:
        """البحث في القنوات والمجموعات العامة"""
        results = []
        
        try:
            # 1. البحث باستخدام username إذا كان يبدأ بـ @
            if keyword.startswith('@'):
                try:
                    entity = await self.client.get_entity(keyword)
                    channel = await self._entity_to_channel(entity)
                    if channel and channel.link:
                        results.append(channel)
                        if progress_callback:
                            progress_callback(len(results), limit)
                except Exception as e:
                    print(f"Error getting entity {keyword}: {e}")
            
            # 2. البحث في الحوارات الموجودة (القنوات المشترك فيها)
            try:
                async for dialog in self.client.iter_dialogs():
                    if len(results) >= limit:
                        break
                    
                    entity = dialog.entity
                    
                    # تحقق من أن الكيان قناة أو مجموعة
                    if isinstance(entity, (TGChannel, Chat)):
                        title = getattr(entity, 'title', '').lower()
                        username = getattr(entity, 'username', '')
                        if username:
                            username = username.lower()
                        
                        # البحث في العنوان أو اسم المستخدم
                        keyword_lower = keyword.lower().replace('@', '')
                        if keyword_lower in title or (username and keyword_lower in username):
                            channel = await self._entity_to_channel(entity)
                            if channel:
                                # إضافة جميع القنوات (عامة وخاصة من القنوات المشترك فيها)
                                results.append(channel)
                                
                                if progress_callback:
                                    progress_callback(len(results), limit)
            except Exception as e:
                print(f"Error searching dialogs: {e}")
            
            # 3. البحث العام في تليجرام
            try:
                from telethon.tl.functions.contacts import SearchRequest
                from telethon.tl.types import InputMessagesFilterEmpty
                
                search_result = await self.client(SearchRequest(
                    q=keyword,
                    limit=min(limit, 10)
                ))
                
                if hasattr(search_result, 'chats'):
                    for chat in search_result.chats:
                        if len(results) >= limit:
                            break
                        
                        if isinstance(chat, (TGChannel, Chat)):
                            # تجنب التكرار
                            chat_id = chat.id
                            if not any(r.telegram_id == chat_id for r in results):
                                channel = await self._entity_to_channel(chat)
                                if channel:
                                    results.append(channel)
                                    
                                    if progress_callback:
                                        progress_callback(len(results), limit)
            except Exception as e:
                print(f"Error in global search: {e}")
            
            return results
            
        except Exception as e:
            print(f"Search error: {e}")
            import traceback
            traceback.print_exc()
            return results

    async def _entity_to_channel(self, entity) -> Optional[Channel]:
        """تحويل كيان تليجرام إلى نموذج قناة"""
        try:
            if not isinstance(entity, (TGChannel, Chat)):
                return None
            
            # تحديد النوع
            if isinstance(entity, TGChannel):
                channel_type = 'channel' if entity.broadcast else 'group'
            else:
                channel_type = 'group'
            
            # الحصول على معلومات إضافية
            members_count = 0
            description = None
            
            try:
                if isinstance(entity, TGChannel):
                    full = await self.client(GetFullChannelRequest(entity))
                    members_count = full.full_chat.participants_count or 0
                    description = full.full_chat.about or None
                elif isinstance(entity, Chat):
                    members_count = entity.participants_count or 0
            except:
                pass
            
            # إنشاء الرابط
            username = getattr(entity, 'username', None)
            link = f"https://t.me/{username}" if username else None
            
            # إنشاء نموذج القناة
            return Channel(
                telegram_id=entity.id,
                username=username,
                title=getattr(entity, 'title', ''),
                type=channel_type,
                members_count=members_count,
                description=description,
                link=link
            )
            
        except Exception as e:
            print(f"Error converting entity: {e}")
            return None

    async def get_channel_details(self, username: str) -> Optional[Channel]:
        """الحصول على تفاصيل قناة معينة"""
        try:
            entity = await self.client.get_entity(username)
            return await self._entity_to_channel(entity)
        except Exception as e:
            print(f"Error getting channel details: {e}")
            return None

    async def disconnect(self):
        """قطع الاتصال"""
        if self.client and self.is_connected:
            await self.client.disconnect()
            self.is_connected = False

    def run_until_disconnected(self):
        """تشغيل العميل حتى يتم قطع الاتصال"""
        if self.client:
            self.client.run_until_disconnected()
