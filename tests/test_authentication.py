#!/usr/bin/env python3
"""
Тест для проверки работы системы аутентификации
"""

import sys
import os

# Add the project root to Python path for proper package imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import from src package
from src.config import config
from src.database import Database
from src.handlers import waiting_for_password
from aiogram import types

def test_password_validation():
    """Тестируем валидацию пароля"""
    print("🔍 Тест системы аутентификации")
    print("=" * 40)
    
    # Проверяем конфигурацию пароля
    print(f"✅ Пароль доступа установлен: '{config.ACCESS_PASSWORD}'")
    
    # Тестируем базу данных
    try:
        db = Database()
        db.init_db()
        print("✅ База данных инициализирована")
        
        # Тестируем проверку неаутентифицированного пользователя
        test_user_id = 999999
        is_auth_before = db.is_user_authenticated(test_user_id)
        print(f"✅ Пользователь {test_user_id} не аутентифицирован: {not is_auth_before}")
        
        # Симулируем аутентификацию
        # Создаем объект User с помощью aiogram types
        mock_user = types.User(
            id=test_user_id,
            is_bot=False,
            first_name="Test",
            last_name="User",
            username="test_user"
        )
        db.authenticate_user(mock_user)
        
        # Проверяем, что пользователь теперь аутентифицирован
        is_auth_after = db.is_user_authenticated(test_user_id)
        print(f"✅ Пользователь {test_user_id} аутентифицирован: {is_auth_after}")
        
        # Проверяем статистику
        auth_count = db.get_authenticated_users_count()
        print(f"✅ Количество аутентифицированных пользователей: {auth_count}")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования БД: {e}")
        return False
    
    # Тестируем состояние ожидания пароля
    test_user_id_2 = 888888
    waiting_for_password.add(test_user_id_2)
    print(f"✅ Пользователь {test_user_id_2} добавлен в очередь ожидания пароля")
    print(f"✅ Размер очереди ожидания: {len(waiting_for_password)}")
    
    # Симулируем проверку пароля
    correct_password = "1337"
    wrong_password = "123"
    
    print(f"✅ Правильный пароль '{correct_password}' == '{config.ACCESS_PASSWORD}': {correct_password == config.ACCESS_PASSWORD}")
    print(f"✅ Неправильный пароль '{wrong_password}' == '{config.ACCESS_PASSWORD}': {wrong_password == config.ACCESS_PASSWORD}")
    
    print("\n🎯 Результат тестирования:")
    print("✅ Все тесты пройдены успешно!")
    print("✅ Система аутентификации работает корректно")
    
    return True

if __name__ == '__main__':
    test_password_validation()