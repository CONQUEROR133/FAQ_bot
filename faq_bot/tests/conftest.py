#!/usr/bin/env python3
"""
Test configuration and fixtures for FAQ bot tests
"""

import sys
import os
import pytest

# Add the src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Test configuration
TEST_CONFIG = {
    'test_user_id': 123456789,
    'test_query': 'тестовый вопрос',
    'test_response': 'тестовый ответ'
}

# Pytest fixtures
@pytest.fixture
def test_config():
    """Returns test configuration"""
    return TEST_CONFIG

@pytest.fixture
def sample_faq_entry():
    """Returns a sample FAQ entry for testing"""
    return {
        "query": "Как установить бота?",
        "variations": ["установка бота", "инструкция по установке"],
        "response": "Для установки бота выполните следующие шаги:",
        "resources": [
            {
                "title": "Руководство по установке",
                "type": "file",
                "files": ["install_guide.pdf"]
            }
        ]
    }

@pytest.fixture
def sample_faq_data():
    """Returns sample FAQ data for testing"""
    return [
        {
            "query": "Как установить бота?",
            "variations": ["установка бота", "инструкция по установке"],
            "response": "Для установки бота выполните следующие шаги:",
            "resources": [
                {
                    "title": "Руководство по установке",
                    "type": "file",
                    "files": ["install_guide.pdf"]
                }
            ]
        },
        {
            "query": "Где найти документацию?",
            "variations": ["документация", "руководство пользователя"],
            "response": "Документация доступна по следующим ссылкам:",
            "resources": [
                {
                    "title": "Официальная документация",
                    "type": "link",
                    "link": "https://example.com/docs"
                }
            ]
        }
    ]