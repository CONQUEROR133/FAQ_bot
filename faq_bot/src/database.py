import sqlite3
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple, Union
from contextlib import contextmanager
from pathlib import Path
from dataclasses import dataclass

# Handle aiogram import with fallback
try:
    from aiogram import types
except ImportError:
    # Create a minimal types module for development environments
    class types:
        pass

from config import config

logger = logging.getLogger(__name__)


@dataclass
class QueryStats:
    """Data class for query statistics."""
    total_queries: int
    success_rate: float
    unanswered_questions: int
    bad_words_count: int
    authenticated_users_count: int
    popular_queries: List[Tuple[str, int]]


@dataclass
class UserInfo:
    """Data class for user information."""
    user_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    authenticated_at: datetime


class DatabaseError(Exception):
    """Custom exception for database-related errors."""
    pass


class Database:
    """Enhanced database manager with improved error handling and type safety."""
    
    def __init__(self, db_path: Union[str, Path, None] = None):
        """Initialize database with proper path handling.
        
        Args:
            db_path: Path to database file. If None, uses config.DB_PATH
        """
        self.db_path = Path(db_path) if db_path else Path(config.DB_PATH)
        self._ensure_db_directory()
        
        # Connection settings
        self.timeout = 30.0
        self.check_same_thread = False
        
        logger.info(f"Database initialized at: {self.db_path}")
    
    def _ensure_db_directory(self) -> None:
        """Ensure database directory exists."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections with proper error handling."""
        conn = None
        try:
            conn = sqlite3.connect(
                str(self.db_path),
                timeout=self.timeout,
                check_same_thread=self.check_same_thread
            )
            conn.row_factory = sqlite3.Row  # Enable column access by name
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise DatabaseError(f"Database operation failed: {e}") from e
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Unexpected database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def init_db(self) -> None:
        """Initialize database and create tables with improved schema."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Users table with better constraints
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS authenticated_users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    authenticated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
                ''')
                
                # Unanswered questions with better indexing
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS unanswered_questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    user_id INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    resolved BOOLEAN DEFAULT 0
                )
                ''')
                
                # Query stats with better metrics
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS query_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    user_id INTEGER,
                    success INTEGER DEFAULT 0,
                    similarity_score REAL,
                    response_time_ms INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                
                # Bad words log with severity levels
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS bad_words_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    message TEXT NOT NULL,
                    severity TEXT DEFAULT 'medium',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_query_stats_timestamp ON query_stats(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_query_stats_success ON query_stats(success)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_unanswered_timestamp ON unanswered_questions(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_bad_words_timestamp ON bad_words_log(timestamp)')
                
                conn.commit()
                logger.info("Database schema initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise DatabaseError(f"Database initialization failed: {e}") from e

    def log_unanswered_question(self, question: str, user_id: Optional[int] = None) -> bool:
        """Log an unanswered question with validation.
        
        Args:
            question: The unanswered question text
            user_id: Optional user ID who asked the question
            
        Returns:
            bool: True if logged successfully, False otherwise
        """
        if not question or not question.strip():
            logger.warning("Attempted to log empty question")
            return False
            
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO unanswered_questions (question, user_id) VALUES (?, ?)",
                    (question.strip(), user_id)
                )
                conn.commit()
                logger.info(f"Logged unanswered question: {question[:50]}...")
                return True
                
        except Exception as e:
            logger.error(f"Failed to log unanswered question: {e}")
            return False
    
    def log_query(self, question: str, success: bool, user_id: Optional[int] = None, 
                  similarity_score: Optional[float] = None, response_time_ms: Optional[int] = None) -> bool:
        """Log a query with enhanced metrics.
        
        Args:
            question: The question text
            success: Whether the query was successful
            user_id: Optional user ID
            similarity_score: Optional similarity score
            response_time_ms: Optional response time in milliseconds
            
        Returns:
            bool: True if logged successfully, False otherwise
        """
        if not question or not question.strip():
            logger.warning("Attempted to log empty query")
            return False
            
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO query_stats (question, user_id, success, similarity_score, response_time_ms) VALUES (?, ?, ?, ?, ?)",
                    (question.strip(), user_id, 1 if success else 0, similarity_score, response_time_ms)
                )
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to log query: {e}")
            return False
    
    def log_bad_word(self, user: types.User, message: str, severity: str = "medium") -> bool:
        """Log bad word usage with severity classification.
        
        Args:
            user: Telegram user object
            message: The message containing bad words
            severity: Severity level (low, medium, high)
            
        Returns:
            bool: True if logged successfully, False otherwise
        """
        if not user:
            logger.warning("Attempted to log bad word without user info")
            return False
            
        if severity not in ["low", "medium", "high"]:
            severity = "medium"
            
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO bad_words_log (user_id, username, first_name, last_name, message, severity) VALUES (?, ?, ?, ?, ?, ?)",
                    (user.id, user.username, user.first_name, user.last_name, message, severity)
                )
                conn.commit()
                logger.info(f"Logged bad word usage by user {user.id} (severity: {severity})")
                return True
                
        except Exception as e:
            logger.error(f"Failed to log bad word: {e}")
            return False

    def get_stats(self) -> QueryStats:
        """Get comprehensive statistics with enhanced error handling.
        
        Returns:
            QueryStats: Statistics object with all metrics
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get basic counts
                cursor.execute("SELECT COUNT(*) FROM query_stats")
                total_queries = cursor.fetchone()[0] or 0
                
                cursor.execute("SELECT COUNT(*) FROM query_stats WHERE success = 1")
                success_queries = cursor.fetchone()[0] or 0
                
                cursor.execute("SELECT COUNT(*) FROM unanswered_questions WHERE resolved = 0")
                unanswered_questions = cursor.fetchone()[0] or 0
                
                cursor.execute("SELECT COUNT(*) FROM bad_words_log")
                bad_words_count = cursor.fetchone()[0] or 0
                
                cursor.execute("SELECT COUNT(*) FROM authenticated_users WHERE is_active = 1")
                authenticated_users_count = cursor.fetchone()[0] or 0
                
                # Get popular queries
                cursor.execute(
                    "SELECT question, COUNT(*) as count FROM query_stats "
                    "WHERE success = 1 "
                    "GROUP BY LOWER(TRIM(question)) "
                    "ORDER BY count DESC LIMIT 10"
                )
                popular_queries = cursor.fetchall() or []
                
                # Calculate success rate
                success_rate = (success_queries / total_queries * 100) if total_queries > 0 else 0
                
                return QueryStats(
                    total_queries=total_queries,
                    success_rate=success_rate,
                    unanswered_questions=unanswered_questions,
                    bad_words_count=bad_words_count,
                    authenticated_users_count=authenticated_users_count,
                    popular_queries=[(row[0], row[1]) for row in popular_queries]
                )
                
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            # Return empty stats on error
            return QueryStats(
                total_queries=0,
                success_rate=0.0,
                unanswered_questions=0,
                bad_words_count=0,
                authenticated_users_count=0,
                popular_queries=[]
            )
    
    def export_stats_to_file(self, include_sensitive: bool = False) -> Optional[str]:
        """Export comprehensive statistics to file with privacy options.
        
        Args:
            include_sensitive: Whether to include sensitive user data
            
        Returns:
            Optional[str]: Filename if successful, None otherwise
        """
        try:
            filename = f"analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                with open(filename, 'w', encoding='utf-8') as f:
                    stats = self.get_stats()
                    
                    # Write summary
                    f.write("=== ОБЩАЯ СТАТИСТИКА ===\n")
                    f.write(f"Всего запросов: {stats.total_queries}\n")
                    f.write(f"Успешных ответов: {stats.success_rate:.2f}%\n")
                    f.write(f"Неотвеченных вопросов: {stats.unanswered_questions}\n")
                    f.write(f"Зафиксировано матов: {stats.bad_words_count}\n")
                    f.write(f"Аутентифицированных пользователей: {stats.authenticated_users_count}\n\n")
                    
                    # Write popular queries
                    f.write("=== ТОП-10 ПОПУЛЯРНЫХ ЗАПРОСОВ ===\n")
                    for i, (query, count) in enumerate(stats.popular_queries, 1):
                        f.write(f"{i}. {query} - {count} запросов\n")
                    f.write("\n")
                    
                    # Write recent unanswered questions
                    f.write("=== ПОСЛЕДНИЕ НЕОТВЕЧЕННЫЕ ВОПРОСЫ ===\n")
                    cursor.execute(
                        "SELECT question, timestamp FROM unanswered_questions "
                        "WHERE resolved = 0 ORDER BY timestamp DESC LIMIT 20"
                    )
                    for row in cursor.fetchall() or []:
                        f.write(f"- {row[0]} ({row[1]})\n")
                    f.write("\n")
                    
                    if include_sensitive:
                        # Write bad words log (if requested)
                        f.write("=== ПОСЛЕДНИЕ ИСПОЛЬЗОВАНИЯ МАТОВ ===\n")
                        cursor.execute(
                            "SELECT user_id, username, first_name, last_name, message, severity, timestamp "
                            "FROM bad_words_log ORDER BY timestamp DESC LIMIT 10"
                        )
                        for row in cursor.fetchall() or []:
                            user_id, username, first_name, last_name, message, severity, timestamp = row
                            name = f"{first_name} {last_name}" if last_name else first_name
                            user_info = f"{name} (@{username})" if username else f"{name} (ID: {user_id})"
                            f.write(f"- {user_info}: {message} (серьезность: {severity}, {timestamp})\n")
                        f.write("\n")
                        
                        # Write authenticated users
                        f.write("=== АУТЕНТИФИЦИРОВАННЫЕ ПОЛЬЗОВАТЕЛИ ===\n")
                        cursor.execute(
                            "SELECT user_id, username, first_name, last_name, authenticated_at "
                            "FROM authenticated_users WHERE is_active = 1 ORDER BY authenticated_at DESC"
                        )
                        for row in cursor.fetchall() or []:
                            user_id, username, first_name, last_name, auth_time = row
                            name = f"{first_name} {last_name}" if last_name else first_name
                            user_info = f"{name} (@{username})" if username else f"{name} (ID: {user_id})"
                            f.write(f"- {user_info}: аутентифицирован {auth_time}\n")
            
            logger.info(f"Statistics exported to: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Failed to export statistics: {e}")
            return None
    
    def is_user_authenticated(self, user_id: int) -> bool:
        """Check if user is authenticated with improved validation.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            bool: True if user is authenticated and active
        """
        if not user_id or user_id <= 0:
            return False
            
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT user_id FROM authenticated_users WHERE user_id = ? AND is_active = 1",
                    (user_id,)
                )
                result = cursor.fetchone()
                return result is not None
                
        except Exception as e:
            logger.error(f"Failed to check authentication for user {user_id}: {e}")
            return False
    
    def authenticate_user(self, user: types.User) -> bool:
        """Authenticate a user with improved error handling.
        
        Args:
            user: Telegram user object
            
        Returns:
            bool: True if authentication successful
        """
        if not user or not user.id:
            logger.warning("Attempted to authenticate invalid user")
            return False
            
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO authenticated_users "
                    "(user_id, username, first_name, last_name, authenticated_at, last_activity, is_active) "
                    "VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1)",
                    (user.id, user.username, user.first_name, user.last_name)
                )
                conn.commit()
                logger.info(f"User {user.id} ({user.first_name}) authenticated successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to authenticate user {user.id}: {e}")
            return False
    
    def update_user_activity(self, user_id: int) -> bool:
        """Update user's last activity timestamp.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            bool: True if update successful
        """
        if not user_id or user_id <= 0:
            return False
            
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE authenticated_users SET last_activity = CURRENT_TIMESTAMP WHERE user_id = ?",
                    (user_id,)
                )
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Failed to update activity for user {user_id}: {e}")
            return False
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user (soft delete).
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            bool: True if deactivation successful
        """
        if not user_id or user_id <= 0:
            return False
            
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE authenticated_users SET is_active = 0 WHERE user_id = ?",
                    (user_id,)
                )
                conn.commit()
                logger.info(f"User {user_id} deactivated")
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Failed to deactivate user {user_id}: {e}")
            return False
    
    def get_authenticated_users_count(self) -> int:
        """Get count of active authenticated users.
        
        Returns:
            int: Number of active authenticated users
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM authenticated_users WHERE is_active = 1")
                return cursor.fetchone()[0] or 0
                
        except Exception as e:
            logger.error(f"Failed to get authenticated users count: {e}")
            return 0
    
    def get_user_info(self, user_id: int) -> Optional[UserInfo]:
        """Get detailed user information.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Optional[UserInfo]: User information if found
        """
        if not user_id or user_id <= 0:
            return None
            
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT user_id, username, first_name, last_name, authenticated_at "
                    "FROM authenticated_users WHERE user_id = ? AND is_active = 1",
                    (user_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    return UserInfo(
                        user_id=row[0],
                        username=row[1],
                        first_name=row[2],
                        last_name=row[3],
                        authenticated_at=datetime.fromisoformat(row[4]) if row[4] else datetime.now()
                    )
                return None
                
        except Exception as e:
            logger.error(f"Failed to get user info for {user_id}: {e}")
            return None
    
    def cleanup_old_data(self, days_to_keep: int = 90) -> bool:
        """Clean up old data to maintain performance.
        
        Args:
            days_to_keep: Number of days of data to keep
            
        Returns:
            bool: True if cleanup successful
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Clean old query stats
                cursor.execute(
                    "DELETE FROM query_stats WHERE timestamp < datetime('now', '-{} days')".format(days_to_keep)
                )
                query_deleted = cursor.rowcount
                
                # Clean old bad words log
                cursor.execute(
                    "DELETE FROM bad_words_log WHERE timestamp < datetime('now', '-{} days')".format(days_to_keep)
                )
                bad_words_deleted = cursor.rowcount
                
                # Clean resolved unanswered questions
                cursor.execute(
                    "DELETE FROM unanswered_questions WHERE resolved = 1 AND timestamp < datetime('now', '-{} days')".format(days_to_keep)
                )
                unanswered_deleted = cursor.rowcount
                
                conn.commit()
                
                logger.info(
                    f"Cleanup completed: {query_deleted} query stats, "
                    f"{bad_words_deleted} bad words logs, {unanswered_deleted} resolved questions deleted"
                )
                return True
                
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return False