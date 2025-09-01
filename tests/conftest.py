"""
Pytest configuration and fixtures for the FAQ bot test suite.
Provides common test utilities, fixtures, and mock objects.
"""

import pytest
import asyncio
import tempfile
import json
import sqlite3
from pathlib import Path
from unittest.mock import Mock, AsyncMock, MagicMock
from typing import Dict, Any, List
import sys
import os

# Add src directory to path for imports
project_root = Path(__file__).parent.parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

from aiogram import types
from src.config import Config
from src.database import Database
from src.faq_loader import FAQLoader
from src.performance_manager import PerformanceManager
from src.security_middleware import SecurityMiddleware


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_config(temp_dir):
    """Create a mock configuration for testing."""
    config = Mock(spec=Config)
    config.BOT_TOKEN = "test_token"
    config.ADMIN_ID = 12345
    config.BASE_DIR = temp_dir
    config.DB_PATH = temp_dir / "test.db"
    config.FAQ_FILE = temp_dir / "test_faq.json"
    config.EMBEDDINGS_FILE = temp_dir / "test_embeddings.pkl"
    config.INDEX_FILE = temp_dir / "test_index.faiss"
    config.security = Mock()
    config.security.access_password = "test_password"
    config.security.blocked_words = ["test_blocked"]
    config.security.enable_rate_limiting = True
    config.security.max_requests_per_minute = 10
    config.security.max_requests_per_hour = 100
    config.ml = Mock()
    config.ml.model_name = "test_model"
    config.ml.similarity_threshold = 0.7
    config.network = Mock()
    config.network.request_timeout = 30
    return config


@pytest.fixture
def sample_faq_data():
    """Create sample FAQ data for testing."""
    return [
        {
            "query": "How to get installment plan",
            "variations": ["installment", "payment plan", "split payment"],
            "response": "You can get an installment plan by...",
            "resources": [
                {
                    "title": "Installment Guide",
                    "type": "file",
                    "files": ["guide.pdf"]
                }
            ]
        },
        {
            "query": "Password reset",
            "variations": ["forgot password", "reset password"],
            "response": "To reset your password...",
            "resources": [
                {
                    "title": "Password Reset Link",
                    "type": "link",
                    "link": "https://example.com/reset"
                }
            ]
        }
    ]


@pytest.fixture
def mock_user():
    """Create a mock Telegram user for testing."""
    return types.User(
        id=123456,
        is_bot=False,
        first_name="Test",
        last_name="User",
        username="test_user"
    )


@pytest.fixture
def mock_message(mock_user):
    """Create a mock Telegram message for testing."""
    message = Mock(spec=types.Message)
    message.from_user = mock_user
    message.text = "Test message"
    message.message_id = 1
    message.date = 1234567890
    message.chat = Mock()
    message.chat.id = 123456
    message.answer = AsyncMock()
    message.answer_document = AsyncMock()
    return message


@pytest.fixture
def mock_callback_query(mock_user):
    """Create a mock Telegram callback query for testing."""
    callback = Mock(spec=types.CallbackQuery)
    callback.from_user = mock_user
    callback.data = "test_callback"
    callback.id = "123"
    callback.message = Mock()
    callback.answer = AsyncMock()
    return callback


@pytest.fixture
def test_database(temp_dir, mock_config):
    """Create a test database with sample data."""
    db_path = temp_dir / "test.db"
    db = Database(db_path)
    db.init_db()
    
    # Add some test data
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Add test authenticated user
        cursor.execute(
            "INSERT INTO authenticated_users (user_id, username, first_name, last_name) VALUES (?, ?, ?, ?)",
            (123456, "test_user", "Test", "User")
        )
        
        # Add test query stats
        cursor.execute(
            "INSERT INTO query_stats (question, user_id, success, similarity_score) VALUES (?, ?, ?, ?)",
            ("test question", 123456, 1, 0.85)
        )
        
        # Add test unanswered question
        cursor.execute(
            "INSERT INTO unanswered_questions (question, user_id) VALUES (?, ?)",
            ("unanswered question", 123456)
        )
        
        conn.commit()
    
    return db


