#!/usr/bin/env python3
"""
Integration test to verify that the auto_send functionality works with the FAQ loader
"""

import sys
import os
import json

# Add the src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_faq_loader_with_auto_send():
    """Test that FAQ loader works with our auto_send changes"""
    print("🔍 Testing FAQ loader with auto_send functionality...")
    
    try:
        from faq_loader import FAQLoader
        from config import config
        print("✅ FAQ loader and config imported successfully")
    except Exception as e:
        print(f"❌ Error importing modules: {e}")
        return False
    
    try:
        # Initialize FAQ loader
        loader = FAQLoader()
        stats = loader.load_faq()
        print(f"✅ FAQ loaded successfully: {stats.valid_queries} valid entries")
        
        # Check if FAQ data is loaded
        if loader.faq is None:
            print("❌ FAQ data is None")
            return False
            
        # Find entries with auto_send resources
        auto_send_entries = []
        for i, entry in enumerate(loader.faq):
            if 'resources' in entry:
                for j, resource in enumerate(entry['resources']):
                    if resource.get('auto_send') is True:
                        auto_send_entries.append({
                            'entry_index': i,
                            'entry_query': entry.get('query', 'Unknown'),
                            'resource_index': j,
                            'resource_title': resource.get('title', 'Unknown')
                        })
        
        print(f"✅ Found {len(auto_send_entries)} resources with auto_send flag:")
        for entry in auto_send_entries:
            print(f"   - Entry '{entry['entry_query']}' resource '{entry['resource_title']}' (index {entry['entry_index']}.{entry['resource_index']})")
        
        # Verify we found the expected entries
        expected_queries = {"Сканер", "Чек-Лист", "platinum", "ТреидИн", "Категории"}
        found_queries = {entry['entry_query'] for entry in auto_send_entries}
        
        # Special handling for Чек-Лист - we only set auto_send on the second resource
        if "Чек-Лист" in found_queries:
            print("✅ Чек-Лист entry correctly has auto_send on second resource")
        elif "Чек-Лист" in expected_queries:
            # This might be okay if we only set it on the second resource
            # Let's check specifically
            checklist_entry = None
            for i, entry in enumerate(loader.faq):
                if entry.get('query') == "Чек-Лист":
                    checklist_entry = entry
                    break
            
            if checklist_entry and 'resources' in checklist_entry and len(checklist_entry['resources']) >= 2:
                second_resource = checklist_entry['resources'][1]
                if second_resource.get('auto_send') is True:
                    print("✅ Чек-Лист entry correctly has auto_send on second resource")
                    # Remove from expected since we found it in the right place
                    expected_queries.remove("Чек-Лист")
                    found_queries.add("Чек-Лист")
        
        missing_queries = expected_queries - found_queries
        if missing_queries:
            print(f"❌ Missing auto_send entries for queries: {missing_queries}")
            return False
        
        print("✅ All expected auto_send entries found")
        return True
        
    except Exception as e:
        print(f"❌ Error testing FAQ loader: {e}")
        return False

def test_handler_logic_with_faq_data():
    """Test that handler logic works correctly with actual FAQ data"""
    print("🔍 Testing handler logic with actual FAQ data...")
    
    try:
        from handlers import should_auto_send_resource
        from faq_loader import FAQLoader
        from config import config
        print("✅ Required modules imported successfully")
    except Exception as e:
        print(f"❌ Error importing modules: {e}")
        return False
    
    try:
        # Load FAQ data
        loader = FAQLoader()
        loader.load_faq()
        
        # Check if FAQ data is loaded
        if loader.faq is None:
            print("❌ FAQ data is None")
            return False
        
        # Test specific entries
        test_cases = [
            ("Сканер", 0, True),  # First resource should auto_send
            ("Чек-Лист", 1, True),  # Second resource should auto_send
            ("platinum", 0, True),  # First resource should auto_send
            ("ТреидИн", 0, True),  # First resource should auto_send
            ("Категории", 0, True),  # First resource should auto_send
        ]
        
        for query, resource_index, expected_auto_send in test_cases:
            # Find the entry
            entry = None
            for faq_entry in loader.faq:
                if faq_entry.get('query') == query:
                    entry = faq_entry
                    break
            
            if not entry:
                print(f"❌ Entry '{query}' not found in FAQ data")
                return False
            
            if 'resources' not in entry or len(entry['resources']) <= resource_index:
                print(f"❌ Entry '{query}' doesn't have resource at index {resource_index}")
                return False
            
            resource = entry['resources'][resource_index]
            should_auto, returned_resource = should_auto_send_resource([resource])
            
            if should_auto == expected_auto_send:
                print(f"✅ Entry '{query}' resource '{resource.get('title', 'Unknown')}' correctly set for auto_send: {should_auto}")
            else:
                print(f"❌ Entry '{query}' resource '{resource.get('title', 'Unknown')}' incorrectly set for auto_send: expected {expected_auto_send}, got {should_auto}")
                return False
        
        print("✅ All handler logic tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing handler logic: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🧪 Running integration tests...\n")
    
    tests = [
        test_faq_loader_with_auto_send,
        test_handler_logic_with_faq_data
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}\n")
    
    print(f"📊 Integration test results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All integration tests passed! The improvements are working correctly.")
        return True
    else:
        print("❌ Some integration tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)