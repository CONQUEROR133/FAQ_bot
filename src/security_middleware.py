import time
import logging
from typing import Dict, Any, Callable, Awaitable, Optional, Set
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject, User

from config import SecurityValidator, config

logger = logging.getLogger(__name__)


@dataclass
class UserActivity:
    """Track user activity for rate limiting and monitoring."""
    user_id: int
    requests_per_minute: deque = field(default_factory=lambda: deque(maxlen=60))
    requests_per_hour: deque = field(default_factory=lambda: deque(maxlen=3600))
    total_requests: int = 0
    suspicious_activity_count: int = 0
    last_activity: datetime = field(default_factory=datetime.now)
    is_blocked: bool = False
    block_until: Optional[datetime] = None
    
    def add_request(self, timestamp: Optional[datetime] = None) -> None:
        """Add a request to the activity tracking."""
        if timestamp is None:
            timestamp = datetime.now()
        
        self.requests_per_minute.append(timestamp)
        self.requests_per_hour.append(timestamp)
        self.total_requests += 1
        self.last_activity = timestamp
    
    def get_requests_in_window(self, window_minutes: int) -> int:
        """Get number of requests in the specified time window."""
        cutoff = datetime.now() - timedelta(minutes=window_minutes)
        
        if window_minutes <= 60:
            return sum(1 for ts in self.requests_per_minute if ts > cutoff)
        else:
            return sum(1 for ts in self.requests_per_hour if ts > cutoff)
    
    def is_rate_limited(self) -> bool:
        """Check if user is currently rate limited."""
        if self.is_blocked and self.block_until:
            if datetime.now() < self.block_until:
                return True
            else:
                # Unblock user
                self.is_blocked = False
                self.block_until = None
        
        # Check minute rate limit
        requests_per_minute = self.get_requests_in_window(1)
        if requests_per_minute > config.security.max_requests_per_minute:
            return True
        
        # Check hour rate limit
        requests_per_hour = self.get_requests_in_window(60)
        if requests_per_hour > config.security.max_requests_per_hour:
            return True
        
        return False
    
    def add_suspicious_activity(self) -> None:
        """Record suspicious activity."""
        self.suspicious_activity_count += 1
        
        # Auto-block after too many suspicious activities
        if self.suspicious_activity_count >= 5:
            self.block_user(minutes=30)
    
    def block_user(self, minutes: int = 60) -> None:
        """Block user for specified duration."""
        self.is_blocked = True
        self.block_until = datetime.now() + timedelta(minutes=minutes)
        logger.warning(f"User {self.user_id} blocked for {minutes} minutes")


