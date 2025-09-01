import os
import logging
import re
import html
from typing import List, Optional, Union, Pattern
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Load .env from parent directory
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

logger = logging.getLogger(__name__)


class SecurityValidator:
    """Security validation utilities for input sanitization."""
    
    # Regex patterns for validation
    SAFE_TEXT_PATTERN: Pattern[str] = re.compile(r'^[\w\s\-\.\,\!\?\(\)\[\]\{\}\:;]+$', re.UNICODE)
    EMAIL_PATTERN: Pattern[str] = re.compile(r'^[\w\.-]+@[\w\.-]+\.[\w]+$')
    USERNAME_PATTERN: Pattern[str] = re.compile(r'^[\w\-\.]{3,32}$')
    
    # Maximum lengths for various inputs
    MAX_QUERY_LENGTH = 1000
    MAX_MESSAGE_LENGTH = 4096  # Telegram limit
    MAX_USERNAME_LENGTH = 32
    MAX_FILENAME_LENGTH = 255
    
    @staticmethod
    def sanitize_text(text: str, max_length: Optional[int] = None) -> str:
        """Sanitize text input by removing potentially dangerous characters.
        
        Args:
            text: Input text to sanitize
            max_length: Maximum allowed length
            
        Returns:
            str: Sanitized text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # HTML escape to prevent XSS-style attacks
        sanitized = html.escape(text.strip())
        
        # Remove null bytes and control characters
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)
        
        # Limit length if specified
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length].rstrip()
            logger.warning(f"Text truncated to {max_length} characters")
        
        return sanitized
    
    @staticmethod
    def validate_query(query: str) -> bool:
        """Validate search query for safety.
        
        Args:
            query: Query to validate
            
        Returns:
            bool: True if query is valid
        """
        if not query or not isinstance(query, str):
            return False
        
        query = query.strip()
        
        # Check length
        if len(query) > SecurityValidator.MAX_QUERY_LENGTH:
            logger.warning(f"Query too long: {len(query)} characters")
            return False
        
        # Check for minimum length
        if len(query) < 2:
            return False
        
        # Check for suspicious patterns (SQL injection style)
        suspicious_patterns = [
            r'(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\s',
            r'[\'\";]',  # SQL injection characters
            r'<script[^>]*>',  # XSS
            r'javascript:',
            r'data:',
            r'vbscript:'
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                logger.warning(f"Suspicious pattern detected in query: {pattern}")
                return False
        
        return True
    
    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """Validate file path for security.
        
        Args:
            file_path: Path to validate
            
        Returns:
            bool: True if path is safe
        """
        if not file_path or not isinstance(file_path, str):
            return False
        
        # Check for path traversal attempts
        if '..' in file_path or file_path.startswith('/'):
            logger.warning(f"Potentially dangerous file path: {file_path}")
            return False
        
        # Check for suspicious file extensions
        dangerous_extensions = ['.exe', '.bat', '.cmd', '.scr', '.vbs', '.js', '.jar']
        if any(file_path.lower().endswith(ext) for ext in dangerous_extensions):
            logger.warning(f"Dangerous file extension: {file_path}")
            return False
        
        return True
    
    @staticmethod
    def is_safe_for_logging(text: str) -> bool:
        """Check if text is safe to include in logs.
        
        Args:
            text: Text to check
            
        Returns:
            bool: True if safe for logging
        """
        if not text:
            return True
        
        # Check for potential log injection
        log_injection_patterns = [
            r'\r|\n',  # Line breaks for log injection
            r'\x1b\[[0-9;]*m',  # ANSI escape codes
        ]
        
        for pattern in log_injection_patterns:
            if re.search(pattern, text):
                return False
        
        return True


@dataclass
class NetworkConfig:
    """Network and connection configuration."""
    request_timeout: int = 30
    connect_timeout: int = 30
    read_timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 1
    
    def __post_init__(self):
        """Validate network configuration values."""
        if self.request_timeout <= 0:
            raise ValueError("Request timeout must be positive")
        if self.max_retries < 0:
            raise ValueError("Max retries cannot be negative")


@dataclass
class SecurityConfig:
    """Security and authentication configuration."""
    access_password: str
    blocked_words: List[str]
    enable_rate_limiting: bool = True
    max_requests_per_minute: int = 20
    max_requests_per_hour: int = 100
    enable_input_validation: bool = True
    log_suspicious_activity: bool = True
    
    def __post_init__(self):
        """Validate security configuration."""
        if not self.access_password:
            raise ValueError("Access password cannot be empty")
        if len(self.access_password) < 4:
            logger.warning("Access password is very short, consider using a stronger password")
        
        # Validate rate limiting settings
        if self.max_requests_per_minute <= 0:
            raise ValueError("Max requests per minute must be positive")
        if self.max_requests_per_hour <= 0:
            raise ValueError("Max requests per hour must be positive")
        
        # Ensure per-hour limit is reasonable compared to per-minute
        if self.max_requests_per_hour < self.max_requests_per_minute:
            logger.warning("Hourly rate limit is lower than minute limit, this may cause issues")
    
    def validate_password_strength(self) -> bool:
        """Validate password strength.
        
        Returns:
            bool: True if password meets strength requirements
        """
        password = self.access_password
        
        # Basic strength checks
        if len(password) < 8:
            logger.warning("Password should be at least 8 characters long")
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
        
        strength_score = sum([has_upper, has_lower, has_digit, has_special])
        
        if strength_score < 3:
            logger.warning("Password should contain uppercase, lowercase, numbers, and special characters")
            return False
        
        return True


@dataclass
class MLConfig:
    """Machine Learning model configuration."""
    model_name: str = "ai-forever/ru-en-RoSBERTa"
    similarity_threshold: float = 0.73
    
    def __post_init__(self):
        """Validate ML configuration values."""
        if not (0.0 <= self.similarity_threshold <= 1.0):
            raise ValueError("Similarity threshold must be between 0.0 and 1.0")


class Config:
    """Main application configuration with validation and type safety."""
    
    def __init__(self):
        """Initialize configuration with validation."""
        # Core settings
        self.BOT_TOKEN = self._get_required_env("BOT_TOKEN")
        self.ADMIN_ID = self._get_int_env("ADMIN_ID", 0)
        
        # Directory setup
        self.BASE_DIR = Path(__file__).parent.parent
        self._ensure_directories()
        
        # File paths
        self.DB_PATH = self.BASE_DIR / "data" / "analytics.db"
        self.FAQ_FILE = self.BASE_DIR / "data" / "faq.json"
        self.EMBEDDINGS_FILE = self.BASE_DIR / "cache" / "faq_embeddings.pkl"
        self.INDEX_FILE = self.BASE_DIR / "cache" / "faq_index.faiss"
        self.LOG_FILE = self.BASE_DIR / "cache" / "bot.log"
        
        # Configuration sections
        self.network = NetworkConfig(
            request_timeout=self._get_int_env("REQUEST_TIMEOUT", 30),
            connect_timeout=self._get_int_env("CONNECT_TIMEOUT", 30),
            read_timeout=self._get_int_env("READ_TIMEOUT", 30),
            max_retries=self._get_int_env("MAX_RETRIES", 3),
            retry_delay=self._get_int_env("RETRY_DELAY", 1)
        )
        
        self.security = SecurityConfig(
            access_password=os.getenv("ACCESS_PASSWORD", "1337"),
            blocked_words=self._load_blocked_words()
        )
        
        self.ml = MLConfig(
            model_name=os.getenv("MODEL_NAME", "ai-forever/ru-en-RoSBERTa"),
            similarity_threshold=self._get_float_env("SIMILARITY_THRESHOLD", 0.73)
        )
        
        # Backward compatibility properties
        self._setup_backward_compatibility()
        
        logger.info("Configuration loaded successfully")
    
    def _get_required_env(self, key: str) -> str:
        """Get required environment variable with validation."""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable '{key}' is not set")
        return value
    
    def _get_int_env(self, key: str, default: int) -> int:
        """Get integer environment variable with default."""
        try:
            value = os.getenv(key)
            return int(value) if value is not None else default
        except ValueError:
            logger.warning(f"Invalid integer value for {key}, using default: {default}")
            return default
    
    def _get_float_env(self, key: str, default: float) -> float:
        """Get float environment variable with default."""
        try:
            value = os.getenv(key)
            return float(value) if value is not None else default
        except ValueError:
            logger.warning(f"Invalid float value for {key}, using default: {default}")
            return default
    
    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        directories = [
            self.BASE_DIR / "data",
            self.BASE_DIR / "cache",
            self.BASE_DIR / "files",
            self.BASE_DIR / "backups"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_blocked_words(self) -> List[str]:
        """Load blocked words from environment or use defaults."""
        env_blocked = os.getenv("BLOCKED_WORDS")
        if env_blocked:
            return [word.strip() for word in env_blocked.split(",") if word.strip()]
        
        # Default blocked words
        return [
            "хуй", "пизда", "ебан", "гандон", "пидор", "бля",
            "сука", "мудак", "долбоеб", "уебан", "залупа"
        ]
    
    def _setup_backward_compatibility(self) -> None:
        """Setup backward compatibility properties."""
        # Network settings (backward compatibility)
        self.REQUEST_TIMEOUT = self.network.request_timeout
        self.CONNECT_TIMEOUT = self.network.connect_timeout
        self.READ_TIMEOUT = self.network.read_timeout
        self.MAX_RETRIES = self.network.max_retries
        self.RETRY_DELAY = self.network.retry_delay
        
        # Security settings (backward compatibility)
        self.ACCESS_PASSWORD = self.security.access_password
        self.BLOCKED_WORDS = self.security.blocked_words
        
        # ML settings (backward compatibility)
        self.MODEL_NAME = self.ml.model_name
        self.SIMILARITY_THRESHOLD = self.ml.similarity_threshold
    
    def validate(self) -> bool:
        """Validate entire configuration."""
        try:
            if not self.BOT_TOKEN:
                raise ValueError("BOT_TOKEN is required")
            
            if self.ADMIN_ID <= 0:
                logger.warning("ADMIN_ID should be set to a valid Telegram user ID")
            
            # Validate paths exist
            required_files = [self.FAQ_FILE]
            for file_path in required_files:
                if not file_path.exists():
                    logger.warning(f"Required file not found: {file_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
    
    def get_summary(self) -> str:
        """Get configuration summary for logging."""
        return (
            f"Bot Configuration Summary:\n"
            f"  - Admin ID: {self.ADMIN_ID}\n"
            f"  - Base Directory: {self.BASE_DIR}\n"
            f"  - ML Model: {self.ml.model_name}\n"
            f"  - Similarity Threshold: {self.ml.similarity_threshold}\n"
            f"  - Network Timeout: {self.network.request_timeout}s\n"
            f"  - Max Retries: {self.network.max_retries}"
        )

# Create global configuration instance
config = Config()

# Validate configuration on import
if not config.validate():
    logger.error("Configuration validation failed, some features may not work properly")