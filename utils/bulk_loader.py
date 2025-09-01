#!/usr/bin/env python3
"""
Bulk FAQ Loader - Tool for quickly importing large numbers of files and instructions
Supports multiple formats and automated organization
"""

import os
import json
import shutil
import logging
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
from datetime import datetime

class BulkFAQLoader:
    def __init__(self, faq_file=None, files_dir=None, backup_dir=None):
        # Get project root directory (parent of utils)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.faq_file = faq_file or os.path.join(project_root, "data", "faq.json")
        self.files_dir = files_dir or os.path.join(project_root, "files")
        self.backup_dir = backup_dir or os.path.join(project_root, "backups")
        
        self.supported_formats = {
            'csv': self.load_from_csv,
            'excel': self.load_from_excel,
            'json': self.load_from_json,
            'folder': self.load_from_folder,
            'txt': self.load_from_txt_list
        }
        
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
    
    def load_from_csv(self, file_path: str, **kwargs) -> List[Dict]:
        """Load FAQ entries from CSV file"""
        self.logger.info(f"📊 Loading from CSV: {file_path}")
        
        required_columns = kwargs.get('required_columns', ['query'])
        delimiter = kwargs.get('delimiter', ',')
        
        entries = []
        
        try:
            df = pd.read_csv(file_path, delimiter=delimiter, encoding='utf-8')
            
            for _, row in df.iterrows():
                try:
                    query_value = row.get('query')
                    if query_value is None or str(query_value).strip() == '' or str(query_value).lower() == 'nan':
                        continue
                except (TypeError, ValueError):
                    continue
                
                query = str(query_value).strip()
                variations = []
                files = []
                links = []
                
                # Parse variations (semicolon separated)
                try:
                    variations_value = row.get('variations')
                    if 'variations' in row and variations_value is not None and str(variations_value).lower() != 'nan':
                        variations = [v.strip() for v in str(variations_value).split(';') if v.strip()]
                except (TypeError, ValueError):
                    pass
                
                # Parse file paths (semicolon separated)
                try:
                    files_value = row.get('files')
                    if 'files' in row and files_value is not None and str(files_value).lower() != 'nan':
                        file_paths = [f.strip() for f in str(files_value).split(';') if f.strip()]
                        files = self.copy_files_to_directory(file_paths)
                except (TypeError, ValueError):
                    pass
                
                # Parse links (semicolon separated)
                try:
                    links_value = row.get('links')
                    if 'links' in row and links_value is not None and str(links_value).lower() != 'nan':
                        links = [l.strip() for l in str(links_value).split(';') if l.strip()]
                except (TypeError, ValueError):
                    pass
                
                response = str(row.get('response', 'По вашему запросу есть следующее:')).strip()
                
                additional_text = None
                try:
                    additional_text_value = row.get('additional_text')
                    if 'additional_text' in row and additional_text_value is not None and str(additional_text_value).lower() != 'nan':
                        additional_text = str(additional_text_value).strip()
                except (TypeError, ValueError):
                    pass
                
                title = None
                try:
                    title_value = row.get('title')
                    if 'title' in row and title_value is not None and str(title_value).lower() != 'nan':
                        title = str(title_value).strip()
                except (TypeError, ValueError):
                    pass
                
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
    
    def load_from_excel(self, file_path: str, **kwargs) -> List[Dict]:
        """Load FAQ entries from Excel file"""
        self.logger.info(f"📊 Loading from Excel: {file_path}")
        
        sheet_name = kwargs.get('sheet_name', 0)
        entries = []
        
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            for _, row in df.iterrows():
                try:
                    query_value = row.get('query')
                    if query_value is None or str(query_value).strip() == '' or str(query_value).lower() == 'nan':
                        continue
                except (TypeError, ValueError):
                    continue
                
                query = str(query_value).strip()
                variations = []
                files = []
                links = []
                
                # Parse variations
                try:
                    variations_value = row.get('variations')
                    if 'variations' in row and variations_value is not None and str(variations_value).lower() != 'nan':
                        variations = [v.strip() for v in str(variations_value).split(';') if v.strip()]
                except (TypeError, ValueError):
                    pass
                
                # Parse file paths
                try:
                    files_value = row.get('files')
                    if 'files' in row and files_value is not None and str(files_value).lower() != 'nan':
                        file_paths = [f.strip() for f in str(files_value).split(';') if f.strip()]
                        files = self.copy_files_to_directory(file_paths)
                except (TypeError, ValueError):
                    pass
                
                # Parse links
                try:
                    links_value = row.get('links')
                    if 'links' in row and links_value is not None and str(links_value).lower() != 'nan':
                        links = [l.strip() for l in str(links_value).split(';') if l.strip()]
                except (TypeError, ValueError):
                    pass
                
                response = str(row.get('response', 'По вашему запросу есть следующее:')).strip()
                
                additional_text = None
                try:
                    additional_text_value = row.get('additional_text')
                    if 'additional_text' in row and additional_text_value is not None and str(additional_text_value).lower() != 'nan':
                        additional_text = str(additional_text_value).strip()
                except (TypeError, ValueError):
                    pass
                
                title = None
                try:
                    title_value = row.get('title')
                    if 'title' in row and title_value is not None and str(title_value).lower() != 'nan':
                        title = str(title_value).strip()
                except (TypeError, ValueError):
                    pass
                
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
            self.logger.error(f"Error loading Excel: {e}")
            raise
        
        self.logger.info(f"✅ Loaded {len(entries)} entries from Excel")
        return entries
    
    def load_from_json(self, file_path: str, **kwargs) -> List[Dict]:
        """Load FAQ entries from JSON file"""
        self.logger.info(f"📄 Loading from JSON: {file_path}")
        
        merge_mode = kwargs.get('merge_mode', False)
        
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
    
    def load_from_folder(self, folder_path: str, **kwargs) -> List[Dict]:
        """Auto-generate FAQ entries from folder structure"""
        self.logger.info(f"📁 Loading from folder: {folder_path}")
        
        pattern = kwargs.get('pattern', '*')
        auto_title = kwargs.get('auto_title', True)
        group_by_extension = kwargs.get('group_by_extension', True)
        
        entries = []
        
        try:
            folder = Path(folder_path)
            
            if group_by_extension:
                # Group files by extension
                file_groups = {}
                for file_path in folder.rglob(pattern):
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
                for file_path in folder.rglob(pattern):
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
    
    def load_from_txt_list(self, file_path: str, **kwargs) -> List[Dict]:
        """Load FAQ entries from simple text file list"""
        self.logger.info(f"📄 Loading from text list: {file_path}")
        
        separator = kwargs.get('separator', '|')  # query|files|links|additional_text
        
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
        merge: bool = True, 
        **kwargs
    ) -> Tuple[int, int]:
        """
        Bulk import FAQ entries from various sources
        
        Args:
            source: Path to source file/folder
            format_type: Type of source (csv, excel, json, folder, txt)
            merge: Whether to merge with existing FAQ or replace
            **kwargs: Additional parameters specific to format
        
        Returns:
            Tuple of (new_entries_count, total_entries_count)
        """
        self.logger.info(f"🚀 Starting bulk import from {source}")
        
        # Create backup
        self.create_backup()
        
        # Load existing FAQ if merging
        existing_faq = self.load_existing_faq() if merge else []
        
        # Load new entries based on format
        if format_type not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format_type}")
        
        new_entries = self.supported_formats[format_type](source, **kwargs)
        
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
        # Use project root templates directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        templates_dir = os.path.join(project_root, "templates")
        os.makedirs(templates_dir, exist_ok=True)
        
        # CSV template
        csv_template = os.path.join(templates_dir, "faq_template.csv")
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
        txt_template = os.path.join(templates_dir, "faq_template.txt")
        with open(txt_template, 'w', encoding='utf-8') as f:
            f.write("# FAQ Template - format: query|files|links|additional_text\n")
            f.write("# Use semicolon (;) to separate multiple files or links\n")
            f.write("Пример вопроса|C:\\path\\to\\file.pdf|https://example.com|Дополнительная информация\n")
            f.write("Другой вопрос|C:\\path\\to\\file1.pdf;C:\\path\\to\\file2.docx||Только файлы\n")
            f.write("Ссылочный вопрос||https://example.com|Только ссылка\n")
        
        # Excel template
        excel_template = os.path.join(templates_dir, "faq_template.xlsx")
        df = pd.DataFrame({
            'query': ['Пример вопроса'],
            'variations': ['альтернатива 1;альтернатива 2'],
            'response': ['По вашему запросу есть следующее:'],
            'files': ['C:\\path\\to\\file1.pdf;C:\\path\\to\\file2.docx'],
            'links': ['https://example.com'],
            'additional_text': ['Дополнительная информация'],
            'title': ['Название ресурса']
        })
        df.to_excel(excel_template, index=False)
        
        self.logger.info(f"📋 Templates created in {templates_dir}/")
        self.logger.info(f"   - CSV: {csv_template}")
        self.logger.info(f"   - TXT: {txt_template}")
        self.logger.info(f"   - Excel: {excel_template}")


def main():
    """Command line interface for bulk loading"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Bulk FAQ Loader")
    parser.add_argument("source", help="Source file or folder path")
    parser.add_argument("format", choices=['csv', 'excel', 'json', 'folder', 'txt'], 
                       help="Source format type")
    parser.add_argument("--merge", action="store_true", default=True,
                       help="Merge with existing FAQ (default: True)")
    parser.add_argument("--replace", action="store_true", 
                       help="Replace existing FAQ instead of merging")
    parser.add_argument("--templates", action="store_true",
                       help="Create template files")
    
    args = parser.parse_args()
    
    loader = BulkFAQLoader()
    
    if args.templates:
        loader.create_template_files()
        return
    
    merge = not args.replace if args.replace else args.merge
    
    try:
        new_count, total_count = loader.bulk_import(
            source=args.source,
            format_type=args.format,
            merge=merge
        )
        print(f"✅ Success! Added {new_count} new entries. Total: {total_count}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())