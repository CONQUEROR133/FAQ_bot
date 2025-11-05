from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Any, Dict, Set
from aiogram.types import Message, CallbackQuery
import logging

class AuthenticationMiddleware(BaseMiddleware):
    """Middleware for checking user authentication."""
    
    def __init__(self, db_instance, config_instance, waiting_for_password: Set[int]):
        """Initialize the authentication middleware.
        
        Args:
            db_instance: Database instance for authentication checks
            config_instance: Configuration instance
            waiting_for_password: Set of user IDs waiting for password input
        """
        self.db = db_instance
        self.config = config_instance
        self.waiting_for_password = waiting_for_password

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any]
    ) -> Any:
        """Process the event and check user authentication.
        
        Args:
            handler: Next handler in the chain
            event: Telegram event (Message or CallbackQuery)
            data: Data dictionary to pass to handlers
            
        Returns:
            Any: Result of the handler execution or None if authentication failed
        """
        # Get user from event
        user = None
        if isinstance(event, (Message, CallbackQuery)):
            user = event.from_user
        
        if not user:
            return await handler(event, data)
        
        # Check commands that don't require authentication
        if isinstance(event, Message) and event.text:
            # Allow /start for everyone (needed for authentication)
            if event.text.strip() == '/start':
                return await handler(event, data)
        
        # Check if user is admin (admin doesn't need authentication)
        if user and user.id == self.config.ADMIN_ID:
            return await handler(event, data)
        
        # Check if user is waiting for password input
        if user and user.id in self.waiting_for_password:
            # User is waiting for password input - allow processing
            return await handler(event, data)
        
        # Check authentication in database
        if user and not self.db.is_user_authenticated(user.id):
            # User is not authenticated
            if isinstance(event, Message):
                await event.answer(
                    "🔒 Чтобы войти в бота, введи команду /start и укажи пароль."
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    "🔒 Сессия истекла. Введи /start для повторного входа.",
                    show_alert=True
                )
            
            logging.warning(f"Unauthenticated access from user {user.id}")
            return  # Interrupt execution
        
        # User is authenticated, continue processing
        return await handler(event, data)