class SecurityMiddleware(BaseMiddleware):
    """Comprehensive security middleware for the FAQ bot."""
    
    def __init__(self, db_instance, config_instance):
        """Initialize security middleware."""
        self.db = db_instance
        self.config = config_instance
        self.user_activities: Dict[int, UserActivity] = {}
        self.validator = SecurityValidator()
        
        # Suspicious patterns to detect
        self.suspicious_patterns = [
            'admin', 'root', 'password', 'hack', 'exploit',
            'injection', 'script', 'eval', 'exec'
        ]
        
        # Known bot/spam indicators
        self.spam_indicators = [
            'http://', 'https://', 'www.', '.com', '.ru', '.org',
            'telegram.me', 't.me', '@', 'channel', 'group'
        ]
        
        logger.info("Security middleware initialized")
    
    def get_user_activity(self, user_id: int) -> UserActivity:
        """Get or create user activity tracking."""
        if user_id not in self.user_activities:
            self.user_activities[user_id] = UserActivity(user_id=user_id)
        return self.user_activities[user_id]
    
    def validate_user(self, user: Optional[User]) -> bool:
        """Validate user object for suspicious indicators."""
        if not user:
            return False
        
        # Check for suspicious usernames
        if user.username:
            username_lower = user.username.lower()
            if any(pattern in username_lower for pattern in self.suspicious_patterns):
                logger.warning(f"Suspicious username detected: {user.username}")
                return False
        
        # Check for bot indicators in first/last name
        full_name = f"{user.first_name or ''} {user.last_name or ''}".lower()
        if any(indicator in full_name for indicator in ['bot', 'spam', 'admin']):
            logger.warning(f"Suspicious name detected: {full_name.strip()}")
            return False
        
        return True
    
    def validate_message_content(self, text: str, user_id: int) -> bool:
        """Validate message content for security threats."""
        if not text:
            return True
        
        # Basic sanitization check
        if not self.validator.validate_query(text):
            logger.warning(f"Invalid query from user {user_id}: {text[:50]}...")
            return False
        
        # Check for spam indicators
        text_lower = text.lower()
        spam_count = sum(1 for indicator in self.spam_indicators if indicator in text_lower)
        
        if spam_count >= 2:  # Multiple spam indicators
            logger.warning(f"Potential spam detected from user {user_id}")
            return False
        
        # Check for excessive repeated characters
        if len(set(text)) < len(text) * 0.3 and len(text) > 10:  # Too repetitive
            logger.warning(f"Repetitive text from user {user_id}")
            return False
        
        # Check for excessive caps
        if text.isupper() and len(text) > 20:
            logger.warning(f"Excessive caps from user {user_id}")
            return False
        
        return True
    
    def log_security_event(self, event_type: str, user_id: int, details: str) -> None:
        """Log security events for monitoring."""
        if not self.validator.is_safe_for_logging(details):
            details = "[UNSAFE_CONTENT_REDACTED]"
        
        logger.warning(f"SECURITY_EVENT: {event_type} from user {user_id}: {details}")
        
        # Store in database if available
        try:
            if hasattr(self.db, 'log_security_event'):
                self.db.log_security_event(event_type, user_id, details)
        except Exception as e:
            logger.error(f"Failed to log security event to database: {e}")
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Main middleware execution."""
        user = None
        message_text = None
        
        try:
            # Extract user information
            if isinstance(event, (Message, CallbackQuery)):
                user = event.from_user
                if isinstance(event, Message) and event.text:
                    message_text = event.text
            
            if not user:
                # No user info, let it pass but log
                logger.warning("Event without user information")
                return await handler(event, data)
            
            user_id = user.id
            
            # Skip security checks for admin
            if user_id == self.config.ADMIN_ID:
                return await handler(event, data)
            
            # Validate user
            if not self.validate_user(user):
                self.log_security_event("SUSPICIOUS_USER", user_id, f"Username: {user.username}")
                activity = self.get_user_activity(user_id)
                activity.add_suspicious_activity()
                return  # Block request
            
            # Get user activity
            activity = self.get_user_activity(user_id)
            
            # Check if user is blocked
            if activity.is_blocked:
                self.log_security_event("BLOCKED_USER_ACCESS", user_id, "User is currently blocked")
                if isinstance(event, Message):
                    try:
                        await event.answer("🚫 Доступ временно ограничен. Попробуйте позже.")
                    except:
                        pass
                return
            
            # Check rate limiting
            if self.config.security.enable_rate_limiting and activity.is_rate_limited():
                self.log_security_event("RATE_LIMIT_EXCEEDED", user_id, 
                                      f"Requests: {activity.get_requests_in_window(1)}/min, {activity.get_requests_in_window(60)}/hour")
                
                if isinstance(event, Message):
                    try:
                        await event.answer("⏰ Слишком много запросов. Подождите немного.")
                    except:
                        pass
                return
            
            # Validate message content
            if message_text and self.config.security.enable_input_validation:
                if not self.validate_message_content(message_text, user_id):
                    self.log_security_event("INVALID_CONTENT", user_id, message_text[:100])
                    activity.add_suspicious_activity()
                    
                    if isinstance(event, Message):
                        try:
                            await event.answer("❌ Недопустимое содержимое сообщения.")
                        except:
                            pass
                    return
            
            # Record legitimate request
            activity.add_request()
            
            # Update user activity in database
            if hasattr(self.db, 'update_user_activity'):
                self.db.update_user_activity(user_id)
            
            # Add security context to data
            data["security_validated"] = True
            data["user_activity"] = activity
            
            # Proceed with request
            return await handler(event, data)
            
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            # On error, let the request pass but log it
            try:
                # Safely extract user_id, handling cases where user might not be defined
                user_id = user.id if user is not None else 0
                self.log_security_event("MIDDLEWARE_ERROR", user_id, str(e))
            except:
                self.log_security_event("MIDDLEWARE_ERROR", 0, str(e))
            return await handler(event, data)
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get security statistics."""
        total_users = len(self.user_activities)
        blocked_users = sum(1 for activity in self.user_activities.values() if activity.is_blocked)
        total_requests = sum(activity.total_requests for activity in self.user_activities.values())
        suspicious_activities = sum(activity.suspicious_activity_count for activity in self.user_activities.values())
        
        return {
            'total_tracked_users': total_users,
            'blocked_users': blocked_users,
            'total_requests': total_requests,
            'suspicious_activities': suspicious_activities,
            'rate_limiting_enabled': self.config.security.enable_rate_limiting,
            'input_validation_enabled': self.config.security.enable_input_validation
        }
    
    def cleanup_old_data(self, days_to_keep: int = 7) -> None:
        """Clean up old activity data to prevent memory bloat."""
        cutoff = datetime.now() - timedelta(days=days_to_keep)
        
        users_to_remove = []
        for user_id, activity in self.user_activities.items():
            if activity.last_activity < cutoff and not activity.is_blocked:
                users_to_remove.append(user_id)
        
        for user_id in users_to_remove:
            del self.user_activities[user_id]
        
        logger.info(f"Cleaned up {len(users_to_remove)} old user activity records")