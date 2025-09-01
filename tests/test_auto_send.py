#!/usr/bin/env python3
"""
Test script for automatic resource sending functionality
"""

import sys
import os
import json

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_should_auto_send_logic():
    """Test the should_auto_send_resource logic"""
    print("🔍 Testing automatic sending logic...")
    
    # Import the function
    from handlers import should_auto_send_resource
    
    # Test cases
    test_cases = [
        {
            "name": "Single file resource (should auto-send)",
            "resources": [
                {
                    "title": "Маркетинговые вставки FF7",
                    "type": "file",
                    "files": ["files/ff7_inserts.jpg"]
                }
            ],
            "expected": True
        },
        {
            "name": "Single link resource (should auto-send)",
            "resources": [
                {
                    "title": "Инструкция по оформлению рассрочки",
                    "type": "link",
                    "link": "https://telegra.ph/Instrukciya-oformleniya-rassrochki-v-1S-04-02"
                }
            ],
            "expected": True
        },
        {
            "name": "Multiple files in one resource (should show keyboard)",
            "resources": [
                {
                    "title": "Заявление о Страховом Случае Альфа-Страхование",
                    "type": "file",
                    "files": ["files/Пример заполнения СС_Альфа.pdf", "files/Заявление о СС_Альфа.docx"]
                }
            ],
            "expected": False
        },
        {
            "name": "Multiple resources (should show keyboard)",
            "resources": [
                {
                    "title": "Памятка по Альфа-Страхованию",
                    "type": "file",
                    "files": ["files/Памятка_по_программам_страхования_в_Альфа_сен_24.pdf"]
                },
                {
                    "title": "Заявление о Страховом Случае Альфа-Страхование",
                    "type": "file",
                    "files": ["files/Пример заполнения СС_Альфа.pdf"]
                }
            ],
            "expected": False
        }
    ]
    
    all_passed = True
    for i, test_case in enumerate(test_cases, 1):
        should_auto, resource = should_auto_send_resource(test_case["resources"])
        expected = test_case["expected"]
        
        if should_auto == expected:
            print(f"✅ Test {i}: {test_case['name']}")
        else:
            print(f"❌ Test {i}: {test_case['name']} - Expected {expected}, got {should_auto}")
            all_passed = False
    
    return all_passed

def test_faq_examples():
    """Test with actual FAQ examples"""
    print("\n🔍 Testing with FAQ examples...")
    
    try:
        # Load FAQ file
        with open('faq.json', 'r', encoding='utf-8') as f:
            faq_data = json.load(f)
        
        from handlers import should_auto_send_resource
        
        for item in faq_data:
            query = item.get('query', 'Unknown')
            resources = item.get('resources', [])
            
            should_auto, resource = should_auto_send_resource(resources)
            
            if should_auto and resource:
                resource_type = resource.get('type', 'unknown')
                if resource_type == 'file':
                    files = resource.get('files', [])
                    print(f"✅ AUTO-SEND: '{query}' -> {resource_type} ({len(files)} file(s))")
                else:
                    print(f"✅ AUTO-SEND: '{query}' -> {resource_type}")
            else:
                print(f"⚪ KEYBOARD: '{query}' -> {len(resources)} resource(s)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    print("🤖 Testing Automatic Resource Sending")
    print("=" * 50)
    
    success = True
    success &= test_should_auto_send_logic()
    success &= test_faq_examples()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests passed!")
        print("Logic implemented correctly:")
        print("• Single file resource → Auto-send")
        print("• Single link resource → Auto-send") 
        print("• Multiple files/resources → Show keyboard")
    else:
        print("❌ Some tests failed!")