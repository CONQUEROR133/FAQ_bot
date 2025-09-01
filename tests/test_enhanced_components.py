"""
Unit tests for the enhanced configuration and database modules.
Tests configuration validation, database operations, and error handling.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch
import sqlite3

from src.config import Config, SecurityConfig, NetworkConfig, MLConfig, SecurityValidator
from src.database import Database, DatabaseError, QueryStats, UserInfo
from aiogram import types


class TestSecurityValidator:
    """Test suite for SecurityValidator utilities."""
    
    def test_sanitize_text_basic(self):
        """Test basic text sanitization."""
        validator = SecurityValidator()
        
        # Test normal text
        result = validator.sanitize_text("Hello, World!")
        assert result == "Hello, World!"
        
        # Test text with HTML
        result = validator.sanitize_text("<script>alert('xss')</script>")
        assert "&lt;script&gt;" in result
        assert "&lt;/script&gt;" in result
        
        # Test empty text
        result = validator.sanitize_text("")
        assert result == ""
        
        # Test None input - type ignore since we're testing defensive programming
        result = validator.sanitize_text(None)  # type: ignore
        assert result == ""
    
    def test_sanitize_text_length_limit(self):
        """Test text sanitization with length limits."""
        validator = SecurityValidator()
        
        long_text = "a" * 1000
        result = validator.sanitize_text(long_text, max_length=100)
        assert len(result) <= 100
    
    def test_validate_query_success(self):
        """Test successful query validation."""
        validator = SecurityValidator()
        
        # Valid queries
        assert validator.validate_query("How to reset password?") is True
        assert validator.validate_query("Как получить рассрочку") is True
        assert validator.validate_query("What is the price?") is True
    
    def test_validate_query_failure(self):
        """Test query validation failures."""
        validator = SecurityValidator()
        
        # Invalid queries
        assert validator.validate_query("") is False
        assert validator.validate_query("a") is False  # Too short
        assert validator.validate_query("a" * 1001) is False  # Too long
        assert validator.validate_query("SELECT * FROM users") is False  # SQL injection
        assert validator.validate_query("<script>alert('xss')</script>") is False  # XSS
        assert validator.validate_query("javascript:alert('xss')") is False  # JavaScript
    
    def test_validate_file_path(self):
        """Test file path validation."""
        validator = SecurityValidator()
        
        # Valid paths
        assert validator.validate_file_path("document.pdf") is True
        assert validator.validate_file_path("folder/file.txt") is True
        
        # Invalid paths
        assert validator.validate_file_path("../../../etc/passwd") is False  # Path traversal
        assert validator.validate_file_path("/etc/passwd") is False  # Absolute path
        assert validator.validate_file_path("malware.exe") is False  # Dangerous extension
        assert validator.validate_file_path("script.js") is False  # JavaScript file
    
    def test_is_safe_for_logging(self):
        """Test log safety validation."""
        validator = SecurityValidator()
        
        # Safe text
        assert validator.is_safe_for_logging("Normal log message") is True
        assert validator.is_safe_for_logging("User 123 logged in") is True
        
        # Unsafe text
        assert validator.is_safe_for_logging("Line 1\\nLine 2") is False  # Line breaks
        assert validator.is_safe_for_logging("Text with \\r carriage return") is False


class TestSecurityConfig:
    """Test suite for SecurityConfig."""
    
    def test_security_config_creation(self):
        """Test SecurityConfig creation and validation."""
        config = SecurityConfig(
            access_password="strong_password_123",
            blocked_words=["spam", "bad"]
        )
        
        assert config.access_password == "strong_password_123"
        assert "spam" in config.blocked_words
        assert config.enable_rate_limiting is True
        assert config.max_requests_per_minute == 20
    
    def test_security_config_validation_errors(self):
        """Test SecurityConfig validation errors."""
        # Empty password should raise error
        with pytest.raises(ValueError, match="Access password cannot be empty"):
            SecurityConfig(
                access_password="",
                blocked_words=[]
            )
        
        # Invalid rate limiting
        with pytest.raises(ValueError):
            SecurityConfig(
                access_password="test",
                blocked_words=[],
                max_requests_per_minute=0
            )
    
    def test_password_strength_validation(self):
        """Test password strength validation."""
        # Weak password
        weak_config = SecurityConfig(
            access_password="123",
            blocked_words=[]
        )
        assert weak_config.validate_password_strength() is False
        
        # Strong password
        strong_config = SecurityConfig(
            access_password="Strong_Password_123!",
            blocked_words=[]
        )
        assert strong_config.validate_password_strength() is True


class TestNetworkConfig:
    """Test suite for NetworkConfig."""
    
    def test_network_config_creation(self):
        """Test NetworkConfig creation."""
        config = NetworkConfig(
            request_timeout=60,
            max_retries=5
        )
        
        assert config.request_timeout == 60
        assert config.max_retries == 5
    
    def test_network_config_validation(self):
        """Test NetworkConfig validation."""
        # Invalid timeout
        with pytest.raises(ValueError, match="Request timeout must be positive"):
            NetworkConfig(request_timeout=0)
        
        # Invalid retries
        with pytest.raises(ValueError, match="Max retries cannot be negative"):
            NetworkConfig(max_retries=-1)


class TestMLConfig:
    """Test suite for MLConfig."""
    
    def test_ml_config_creation(self):
        """Test MLConfig creation."""
        config = MLConfig(
            model_name="test-model",
            similarity_threshold=0.8
        )
        
        assert config.model_name == "test-model"
        assert config.similarity_threshold == 0.8
    
    def test_ml_config_validation(self):
        """Test MLConfig validation."""
        # Invalid threshold
        with pytest.raises(ValueError, match="Similarity threshold must be between 0.0 and 1.0"):
            MLConfig(similarity_threshold=1.5)
        
        with pytest.raises(ValueError, match="Similarity threshold must be between 0.0 and 1.0"):
            MLConfig(similarity_threshold=-0.5)


class TestDatabase:
    """Test suite for enhanced Database class."""
    
    def test_database_creation(self, temp_dir):
        """Test database creation and initialization."""
        db_path = temp_dir / "test.db"
        db = Database(db_path)
        db.init_db()
        
        # Check that database file was created
        assert db_path.exists()
        
        # Check that tables were created
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Check authenticated_users table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='authenticated_users'")
            assert cursor.fetchone() is not None
            
            # Check indexes were created
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_query_stats_timestamp'")
            assert cursor.fetchone() is not None
    
    def test_user_authentication(self, test_database, mock_user):
        """Test user authentication operations."""
        # Initially user should not be authenticated
        assert test_database.is_user_authenticated(mock_user.id) is True  # Added in fixture
        
        # Test with new user
        new_user = types.User(
            id=999999,
            is_bot=False,
            first_name="New",
            last_name="User",
            username="new_user"
        )
        
        assert test_database.is_user_authenticated(new_user.id) is False
        
        # Authenticate user
        result = test_database.authenticate_user(new_user)
        assert result is True
        
        # Check user is now authenticated
        assert test_database.is_user_authenticated(new_user.id) is True
    
    def test_invalid_user_authentication(self, test_database):
        """Test authentication with invalid users."""
        # Test with None user
        assert test_database.authenticate_user(None) is False
        
        # Test with invalid user ID
        assert test_database.is_user_authenticated(0) is False
        assert test_database.is_user_authenticated(-1) is False
    
    def test_query_logging(self, test_database):
        """Test query logging functionality."""
        # Log successful query
        result = test_database.log_query("test question", True, user_id=123456, similarity_score=0.85)
        assert result is True
        
        # Log failed query
        result = test_database.log_query("failed question", False, user_id=123456)
        assert result is True
        
        # Test with empty query
        result = test_database.log_query("", True)
        assert result is False
    
    def test_unanswered_question_logging(self, test_database):
        """Test unanswered question logging."""
        result = test_database.log_unanswered_question("What is this?", user_id=123456)
        assert result is True
        
        # Test with empty question
        result = test_database.log_unanswered_question("")
        assert result is False
    
    def test_bad_word_logging(self, test_database, mock_user):
        """Test bad word logging."""
        result = test_database.log_bad_word(mock_user, "This contains bad words", severity="high")
        assert result is True
        
        # Test with None user
        result = test_database.log_bad_word(None, "test message")
        assert result is False
    
    def test_get_stats(self, test_database):
        """Test statistics retrieval."""
        stats = test_database.get_stats()
        
        assert isinstance(stats, QueryStats)
        assert stats.total_queries >= 0
        assert 0 <= stats.success_rate <= 100
        assert stats.authenticated_users_count >= 0
    
    def test_user_activity_management(self, test_database):
        """Test user activity tracking."""
        user_id = 123456
        
        # Update activity
        result = test_database.update_user_activity(user_id)
        assert result is True
        
        # Test with invalid user ID
        result = test_database.update_user_activity(0)
        assert result is False
    
    def test_user_deactivation(self, test_database):
        """Test user deactivation."""
        user_id = 123456
        
        # Deactivate user
        result = test_database.deactivate_user(user_id)
        assert result is True
        
        # User should no longer be authenticated
        assert test_database.is_user_authenticated(user_id) is False
    
    def test_get_user_info(self, test_database):
        """Test user information retrieval."""
        user_id = 123456
        
        user_info = test_database.get_user_info(user_id)
        assert user_info is not None
        assert isinstance(user_info, UserInfo)
        assert user_info.user_id == user_id
        
        # Test with non-existent user
        user_info = test_database.get_user_info(999999)
        assert user_info is None
    
    def test_export_stats_to_file(self, test_database, temp_dir):
        """Test statistics export."""
        # Change to temp directory to avoid creating files in project root
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            filename = test_database.export_stats_to_file(include_sensitive=False)
            
            assert filename is not None
            assert Path(filename).exists()
            
            # Check file content
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "ОБЩАЯ СТАТИСТИКА" in content
                assert "ТОП-10 ПОПУЛЯРНЫХ ЗАПРОСОВ" in content
        finally:
            os.chdir(original_cwd)
    
    def test_cleanup_old_data(self, test_database):
        """Test old data cleanup."""
        result = test_database.cleanup_old_data(days_to_keep=1)
        assert result is True
    
    def test_database_error_handling(self, temp_dir):
        """Test database error handling."""
        # Test with invalid database path
        invalid_path = temp_dir / "nonexistent" / "test.db"
        
        # This should work as the Database class creates directories
        db = Database(invalid_path)
        db.init_db()
        assert invalid_path.exists()
    
    def test_connection_context_manager(self, test_database):
        """Test database connection context manager."""
        # Test successful connection
        with test_database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1
    
    @pytest.mark.integration
    def test_database_performance(self, test_database):
        """Test database performance with multiple operations."""
        import time
        
        start_time = time.time()
        
        # Perform multiple operations
        for i in range(100):
            test_database.log_query(f"test query {i}", True, user_id=123456)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert execution_time < 5.0  # 5 seconds for 100 operations