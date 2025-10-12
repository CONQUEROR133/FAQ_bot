#!/usr/bin/env python3
"""
Test script to verify current bot functionality is still working
"""

import sys
import os
import json

# Add the src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_config_loading():
    """Test that config loads correctly"""
    print("🔍 Testing config loading...")
    
    try:
        from config import config
        print("✅ Config loaded successfully")
        print(f"   BOT_TOKEN configured: {'Yes' if config.BOT_TOKEN else 'No'}")
        print(f"   ADMIN_ID: {config.ADMIN_ID}")
        return True
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return False

def test_faq_loader_import():
    """Test that FAQ loader can be imported"""
    print("\n🔍 Testing FAQ loader import...")
    
    try:
        from faq_loader import FAQLoader
        print("✅ FAQ loader imported successfully")
        return True
    except Exception as e:
        print(f"❌ Error importing FAQ loader: {e}")
        return False

def test_faq_structure():
    """Test that FAQ structure is valid"""
    print("\n🔍 Testing FAQ structure...")
    
    try:
        # Load FAQ data directly
        faq_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'faq.json')
        with open(faq_file_path, 'r', encoding='utf-8') as f:
            faq_data = json.load(f)
        
        print(f"✅ FAQ file loaded successfully with {len(faq_data)} entries")
        
        # Basic validation
        valid_entries = 0
        for entry in faq_data:
            if isinstance(entry, dict) and 'query' in entry:
                valid_entries += 1
        
        print(f"✅ Valid entries: {valid_entries}/{len(faq_data)}")
        return valid_entries == len(faq_data)
        
    except Exception as e:
        print(f"❌ Error testing FAQ structure: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing current bot functionality...\n")
    
    tests = [
        test_config_loading,
        test_faq_loader_import,
        test_faq_structure
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! Bot is functioning correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)