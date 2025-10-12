from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Any, Dict
from aiogram.types import Message, CallbackQuery
import logging

class AuthenticationMiddleware(BaseMiddleware):
    """Middleware for checking user authentication"""
    
    def __init__(self, db_instance, config_instance):
        self.db = db_instance
        self.config = config_instance

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any]
    ) -> Any:
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
        # Import waiting_for_password from handlers
        try:
            from handlers import waiting_for_password
            if user and user.id in waiting_for_password:
                # User is waiting for password input - allow processing
                return await handler(event, data)
        except ImportError:
            # If we can't import, continue without checking
            pass
        
        # Check authentication in database
        if user and not self.db.is_user_authenticated(user.id):
            # User is not authenticated
            if isinstance(event, Message):
                await event.answer(
                    "🔒 To access the bot, run the /start command and enter the password."
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    "🔒 Session expired. Run /start to re-authenticate.",
                    show_alert=True
                )
            
            logging.warning(f"Unauthenticated access from user {user.id}")
            return  # Interrupt execution
        
        # User is authenticated, continue processing
        return await handler(event, data)
