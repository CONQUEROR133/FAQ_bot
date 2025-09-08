from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Any
from aiogram.types import Message, CallbackQuery, TelegramObject
from typing import Union

class DependenciesMiddleware(BaseMiddleware):
    def __init__(self, db_instance, faq_loader_instance, config_instance):
        self.db = db_instance
        self.faq_loader = faq_loader_instance
        self.config = config_instance

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
    ) -> Any:
        # Добавляем зависимости в data
        data["db"] = self.db
        data["faq_loader"] = self.faq_loader
        data["config"] = self.config
        
        return await handler(event, data)