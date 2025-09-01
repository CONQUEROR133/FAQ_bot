from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Any
from aiogram.types import Message, CallbackQuery, TelegramObject
from typing import Union
import logging

class AuthenticationMiddleware(BaseMiddleware):
    """Middleware для проверки аутентификации пользователей"""
    
    def __init__(self, db_instance, config_instance):
        self.db = db_instance
        self.config = config_instance

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
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
        if user.id == self.config.ADMIN_ID:
            return await handler(event, data)
        
        # Проверяем, ожидает ли пользователь ввода пароля
        # Импортируем waiting_for_password из handlers
        try:
            from handlers import waiting_for_password
            if user.id in waiting_for_password:
                # Пользователь ожидает ввода пароля - разрешаем обработку
                return await handler(event, data)
        except ImportError:
            # Если не можем импортировать, продолжаем без проверки
            pass
        
        # Проверяем аутентификацию в базе данных
        if not self.db.is_user_authenticated(user.id):
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