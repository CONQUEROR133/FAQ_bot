#!/usr/bin/env python3
"""
Simple test to verify core FAQ bot functionality
"""

import sys
import os

def test_imports():
    """Test that all core modules can be imported"""
    print("🔍 Testing core module imports...")
    
    try:
        # Test aiogram
        import aiogram
        print(f"✅ aiogram: {aiogram.__version__}")
    except ImportError as e:
        print(f"❌ aiogram import failed: {e}")
        return False
    
    try:
        # Test sentence-transformers
        import sentence_transformers
        print(f"✅ sentence-transformers: {sentence_transformers.__version__}")
    except ImportError as e:
        print(f"❌ sentence-transformers import failed: {e}")
        return False
    
    try:
        # Test faiss
        import faiss
        print(f"✅ faiss-cpu: {faiss.__version__}")
    except ImportError as e:
        print(f"❌ faiss-cpu import failed: {e}")
        return False
    
    try:
        # Test python-dotenv
        import dotenv
        print(f"✅ python-dotenv: OK")
    except ImportError as e:
        print(f"❌ python-dotenv import failed: {e}")
        return False
    
    try:
        # Test psutil
        import psutil
        print(f"✅ psutil: {psutil.__version__}")
    except ImportError as e:
        print(f"❌ psutil import failed: {e}")
        return False
    
    return True

def test_project_structure():
    """Test that essential project files and directories exist"""
    print("\n🔍 Testing project structure...")
    
    # Essential files
    essential_files = [
        ".env",
        "requirements.txt",
        "run.py",
        "setup.py",
        "train_model.py"
    ]
    
    for file in essential_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} not found")
            return False
    
    # Essential directories
    essential_dirs = [
        "src",
        "data",
        "cache",
        "logs",
        "tests"
    ]
    
    for dir_name in essential_dirs:
        if os.path.exists(dir_name) and os.path.isdir(dir_name):
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/ not found")
            return False
    
    return True

def test_faq_data():
    """Test that FAQ data file exists and is valid"""
    print("\n🔍 Testing FAQ data...")
    
    faq_file = os.path.join("data", "faq.json")
    if not os.path.exists(faq_file):
        print(f"❌ {faq_file} not found")
        return False
    
    try:
        import json
        with open(faq_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ FAQ data file valid, contains {len(data)} entries")
        return True
    except Exception as e:
        print(f"❌ FAQ data file invalid: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 FAQ Bot Core Functionality Test")
    print("=" * 40)
    
    # Run all tests
    tests = [
        test_imports,
        test_project_structure,
        test_faq_data
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 40)
    print("📋 Test Results Summary")
    print("=" * 40)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All {total} tests passed! The FAQ bot is ready for use.")
        return 0
    else:
        print(f"⚠️  {passed}/{total} tests passed. Some issues need attention.")
        return 1

if __name__ == "__main__":
    sys.exit(main())