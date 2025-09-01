#!/usr/bin/env python3
"""
Example: Programmatic Bulk FAQ Generation
Demonstrates how to programmatically create and load large amounts of FAQ data
"""

import os
import csv
import json
from pathlib import Path
from bulk_loader import BulkFAQLoader

def generate_sample_csv(filename="sample_1000_files.csv", count=1000):
    """Generate a sample CSV with many FAQ entries"""
    print(f"🔄 Generating {count} sample FAQ entries...")
    
    # Sample data templates
    queries = [
        "Инструкция по {topic}",
        "Как работать с {topic}",
        "Документация {topic}", 
        "Руководство {topic}",
        "Памятка по {topic}",
        "Настройка {topic}",
        "Установка {topic}",
        "Обновление {topic}",
        "Техподдержка {topic}",
        "FAQ по {topic}"
    ]
    
    topics = [
        "1С", "CRM", "ERP", "касса", "терминал", "платежи", "интеграция",
        "API", "веб-сайт", "мобильное приложение", "база данных", "отчеты",
        "аналитика", "безопасность", "резервное копирование", "обновления",
        "пользователи", "роли", "права доступа", "настройки", "конфигурация",
        "импорт", "экспорт", "синхронизация", "документооборот", "workflow",
        "уведомления", "email", "SMS", "push", "интерфейс", "дизайн",
        "производительность", "оптимизация", "мониторинг", "логирование",
        "тестирование", "отладка", "развертывание", "DevOps", "CI/CD"
    ]
    
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['query', 'variations', 'response', 'files', 'title'])
        
        for i in range(count):
            topic = topics[i % len(topics)]
            query_template = queries[i % len(queries)]
            query = query_template.format(topic=topic)
            
            # Generate variations
            variations = [
                f"{topic} инструкция",
                f"как {topic}",
                f"{topic} помощь"
            ]
            
            # Simulate file paths (replace with real paths)
            files = [
                f"files/{topic}_manual_{i}.pdf",
                f"files/{topic}_guide_{i}.docx"
            ]
            
            writer.writerow([
                query,
                ';'.join(variations),
                f"По вопросу '{topic}' есть следующие материалы:",
                ';'.join(files),
                f"Документация по {topic}"
            ])
    
    print(f"✅ Generated {filename} with {count} entries")
    return filename

def generate_from_folder_structure():
    """Example: Generate FAQ from existing folder structure"""
    print("📁 Generating FAQ from folder structure...")
    
    # Create sample folder structure
    sample_dir = "sample_files"
    os.makedirs(sample_dir, exist_ok=True)
    
    # Create sample subdirectories and files
    categories = ["manuals", "guides", "templates", "forms", "reports"]
    
    for category in categories:
        cat_dir = os.path.join(sample_dir, category)
        os.makedirs(cat_dir, exist_ok=True)
        
        # Create sample files
        for i in range(5):
            file_path = os.path.join(cat_dir, f"{category}_{i+1}.txt")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"Sample content for {category} #{i+1}")
    
    # Load using bulk loader
    loader = BulkFAQLoader()
    new_count, total_count = loader.bulk_import(
        source=sample_dir,
        format_type="folder",
        merge=True,
        group_by_extension=False  # Create individual entries
    )
    
    print(f"✅ Created {new_count} FAQ entries from folder structure")
    return new_count, total_count

def generate_json_data(filename="sample_data.json"):
    """Generate structured JSON data"""
    print("📄 Generating JSON data...")
    
    data = []
    
    departments = ["IT", "HR", "Finance", "Sales", "Support", "Marketing"]
    
    for dept in departments:
        for i in range(10):
            entry = {
                "query": f"Процедуры отдела {dept} - {i+1}",
                "variations": [
                    f"{dept} процедура {i+1}",
                    f"отдел {dept} {i+1}",
                    f"{dept.lower()} {i+1}"
                ],
                "response": f"Документация по процедурам отдела {dept}:",
                "resources": [
                    {
                        "title": f"Регламент {dept} #{i+1}",
                        "type": "file",
                        "files": [f"files/{dept.lower()}_procedure_{i+1}.pdf"]
                    },
                    {
                        "title": f"Инструкция {dept} #{i+1}",
                        "type": "link", 
                        "link": f"https://company.com/{dept.lower()}/procedure-{i+1}"
                    }
                ]
            }
            data.append(entry)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Generated {filename} with {len(data)} structured entries")
    return filename

def demo_all_methods():
    """Demonstrate all bulk loading methods"""
    print("🚀 Bulk FAQ Loading Demo")
    print("=" * 50)
    
    loader = BulkFAQLoader()
    
    # Method 1: CSV generation and loading
    print("\n1. CSV Method:")
    csv_file = generate_sample_csv("demo_data.csv", 50)
    new_count, total_count = loader.bulk_import(csv_file, "csv", merge=True)
    print(f"   Added {new_count} entries from CSV")
    
    # Method 2: Folder structure
    print("\n2. Folder Method:")
    new_count, total_count = generate_from_folder_structure()
    print(f"   Added {new_count} entries from folder")
    
    # Method 3: JSON data
    print("\n3. JSON Method:")
    json_file = generate_json_data("demo_data.json")
    new_count, total_count = loader.bulk_import(json_file, "json", merge=True)
    print(f"   Added {new_count} entries from JSON")
    
    print(f"\n🎉 Demo completed! Total FAQ entries: {total_count}")
    print("💡 Now restart your bot to see the new entries!")

def quick_1000_files_setup():
    """Quick setup for 1000 files scenario"""
    print("⚡ Quick 1000 Files Setup")
    print("=" * 30)
    
    # Generate large CSV
    csv_file = generate_sample_csv("bulk_1000_files.csv", 1000)
    
    # Load it
    loader = BulkFAQLoader()
    new_count, total_count = loader.bulk_import(csv_file, "csv", merge=True)
    
    print(f"✅ Successfully loaded {new_count} FAQ entries!")
    print(f"📊 Total entries in FAQ: {total_count}")
    print("🔄 Restart bot with: restart_bot.bat")
    
    return total_count

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "demo":
            demo_all_methods()
        elif sys.argv[1] == "1000":
            quick_1000_files_setup()
        elif sys.argv[1] == "csv":
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 100
            generate_sample_csv("generated_data.csv", count)
        else:
            print("Usage: python example_bulk_load.py [demo|1000|csv [count]]")
    else:
        print("🎯 Example Bulk Loading Options:")
        print("  python example_bulk_load.py demo     - Run full demo")
        print("  python example_bulk_load.py 1000     - Quick 1000 files setup")
        print("  python example_bulk_load.py csv 500  - Generate CSV with 500 entries")