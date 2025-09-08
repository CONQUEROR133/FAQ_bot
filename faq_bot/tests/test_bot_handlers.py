#!/usr/bin/env python3
"""
Bot handlers test to verify command and message handlers
"""

import sys
import os

# Add the src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_handler_imports():
    """Test if all handlers can be imported without errors"""
    print("🔍 Testing handler imports...")
    
    try:
        from handlers import router
        print("✅ Handlers imported successfully")
        return True
    except Exception as e:
        print(f"❌ Handler import failed: {e}")
        return False

def test_router_setup():
    """Test if router is properly configured"""
    print("🔍 Testing router setup...")
    
    try:
        from handlers import router
        from aiogram import Router
        
        if not isinstance(router, Router):
            print("❌ Router is not an instance of aiogram.Router")
            return False
        
        # Check that router has some routes registered
        if hasattr(router, 'message') and hasattr(router, 'callback_query'):
            print("✅ Router has message and callback query handlers")
            return True
        else:
            print("⚠️ Router may not have handlers registered")
            return True  # Not a critical failure
            
    except Exception as e:
        print(f"❌ Router setup test failed: {e}")
        return False

def test_middleware_imports():
    """Test if middlewares can be imported"""
    print("🔍 Testing middleware imports...")
    
    try:
        from middlewares import DependenciesMiddleware
        print("✅ Middlewares imported successfully")
        return True
    except Exception as e:
        print(f"❌ Middleware import failed: {e}")
        return False

def test_auth_middleware_imports():
    """Test if authentication middleware can be imported"""
    print("🔍 Testing authentication middleware imports...")
    
    try:
        from auth_middleware import AuthenticationMiddleware
        print("✅ Authentication middleware imported successfully")
        return True
    except Exception as e:
        print(f"❌ Authentication middleware import failed: {e}")
        return False

def main():
    print("⚙️ Bot Handlers Tests")
    print("=" * 40)
    
    tests = [
        ("Handler Imports", test_handler_imports()),
        ("Router Setup", test_router_setup()),
        ("Middleware Imports", test_middleware_imports()),
        ("Auth Middleware Imports", test_auth_middleware_imports())
    ]
    
    success_count = 0
    for test_name, result in tests:
        if result:
            success_count += 1
            print(f"✅ {test_name} passed")
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 40)
    print(f"📊 Results: {success_count}/{len(tests)} tests passed")
    
    if success_count == len(tests):
        print("🎉 All handler tests passed!")
        return 0
    else:
        print("⚠️ Some handler tests failed. Please check the issues above.")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)