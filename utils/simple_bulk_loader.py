#!/usr/bin/env python3
"""
Simple Bulk FAQ Loader - Works without external dependencies
Basic functionality for quick file loading
"""

import os
import json
import shutil
import logging
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

class SimpleBulkFAQLoader:
    def __init__(self, faq_file=None, files_dir=None, backup_dir=None):
        # Get project root directory (parent of utils)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.faq_file = faq_file or os.path.join(project_root, "data", "faq.json")
        self.files_dir = files_dir or os.path.join(project_root, "files")
        self.backup_dir = backup_dir or os.path.join(project_root, "backups")
        
        # Ensure directories exist
        os.makedirs(self.files_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.faq_file), exist_ok=True)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def create_backup(self):
        """Create backup of current FAQ"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(self.backup_dir, f"faq_backup_{timestamp}.json")
        
        if os.path.exists(self.faq_file):
            shutil.copy2(self.faq_file, backup_file)
            self.logger.info(f"📦 Backup created: {backup_file}")
            return backup_file
        return None
    
    def load_existing_faq(self) -> List[Dict]:
        """Load existing FAQ data"""
        if os.path.exists(self.faq_file):
            try:
                with open(self.faq_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading existing FAQ: {e}")
        return []
    
    def save_faq(self, faq_data: List[Dict]):
        """Save FAQ data to file"""
        try:
            with open(self.faq_file, 'w', encoding='utf-8') as f:
                json.dump(faq_data, f, ensure_ascii=False, indent=2)
            self.logger.info(f"✅ FAQ saved with {len(faq_data)} items")
        except Exception as e:
            self.logger.error(f"Error saving FAQ: {e}")
            raise
    
    def copy_files_to_directory(self, source_files: List[str]) -> List[str]:
        """Copy files to the bot's files directory"""
        copied_files = []
        
        for source_file in source_files:
            if not os.path.exists(source_file):
                self.logger.warning(f"⚠️ File not found: {source_file}")
                continue
            
            filename = os.path.basename(source_file)
            # Handle duplicate filenames
            counter = 1
            base_name, ext = os.path.splitext(filename)
            dest_path = os.path.join(self.files_dir, filename)
            
            while os.path.exists(dest_path):
                filename = f"{base_name}_{counter}{ext}"
                dest_path = os.path.join(self.files_dir, filename)
                counter += 1
            
            try:
                shutil.copy2(source_file, dest_path)
                copied_files.append(os.path.join(self.files_dir, filename))
                self.logger.info(f"📁 Copied: {filename}")
            except Exception as e:
                self.logger.error(f"Error copying {source_file}: {e}")
        
        return copied_files
    
    def create_faq_entry(
        self, 
        query: str, 
        variations: Optional[List[str]] = None, 
        response: str = "По вашему запросу есть следующее:",
        files: Optional[List[str]] = None,
        links: Optional[List[str]] = None,
        additional_text: Optional[str] = None,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a standardized FAQ entry"""
        entry = {
            "query": query,
            "variations": variations or [],
            "response": response,
            "resources": []
        }
        
        # Add file resources
        if files:
            file_resource = {
                "title": title or f"Материалы по {query}",
                "type": "file",
                "files": files
            }
            if additional_text:
                file_resource["additional_text"] = additional_text
            entry["resources"].append(file_resource)
        
        # Add link resources
        if links:
            for link in links:
                link_resource = {
                    "title": title or f"Ссылка по {query}",
                    "type": "link",
                    "link": link
                }
                entry["resources"].append(link_resource)
        
        return entry
    
    def load_from_csv_simple(self, file_path: str) -> List[Dict]:
        """Load FAQ entries from CSV file using built-in csv module"""
        self.logger.info(f"📊 Loading from CSV: {file_path}")
        entries = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    if not row.get('query'):
                        continue
                    
                    query = row['query'].strip()
                    variations = []
                    files = []
                    links = []
                    
                    # Parse variations (semicolon separated)
                    if row.get('variations'):
                        variations = [v.strip() for v in row['variations'].split(';') if v.strip()]
                    
                    # Parse file paths (semicolon separated)
                    if row.get('files'):
                        file_paths = [f.strip() for f in row['files'].split(';') if f.strip()]
                        files = self.copy_files_to_directory(file_paths)
                    
                    # Parse links (semicolon separated)
                    if row.get('links'):
                        links = [l.strip() for l in row['links'].split(';') if l.strip()]
                    
                    response = row.get('response', 'По вашему запросу есть следующее:').strip()
                    additional_text = row.get('additional_text', '').strip() if row.get('additional_text') else None
                    title = row.get('title', '').strip() if row.get('title') else None
                    
                    entry = self.create_faq_entry(
                        query=query,
                        variations=variations,
                        response=response,
                        files=files,
                        links=links,
                        additional_text=additional_text,
                        title=title
                    )
                    entries.append(entry)
                    
        except Exception as e:
            self.logger.error(f"Error loading CSV: {e}")
            raise
        
        self.logger.info(f"✅ Loaded {len(entries)} entries from CSV")
        return entries
    
    def load_from_json(self, file_path: str) -> List[Dict]:
        """Load FAQ entries from JSON file"""
        self.logger.info(f"📄 Loading from JSON: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                entries = data
            elif isinstance(data, dict) and 'entries' in data:
                entries = data['entries']
            else:
                raise ValueError("JSON should contain a list of entries or an object with 'entries' key")
            
            # Copy referenced files
            for entry in entries:
                if 'resources' in entry:
                    for resource in entry['resources']:
                        if resource.get('type') == 'file' and 'files' in resource:
                            new_files = []
                            for file_path in resource['files']:
                                if os.path.exists(file_path):
                                    copied = self.copy_files_to_directory([file_path])
                                    new_files.extend(copied)
                                else:
                                    # File path is already relative to files directory
                                    new_files.append(file_path)
                            resource['files'] = new_files
            
        except Exception as e:
            self.logger.error(f"Error loading JSON: {e}")
            raise
        
        self.logger.info(f"✅ Loaded {len(entries)} entries from JSON")
        return entries
    
    def load_from_folder(self, folder_path: str, group_by_extension: bool = True) -> List[Dict]:
        """Auto-generate FAQ entries from folder structure"""
        self.logger.info(f"📁 Loading from folder: {folder_path}")
        entries = []
        
        try:
            folder = Path(folder_path)
            
            if group_by_extension:
                # Group files by extension
                file_groups = {}
                for file_path in folder.rglob('*'):
                    if file_path.is_file():
                        ext = file_path.suffix.lower()
                        if ext not in file_groups:
                            file_groups[ext] = []
                        file_groups[ext].append(str(file_path))
                
                for ext, files in file_groups.items():
                    if not files:
                        continue
                    
                    copied_files = self.copy_files_to_directory(files)
                    
                    query = f"Файлы {ext.upper()}" if ext else "Файлы без расширения"
                    title = f"Материалы {ext.upper()}" if ext else "Различные материалы"
                    
                    entry = self.create_faq_entry(
                        query=query,
                        variations=[f"документы {ext}", f"материалы {ext}"] if ext else [],
                        files=copied_files,
                        title=title
                    )
                    entries.append(entry)
            else:
                # Individual file entries
                for file_path in folder.rglob('*'):
                    if file_path.is_file():
                        copied_files = self.copy_files_to_directory([str(file_path)])
                        
                        if copied_files:
                            file_name = file_path.stem
                            query = file_name.replace('_', ' ').replace('-', ' ')
                            
                            entry = self.create_faq_entry(
                                query=query,
                                variations=[file_name],
                                files=copied_files,
                                title=f"Документ: {file_name}"
                            )
                            entries.append(entry)
        
        except Exception as e:
            self.logger.error(f"Error loading from folder: {e}")
            raise
        
        self.logger.info(f"✅ Generated {len(entries)} entries from folder")
        return entries
    
    def load_from_txt_list(self, file_path: str, separator: str = '|') -> List[Dict]:
        """Load FAQ entries from simple text file list"""
        self.logger.info(f"📄 Loading from text list: {file_path}")
        entries = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):  # Skip empty lines and comments
                        continue
                    
                    parts = [p.strip() for p in line.split(separator)]
                    if len(parts) < 1:
                        continue
                    
                    query = parts[0]
                    files = []
                    links = []
                    additional_text = None
                    
                    if len(parts) > 1 and parts[1]:  # Files
                        file_paths = [f.strip() for f in parts[1].split(';') if f.strip()]
                        files = self.copy_files_to_directory(file_paths)
                    
                    if len(parts) > 2 and parts[2]:  # Links
                        links = [l.strip() for l in parts[2].split(';') if l.strip()]
                    
                    if len(parts) > 3 and parts[3]:  # Additional text
                        additional_text = parts[3]
                    
                    entry = self.create_faq_entry(
                        query=query,
                        files=files,
                        links=links,
                        additional_text=additional_text
                    )
                    entries.append(entry)
                    
        except Exception as e:
            self.logger.error(f"Error loading text list: {e}")
            raise
        
        self.logger.info(f"✅ Loaded {len(entries)} entries from text list")
        return entries
    
    def bulk_import(
        self, 
        source: str, 
        format_type: str, 
        merge: bool = True
    ) -> Tuple[int, int]:
        """Bulk import FAQ entries from various sources"""
        self.logger.info(f"🚀 Starting bulk import from {source}")
        
        # Create backup
        self.create_backup()
        
        # Load existing FAQ if merging
        existing_faq = self.load_existing_faq() if merge else []
        
        # Load new entries based on format
        if format_type == 'csv':
            new_entries = self.load_from_csv_simple(source)
        elif format_type == 'json':
            new_entries = self.load_from_json(source)
        elif format_type == 'folder':
            new_entries = self.load_from_folder(source)
        elif format_type == 'txt':
            new_entries = self.load_from_txt_list(source)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
        
        # Merge or replace
        if merge:
            all_entries = existing_faq + new_entries
        else:
            all_entries = new_entries
        
        # Save to file
        self.save_faq(all_entries)
        
        self.logger.info(f"🎉 Import completed!")
        self.logger.info(f"📊 Added: {len(new_entries)} new entries")
        self.logger.info(f"📚 Total: {len(all_entries)} entries")
        
        return len(new_entries), len(all_entries)
    
    def create_template_files(self):
        """Create template files for easy bulk loading"""
        templates_dir = "templates"
        os.makedirs(templates_dir, exist_ok=True)
        
        # CSV template
        csv_template = os.path.join(templates_dir, "simple_faq_template.csv")
        with open(csv_template, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['query', 'variations', 'response', 'files', 'links', 'additional_text', 'title'])
            writer.writerow([
                'Пример вопроса',
                'альтернатива 1;альтернатива 2',
                'По вашему запросу есть следующее:',
                'C:\\path\\to\\file1.pdf;C:\\path\\to\\file2.docx',
                'https://example.com;https://another-link.com',
                'Дополнительная информация',
                'Название ресурса'
            ])
        
        # Text template
        txt_template = os.path.join(templates_dir, "simple_faq_template.txt")
        with open(txt_template, 'w', encoding='utf-8') as f:
            f.write("# Simple FAQ Template - format: query|files|links|additional_text\n")
            f.write("# Use semicolon (;) to separate multiple files or links\n")
            f.write("Пример вопроса|C:\\path\\to\\file.pdf|https://example.com|Дополнительная информация\n")
            f.write("Другой вопрос|C:\\path\\to\\file1.pdf;C:\\path\\to\\file2.docx||Только файлы\n")
            f.write("Ссылочный вопрос||https://example.com|Только ссылка\n")
        
        self.logger.info(f"📋 Simple templates created in {templates_dir}/")
        self.logger.info(f"   - CSV: {csv_template}")
        self.logger.info(f"   - TXT: {txt_template}")


def main():
    """Command line interface for simple bulk loading"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple Bulk FAQ Loader (no external dependencies)")
    parser.add_argument("source", nargs='?', help="Source file or folder path")
    parser.add_argument("format", nargs='?', choices=['csv', 'json', 'folder', 'txt'], 
                       help="Source format type")
    parser.add_argument("--merge", action="store_true", default=True,
                       help="Merge with existing FAQ (default: True)")
    parser.add_argument("--replace", action="store_true", 
                       help="Replace existing FAQ instead of merging")
    parser.add_argument("--templates", action="store_true",
                       help="Create template files")
    
    args = parser.parse_args()
    
    loader = SimpleBulkFAQLoader()
    
    if args.templates:
        loader.create_template_files()
        return
    
    if not args.source or not args.format:
        print("📋 Simple Bulk FAQ Loader")
        print("Usage examples:")
        print("  python simple_bulk_loader.py data.csv csv")
        print("  python simple_bulk_loader.py data.json json")
        print("  python simple_bulk_loader.py folder_path folder")
        print("  python simple_bulk_loader.py --templates")
        return
    
    merge = not args.replace if args.replace else args.merge
    
    try:
        new_count, total_count = loader.bulk_import(
            source=args.source,
            format_type=args.format,
            merge=merge
        )
        print(f"✅ Success! Added {new_count} new entries. Total: {total_count}")
        print("💡 Restart bot to see changes: restart_bot.bat")
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())