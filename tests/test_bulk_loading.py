#!/usr/bin/env python3
"""
Test Bulk Loading Functionality
Demonstrates bulk loading without requiring external dependencies initially
"""

import os
import json
import sys
import shutil
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_functionality():
    """Test basic functionality without pandas"""
    print("🧪 Testing basic bulk loading functionality...")
    
    # Test JSON loading (no external dependencies)
    test_data = [
        {
            "query": "Тест вопрос 1", 
            "variations": ["тест 1", "вопрос 1"],
            "response": "Ответ на тест 1",
            "resources": [
                {
                    "title": "Тестовый документ",
                    "type": "file",
                    "files": ["test_file_1.pdf"]
                }
            ]
        },
        {
            "query": "Тест вопрос 2",
            "variations": ["тест 2", "вопрос 2"], 
            "response": "Ответ на тест 2",
            "resources": [
                {
                    "title": "Тестовая ссылка",
                    "type": "link",
                    "link": "https://example.com"
                }
            ]
        }
    ]
    
    # Save test data
    test_file = "test_data.json"
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Created test file: {test_file}")
    
    # Test basic loading without external dependencies
    try:
        from bulk_loader import BulkFAQLoader
        print("❌ Bulk loader requires pandas - install dependencies first")
        return False
    except ImportError as e:
        print(f"⚠️ Dependencies not installed: {e}")
        print("💡 Run: pip install pandas openpyxl tkinterdnd2")
        return False

def create_simple_csv_test():
    """Create a simple CSV test file"""
    print("📊 Creating simple CSV test...")
    
    csv_content = """query,variations,response,files,title
Простой тест,"тест;проверка","Это тестовый ответ","test.pdf","Тестовый файл"
Другой тест,"другой;второй","Это другой ответ","test2.pdf","Другой файл"
Третий тест,"третий;последний","Это третий ответ","test3.pdf;test3.docx","Третий файл"
"""
    
    with open("simple_test.csv", 'w', encoding='utf-8') as f:
        f.write(csv_content)
    
    print("✅ Created simple_test.csv")
    return "simple_test.csv"

def create_folder_structure_test():
    """Create test folder structure"""
    print("📁 Creating test folder structure...")
    
    test_dir = "test_bulk_files"
    os.makedirs(test_dir, exist_ok=True)
    
    # Create sample files
    categories = ["manuals", "guides", "forms"]
    
    for category in categories:
        cat_dir = os.path.join(test_dir, category)
        os.makedirs(cat_dir, exist_ok=True)
        
        for i in range(3):
            file_path = os.path.join(cat_dir, f"{category}_{i+1}.txt")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"Sample content for {category} #{i+1}\n")
                f.write(f"This is a test file in the {category} category.\n")
    
    print(f"✅ Created test folder structure: {test_dir}")
    return test_dir

def create_text_list_test():
    """Create text list test file"""
    print("📄 Creating text list test...")
    
    txt_content = """# FAQ Text List Test
# Format: query|files|links|additional_text
Текстовый тест 1|test1.pdf||Дополнительная информация для теста 1
Текстовый тест 2|test2.pdf;test2.docx|https://example.com|Информация с файлами и ссылкой
Текстовый тест 3||https://google.com|Только ссылка без файлов
"""
    
    with open("text_list_test.txt", 'w', encoding='utf-8') as f:
        f.write(txt_content)
    
    print("✅ Created text_list_test.txt")
    return "text_list_test.txt"

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required = ['pandas', 'openpyxl', 'tkinterdnd2']
    missing = []
    
    for module in required:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module}")
            missing.append(module)
    
    if missing:
        print(f"\n⚠️ Missing dependencies: {', '.join(missing)}")
        print("💡 Install with: pip install " + ' '.join(missing))
        return False
    else:
        print("\n✅ All dependencies installed!")
        return True

def run_actual_test():
    """Run actual bulk loading test if dependencies are available"""
    print("🚀 Running actual bulk loading test...")
    
    try:
        from bulk_loader import BulkFAQLoader
        
        loader = BulkFAQLoader()
        
        # Test JSON loading
        print("\n1. Testing JSON loading...")
        test_data = [
            {
                "query": "JSON тест",
                "variations": ["json", "тест"],
                "response": "JSON тестовый ответ",
                "resources": [{"title": "JSON файл", "type": "file", "files": ["json_test.pdf"]}]
            }
        ]
        
        with open("test_json.json", 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        new_count, total_count = loader.bulk_import("test_json.json", "json", merge=True)
        print(f"   ✅ JSON: Added {new_count} entries, total: {total_count}")
        
        # Test folder loading
        print("\n2. Testing folder loading...")
        test_dir = create_folder_structure_test()
        new_count, total_count = loader.bulk_import(test_dir, "folder", merge=True)
        print(f"   ✅ Folder: Added {new_count} entries, total: {total_count}")
        
        # Test CSV loading (if pandas available)
        print("\n3. Testing CSV loading...")
        csv_file = create_simple_csv_test()
        new_count, total_count = loader.bulk_import(csv_file, "csv", merge=True)
        print(f"   ✅ CSV: Added {new_count} entries, total: {total_count}")
        
        # Test text list loading
        print("\n4. Testing text list loading...")
        txt_file = create_text_list_test()
        new_count, total_count = loader.bulk_import(txt_file, "txt", merge=True)
        print(f"   ✅ Text: Added {new_count} entries, total: {total_count}")
        
        print(f"\n🎉 All tests passed! Final FAQ size: {total_count} entries")
        
        # Show current FAQ summary
        faq_data = loader.load_existing_faq()
        print(f"\n📚 Current FAQ summary:")
        for i, entry in enumerate(faq_data[-10:], max(1, len(faq_data)-9)):  # Show last 10
            query = entry.get('query', 'No title')
            resources = len(entry.get('resources', []))
            print(f"  {i}. {query} ({resources} resources)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Bulk FAQ Loader Test Suite")
    print("=" * 50)
    
    # Check dependencies first
    deps_ok = check_dependencies()
    
    if deps_ok:
        print("\n🚀 Dependencies available - running full tests...")
        if run_actual_test():
            print("\n✅ All tests completed successfully!")
            print("💡 You can now use the bulk loader tools:")
            print("   - python bulk_loader.py --templates")
            print("   - python faq_gui.py")
            print("   - python drag_drop_loader.py")
            print("   - 3_bulk_loader.bat")
        else:
            print("\n❌ Some tests failed")
    else:
        print("\n⚠️ Dependencies missing - creating test files only...")
        
        # Create test files anyway
        create_simple_csv_test()
        create_folder_structure_test() 
        create_text_list_test()
        
        print("\n📋 Test files created! Install dependencies and run again:")
        print("   pip install pandas openpyxl tkinterdnd2")
        print("   python test_bulk_loading.py")

if __name__ == "__main__":
    main()