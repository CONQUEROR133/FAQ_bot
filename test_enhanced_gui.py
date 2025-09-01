#!/usr/bin/env python3
"""
Enhanced FAQ GUI - Functionality Test
Demonstrates the capabilities of the enhanced interface
"""

import sys
import os
from pathlib import Path

# Add utils to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

def test_smart_file_processor():
    """Test smart file processing capabilities"""
    print("🧪 Testing Smart File Processor...")
    
    try:
        from enhanced_faq_gui import SmartFileProcessor
        
        processor = SmartFileProcessor()
        
        # Test file type detection
        test_files = [
            "test.csv",
            "data.xlsx", 
            "config.json",
            "readme.txt",
            "document.pdf"
        ]
        
        for filename in test_files:
            file_type = processor.detect_file_type(filename)
            print(f"  📄 {filename} -> {file_type}")
        
        print("✅ Smart File Processor test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Smart File Processor test failed: {e}")
        return False

def test_faq_validator():
    """Test FAQ validation functionality"""
    print("\n🧪 Testing FAQ Validator...")
    
    try:
        from smart_faq_processor import FAQValidator
        
        validator = FAQValidator()
        
        # Test valid entry
        valid_entry = {
            "query": "How to login?",
            "variations": ["login process", "sign in"],
            "response": "По вашему запросу есть следующее:",
            "resources": [
                {
                    "type": "file",
                    "title": "Login Guide",
                    "files": ["login_guide.pdf"]
                }
            ]
        }
        
        result = validator.validate_entry(valid_entry)
        print(f"  ✅ Valid entry: {len(result['errors'])} errors, {len(result['warnings'])} warnings")
        
        # Test invalid entry
        invalid_entry = {
            "variations": ["test"],
            "resources": []
        }
        
        result = validator.validate_entry(invalid_entry)
        print(f"  ❌ Invalid entry: {len(result['errors'])} errors, {len(result['warnings'])} warnings")
        
        print("✅ FAQ Validator test passed!")
        return True
        
    except Exception as e:
        print(f"❌ FAQ Validator test failed: {e}")
        return False

def test_smart_merger():
    """Test smart FAQ merging"""
    print("\n🧪 Testing Smart FAQ Merger...")
    
    try:
        from smart_faq_processor import SmartFAQMerger
        
        merger = SmartFAQMerger()
        
        existing_faq = [
            {
                "query": "How to login",
                "variations": ["sign in"],
                "resources": [{"type": "link", "link": "https://example.com/login"}]
            }
        ]
        
        new_faq = [
            {
                "query": "Login process",
                "variations": ["how to sign in"],
                "resources": [{"type": "file", "files": ["login_guide.pdf"]}]
            },
            {
                "query": "Password reset",
                "variations": ["forgot password"],
                "resources": [{"type": "link", "link": "https://example.com/reset"}]
            }
        ]
        
        merged_faq, report = merger.merge_faqs(existing_faq, new_faq)
        
        print(f"  📊 Merge Results:")
        print(f"    Added: {report.get('added', 0)}")
        print(f"    Updated: {report.get('updated', 0)}")
        print(f"    Total: {report.get('total', 0)}")
        print(f"    Conflicts: {len(report.get('conflicts', []))}")
        
        print("✅ Smart FAQ Merger test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Smart FAQ Merger test failed: {e}")
        return False

def test_progress_manager():
    """Test progress tracking system"""
    print("\n🧪 Testing Progress Manager...")
    
    try:
        import tkinter as tk
        from tkinter import ttk
        
        # Create minimal GUI for testing
        root = tk.Tk()
        root.withdraw()  # Hide window
        
        progress_bar = ttk.Progressbar(root)
        status_label = ttk.Label(root)
        
        # Mock text widget
        class MockText:
            def insert(self, pos, text): pass
            def see(self, pos): pass
        
        from enhanced_faq_gui import ProgressManager
        
        progress_mgr = ProgressManager(progress_bar, status_label, MockText())
        
        # Test progress operations
        progress_mgr.start(5, "Testing progress...")
        for i in range(5):
            progress_mgr.step(f"Step {i+1}")
        progress_mgr.finish("Test complete!")
        
        root.destroy()
        
        print("✅ Progress Manager test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Progress Manager test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 Enhanced FAQ GUI - Functionality Tests")
    print("=" * 60)
    
    tests = [
        test_smart_file_processor,
        test_faq_validator, 
        test_smart_merger,
        test_progress_manager
    ]
    
    results = []
    for test_func in tests:
        results.append(test_func())
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Enhanced GUI is ready for use.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    print("\n💡 To launch the Enhanced FAQ GUI:")
    print("   - Windows: Double-click Enhanced_FAQ_Loader.bat")
    print("   - Python:  python utils/launch_enhanced_gui.py")
    print("   - Direct:  python utils/enhanced_faq_gui.py")

if __name__ == "__main__":
    main()