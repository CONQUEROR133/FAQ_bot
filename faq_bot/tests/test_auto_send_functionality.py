#!/usr/bin/env python3
"""
Test script to verify auto_send functionality
"""

import sys
import os
import json

# Add the src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_auto_send_logic():
    """Test the auto_send logic function"""
    print("🔍 Testing auto_send logic...")
    
    try:
        from handlers import should_auto_send_resource
        print("✅ should_auto_send_resource function imported successfully")
    except Exception as e:
        print(f"❌ Error importing should_auto_send_resource: {e}")
        return False
    
    # Test cases
    test_cases = [
        # Test 1: Resource with explicit auto_send=True
        (
            "auto_send=True resource",
            [{'type': 'file', 'files': ['test.pdf'], 'auto_send': True}],
            True
        ),
        # Test 2: Resource with explicit auto_send=False should fall back to default logic
        (
            "auto_send=False resource",
            [{'type': 'file', 'files': ['test.pdf'], 'auto_send': False}],
            True  # Should still be True because it's a single file
        ),
        # Test 3: Link resource (should always auto-send)
        (
            "Link resource",
            [{'type': 'link', 'link': 'http://example.com'}],
            True
        ),
        # Test 4: Single file resource (should auto-send)
        (
            "Single file resource",
            [{'type': 'file', 'files': ['test.pdf']}],
            True
        ),
        # Test 5: Multiple files resource (should NOT auto-send)
        (
            "Multiple files resource",
            [{'type': 'file', 'files': ['test1.pdf', 'test2.pdf']}],
            False
        )
    ]
    
    passed = 0
    for test_name, resources, expected in test_cases:
        should_auto, _ = should_auto_send_resource(resources)
        if should_auto == expected:
            print(f"✅ Test {passed+1} passed: {test_name}")
            passed += 1
        else:
            print(f"❌ Test {passed+1} failed: {test_name} - expected {expected}, got {should_auto}")
    
    print(f"\n📊 Auto-send logic test results: {passed}/{len(test_cases)} tests passed")
    return passed == len(test_cases)

def test_faq_entries():
    """Test that FAQ entries have correct auto_send flags"""
    print("\n🔍 Testing FAQ entries for auto_send flags...")
    
    try:
        # Load FAQ data
        faq_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'faq.json')
        with open(faq_file_path, 'r', encoding='utf-8') as f:
            faq_data = json.load(f)
        
        print(f"✅ FAQ file loaded successfully with {len(faq_data)} entries")
        
        # Check specific entries
        expected_entries = {
            "Сканер": True,
            "Чек-Лист": None,  # Special case - first False, second True
            "platinum": True,
            "ТреидИн": True,
            "Категории": True
        }
        
        found_entries = 0
        for entry in faq_data:
            query = entry.get('query')
            if query in expected_entries:
                if query == "Чек-Лист":
                    # Special handling for Чек-Лист
                    if 'resources' in entry and len(entry['resources']) >= 2:
                        first_resource = entry['resources'][0]
                        second_resource = entry['resources'][1]
                        
                        first_auto_send = first_resource.get('auto_send', False)
                        second_auto_send = second_resource.get('auto_send', False)
                        
                        if not first_auto_send and second_auto_send:
                            print(f"✅ {query}: Correctly configured (first: {first_auto_send}, second: {second_auto_send})")
                            found_entries += 1
                        else:
                            print(f"❌ {query}: Incorrectly configured (first: {first_auto_send}, second: {second_auto_send})")
                else:
                    # Normal handling for other entries
                    if 'resources' in entry and len(entry['resources']) > 0:
                        resource = entry['resources'][0]
                        auto_send = resource.get('auto_send', False)
                        expected = expected_entries[query]
                        
                        if auto_send == expected:
                            print(f"✅ {query}: Correctly configured (auto_send: {auto_send})")
                            found_entries += 1
                        else:
                            print(f"❌ {query}: Incorrectly configured (auto_send: {auto_send}, expected: {expected})")
        
        expected_count = len(expected_entries)
        print(f"\n📊 FAQ entries test results: {found_entries}/{expected_count} entries correctly configured")
        return found_entries == expected_count
        
    except Exception as e:
        print(f"❌ Error testing FAQ entries: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing auto_send functionality...\n")
    
    tests = [
        test_auto_send_logic,
        test_faq_entries
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! Auto_send functionality is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)