from typing import Callable, Awaitable, Any, Dict
import logging

# Define BaseMiddleware class that works in all environments
class BaseMiddleware:
    """Base class for middleware"""
    async def __call__(
        self, 
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]], 
        event: Any, 
        data: Dict[str, Any]
    ) -> Any:
        return await handler(event, data)

# Try to import aiogram classes
try:
    from aiogram.types import Message, CallbackQuery, TelegramObject
except ImportError:
    # Fallback classes for development environments
    class Message:
        def __init__(self):
            self.from_user = None
            self.text = ""
        
        async def answer(self, text, *args, **kwargs):
            pass
    
    class CallbackQuery:
        def __init__(self):
            self.from_user = None
            
        async def answer(self, text, show_alert=False, *args, **kwargs):
            pass
        
    class TelegramObject:
        pass

class AuthenticationMiddleware(BaseMiddleware):
    """Middleware для проверки аутентификации пользователей"""
    
    def __init__(self, db_instance, config_instance):
        self.db = db_instance
        self.config = config_instance

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any]
    ) -> Any:
        # Получаем пользователя из события
        user = None
        if isinstance(event, (Message, CallbackQuery)):
            user = event.from_user
        
        if not user:
            return await handler(event, data)
        
        # Проверяем команды, которые не требуют аутентификации
        if isinstance(event, Message) and event.text:
            # Разрешаем /start для всех (нужно для аутентификации)
            if event.text.strip() == '/start':
                return await handler(event, data)
        
        # Проверяем, является ли пользователь админом (админ не нуждается в аутентификации)
        if user and user.id == self.config.ADMIN_ID:
            return await handler(event, data)
        
        # Проверяем, ожидает ли пользователь ввода пароля
        # Импортируем waiting_for_password из handlers
        try:
            from handlers import waiting_for_password
            if user and user.id in waiting_for_password:
                # Пользователь ожидает ввода пароля - разрешаем обработку
                return await handler(event, data)
        except ImportError:
            # Если не можем импортировать, продолжаем без проверки
            pass
        
        # Проверяем аутентификацию в базе данных
        if user and not self.db.is_user_authenticated(user.id):
            # Пользователь не аутентифицирован
            if isinstance(event, Message):
                await event.answer(
                    "🔒 Для доступа к боту выполните команду /start и введите пароль."
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    "🔒 Сессия истекла. Выполните /start для повторной аутентификации.",
                    show_alert=True
                )
            
            logging.warning(f"Неаутентифицированный доступ от пользователя {user.id}")
            return  # Прерываем выполнение
        
        # Пользователь аутентифицирован, продолжаем обработку
        return await handler(event, data)