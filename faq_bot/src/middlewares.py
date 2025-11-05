from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Any, Dict, Union
from aiogram.types import Message, CallbackQuery, TelegramObject

class DependenciesMiddleware(BaseMiddleware):
    """Middleware for injecting dependencies into handlers."""
    
    def __init__(self, db_instance: Any, faq_loader_instance: Any, config_instance: Any) -> None:
        """Initialize the middleware with dependencies.
        
        Args:
            db_instance: Database instance
            faq_loader_instance: FAQ loader instance
            config_instance: Configuration instance
        """
        self.db = db_instance
        self.faq_loader = faq_loader_instance
        self.config = config_instance

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Process the event and inject dependencies.
        
        Args:
            handler: Next handler in the chain
            event: Telegram event
            data: Data dictionary to pass to handlers
            
        Returns:
            Any: Result of the handler execution
        """
        # Add dependencies to data
        data["db"] = self.db
        data["faq_loader"] = self.faq_loader
        data["config"] = self.config
        
        return await handler(event, data)