@pytest.fixture
def mock_faq_loader(temp_dir, sample_faq_data, mock_config):
    """Create a mock FAQ loader with sample data."""
    faq_file = temp_dir / "test_faq.json"
    
    # Write sample FAQ data to file
    with open(faq_file, 'w', encoding='utf-8') as f:
        json.dump(sample_faq_data, f, ensure_ascii=False, indent=2)
    
    # Create loader with mocked model
    loader = FAQLoader(
        faq_file=faq_file,
        embeddings_file=temp_dir / "test_embeddings.pkl",
        index_file=temp_dir / "test_index.faiss"
    )
    
    # Mock the sentence transformer model
    loader.model = Mock()
    loader.model.encode = Mock(return_value=[[0.1, 0.2, 0.3, 0.4]])
    loader._model_loaded = True
    
    return loader


@pytest.fixture
def mock_performance_manager():
    """Create a mock performance manager for testing."""
    manager = Mock(spec=PerformanceManager)
    manager.track_request = Mock()
    manager.get_cached_query_result = Mock(return_value=None)
    manager.cache_query_result = Mock()
    manager.get_cached_embedding = Mock(return_value=None)
    manager.cache_embedding = Mock()
    manager.metrics = Mock()
    manager.metrics.total_requests = 0
    manager.metrics.cache_hits = 0
    manager.metrics.cache_misses = 0
    return manager


@pytest.fixture
def mock_security_middleware(test_database, mock_config):
    """Create a mock security middleware for testing."""
    middleware = SecurityMiddleware(test_database, mock_config)
    return middleware


class MockFAISSIndex:
    """Mock FAISS index for testing."""
    
    def __init__(self, dimension=4):
        self.dimension = dimension
        self.ntotal = 2
        self._vectors = []
    
    def add(self, vectors):
        """Mock add method."""
        self._vectors.extend(vectors)
    
    def search(self, query_vector, k):
        """Mock search method returning distances and indices."""
        # Return mock similarities and indices
        distances = [[0.85, 0.70]]  # Mock similarity scores
        indices = [[0, 1]]  # Mock indices
        return distances, indices


@pytest.fixture
def mock_faiss_index():
    """Create a mock FAISS index for testing."""
    return MockFAISSIndex()


@pytest.fixture
def test_data_factory():
    """Factory for creating test data."""
    class TestDataFactory:
        @staticmethod
        def create_user(user_id=123456, username="test_user", first_name="Test", last_name="User"):
            return types.User(
                id=user_id,
                is_bot=False,
                first_name=first_name,
                last_name=last_name,
                username=username
            )
        
        @staticmethod
        def create_message(text="Test message", user=None):
            if user is None:
                user = TestDataFactory.create_user()
            
            message = Mock(spec=types.Message)
            message.from_user = user
            message.text = text
            message.message_id = 1
            message.answer = AsyncMock()
            message.answer_document = AsyncMock()
            return message
        
        @staticmethod
        def create_faq_entry(query="Test query", response="Test response"):
            return {
                "query": query,
                "variations": [f"{query} variation"],
                "response": response,
                "resources": []
            }
    
    return TestDataFactory()


# Test environment setup
@pytest.fixture(autouse=True)
def setup_test_environment(temp_dir, monkeypatch):
    """Setup test environment for all tests."""
    # Set test environment variables
    monkeypatch.setenv("BOT_TOKEN", "test_token")
    monkeypatch.setenv("ADMIN_ID", "12345")
    monkeypatch.setenv("ACCESS_PASSWORD", "test_password")
    
    # Ensure test directories exist
    (temp_dir / "data").mkdir(exist_ok=True)
    (temp_dir / "cache").mkdir(exist_ok=True)
    (temp_dir / "files").mkdir(exist_ok=True)
    (temp_dir / "backups").mkdir(exist_ok=True)


# Async test helpers
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (may need special handling)"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


class AsyncTestHelper:
    """Helper class for async testing utilities."""
    
    @staticmethod
    async def wait_for_condition(condition_func, timeout=5.0, interval=0.1):
        """Wait for a condition to become true."""
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if condition_func():
                return True
            await asyncio.sleep(interval)
        
        return False
    
    @staticmethod
    def create_async_mock():
        """Create an async mock function."""
        return AsyncMock()


@pytest.fixture
def async_test_helper():
    """Provide async testing utilities."""
    return AsyncTestHelper()