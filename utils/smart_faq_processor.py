#!/usr/bin/env python3
"""
Smart FAQ Processor - Intelligent validation and merging algorithms
Features: Duplicate detection, content validation, smart merging
"""

import json
import os
import re
from typing import Dict, List, Any, Tuple, Set, Optional
from pathlib import Path
from datetime import datetime
import difflib
from collections import defaultdict
import logging

class FAQValidator:
    """Intelligent FAQ content validation"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.suggestions = []
    
    def validate_entry(self, entry: Dict[str, Any], entry_id: int = None) -> Dict[str, List[str]]:
        """Validate a single FAQ entry"""
        self.errors.clear()
        self.warnings.clear()
        self.suggestions.clear()
        
        entry_ref = f"Entry {entry_id}" if entry_id else "Entry"
        
        # Required fields validation
        if not entry.get('query'):
            self.errors.append(f"{entry_ref}: Missing required 'query' field")
        elif not isinstance(entry['query'], str) or not entry['query'].strip():
            self.errors.append(f"{entry_ref}: Query must be a non-empty string")
        
        # Query quality checks
        query = entry.get('query', '')
        if len(query) < 3:
            self.warnings.append(f"{entry_ref}: Query is very short (< 3 characters)")
        elif len(query) > 200:
            self.warnings.append(f"{entry_ref}: Query is very long (> 200 characters)")
        
        # Check for placeholder text
        if query.lower() in ['example', 'пример', 'test', 'тест']:
            self.warnings.append(f"{entry_ref}: Query appears to be placeholder text")
        
        # Variations validation
        variations = entry.get('variations', [])
        if variations and not isinstance(variations, list):
            self.errors.append(f"{entry_ref}: Variations must be a list")
        elif variations:
            for i, var in enumerate(variations):
                if not isinstance(var, str) or not var.strip():
                    self.warnings.append(f"{entry_ref}: Variation {i+1} is empty or invalid")
        
        # Resources validation
        resources = entry.get('resources', [])
        if not isinstance(resources, list):
            self.errors.append(f"{entry_ref}: Resources must be a list")
        elif not resources:
            self.warnings.append(f"{entry_ref}: No resources provided - entry may be incomplete")
        else:
            self._validate_resources(resources, entry_ref)
        
        return {
            'errors': self.errors.copy(),
            'warnings': self.warnings.copy(),
            'suggestions': self.suggestions.copy()
        }
    
    def _validate_resources(self, resources: List[Dict], entry_ref: str):
        """Validate resources within an entry"""
        for i, resource in enumerate(resources):
            res_ref = f"{entry_ref}, Resource {i+1}"
            
            # Resource type validation
            res_type = resource.get('type')
            if not res_type:
                self.errors.append(f"{res_ref}: Missing 'type' field")
                continue
            elif res_type not in ['file', 'link']:
                self.errors.append(f"{res_ref}: Invalid type '{res_type}' (must be 'file' or 'link')")
            
            # Type-specific validation
            if res_type == 'file':
                files = resource.get('files', [])
                if not files:
                    self.warnings.append(f"{res_ref}: No files specified")
                elif not isinstance(files, list):
                    self.errors.append(f"{res_ref}: Files must be a list")
                else:
                    for j, file_path in enumerate(files):
                        if not isinstance(file_path, str) or not file_path.strip():
                            self.warnings.append(f"{res_ref}, File {j+1}: Empty file path")
            
            elif res_type == 'link':
                link = resource.get('link', '')
                if not link:
                    self.errors.append(f"{res_ref}: Missing 'link' field")
                elif not isinstance(link, str):
                    self.errors.append(f"{res_ref}: Link must be a string")
                elif not self._is_valid_url(link):
                    self.warnings.append(f"{res_ref}: Link may not be a valid URL")
    
    def _is_valid_url(self, url: str) -> bool:
        """Basic URL validation"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None

class SmartFAQMerger:
    """Intelligent FAQ merging with duplicate detection"""
    
    def __init__(self, similarity_threshold: float = 0.8):
        self.similarity_threshold = similarity_threshold
        self.logger = logging.getLogger(__name__)
    
    def merge_faqs(self, existing_faq: List[Dict], new_faq: List[Dict], 
                  strategy: str = "smart") -> Tuple[List[Dict], Dict[str, Any]]:
        """
        Merge FAQ lists using intelligent algorithms
        
        Args:
            existing_faq: Current FAQ entries
            new_faq: New FAQ entries to merge
            strategy: Merging strategy ('smart', 'append', 'replace')
        
        Returns:
            Tuple of (merged_faq, merge_report)
        """
        if strategy == "replace":
            return new_faq, {"strategy": "replace", "total": len(new_faq)}
        elif strategy == "append":
            return existing_faq + new_faq, {
                "strategy": "append", 
                "added": len(new_faq),
                "total": len(existing_faq) + len(new_faq)
            }
        
        # Smart merging
        return self._smart_merge(existing_faq, new_faq)
    
    def _smart_merge(self, existing_faq: List[Dict], new_faq: List[Dict]) -> Tuple[List[Dict], Dict]:
        """Perform intelligent merging with duplicate detection"""
        merged_faq = existing_faq.copy()
        merge_report = {
            "strategy": "smart",
            "added": 0,
            "updated": 0,
            "duplicates_found": 0,
            "conflicts": []
        }
        
        for new_entry in new_faq:
            match_result = self._find_similar_entries(new_entry, existing_faq)
            
            if not match_result['matches']:
                # No similar entries found - add as new
                merged_faq.append(new_entry)
                merge_report["added"] += 1
            else:
                # Found similar entries - handle conflicts
                best_match = match_result['matches'][0]
                
                if best_match['similarity'] > 0.95:
                    # Very high similarity - likely duplicate
                    merge_report["duplicates_found"] += 1
                    
                    # Try to merge resources
                    merged_entry = self._merge_entries(
                        merged_faq[best_match['index']], 
                        new_entry
                    )
                    merged_faq[best_match['index']] = merged_entry
                    merge_report["updated"] += 1
                    
                elif best_match['similarity'] > self.similarity_threshold:
                    # Potential conflict - record for user review
                    merge_report["conflicts"].append({
                        "existing_query": merged_faq[best_match['index']]['query'],
                        "new_query": new_entry['query'],
                        "similarity": best_match['similarity'],
                        "action": "added_as_new"  # Default action
                    })
                    merged_faq.append(new_entry)
                    merge_report["added"] += 1
                else:
                    # Low similarity - add as new entry
                    merged_faq.append(new_entry)
                    merge_report["added"] += 1
        
        merge_report["total"] = len(merged_faq)
        return merged_faq, merge_report
    
    def _find_similar_entries(self, entry: Dict, faq_list: List[Dict]) -> Dict:
        """Find entries similar to the given entry"""
        query = entry.get('query', '').lower().strip()
        variations = [v.lower().strip() for v in entry.get('variations', [])]
        all_queries = [query] + variations
        
        matches = []
        
        for i, existing_entry in enumerate(faq_list):
            existing_query = existing_entry.get('query', '').lower().strip()
            existing_variations = [v.lower().strip() for v in existing_entry.get('variations', [])]
            existing_queries = [existing_query] + existing_variations
            
            max_similarity = 0
            
            # Compare all combinations
            for new_q in all_queries:
                for existing_q in existing_queries:
                    if new_q and existing_q:
                        similarity = difflib.SequenceMatcher(None, new_q, existing_q).ratio()
                        max_similarity = max(max_similarity, similarity)
            
            if max_similarity > 0.5:  # Minimum threshold for consideration
                matches.append({
                    'index': i,
                    'similarity': max_similarity,
                    'entry': existing_entry
                })
        
        # Sort by similarity (highest first)
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        
        return {'matches': matches}
    
    def _merge_entries(self, existing_entry: Dict, new_entry: Dict) -> Dict:
        """Merge two similar entries intelligently"""
        merged = existing_entry.copy()
        
        # Merge variations
        existing_variations = set(existing_entry.get('variations', []))
        new_variations = set(new_entry.get('variations', []))
        all_variations = existing_variations | new_variations
        
        # Don't include the main query in variations
        main_query = existing_entry.get('query', '').lower()
        all_variations.discard(main_query)
        
        merged['variations'] = list(all_variations)
        
        # Merge resources
        existing_resources = existing_entry.get('resources', [])
        new_resources = new_entry.get('resources', [])
        
        # Group resources by type
        resource_map = defaultdict(list)
        
        for resource in existing_resources + new_resources:
            res_type = resource.get('type', 'unknown')
            resource_map[res_type].append(resource)
        
        # Merge file resources
        merged_resources = []
        
        for res_type, resources in resource_map.items():
            if res_type == 'file':
                # Combine all files
                all_files = []
                titles = []
                additional_texts = []
                
                for resource in resources:
                    all_files.extend(resource.get('files', []))
                    if resource.get('title'):
                        titles.append(resource['title'])
                    if resource.get('additional_text'):
                        additional_texts.append(resource['additional_text'])
                
                # Remove duplicates while preserving order
                unique_files = []
                seen_files = set()
                for file_path in all_files:
                    if file_path not in seen_files:
                        unique_files.append(file_path)
                        seen_files.add(file_path)
                
                if unique_files:
                    merged_resource = {
                        'type': 'file',
                        'files': unique_files
                    }
                    
                    if titles:
                        merged_resource['title'] = titles[0]  # Use first title
                    
                    if additional_texts:
                        merged_resource['additional_text'] = ' | '.join(set(additional_texts))
                    
                    merged_resources.append(merged_resource)
            
            elif res_type == 'link':
                # Keep unique links
                unique_links = []
                seen_links = set()
                
                for resource in resources:
                    link = resource.get('link', '')
                    if link and link not in seen_links:
                        unique_links.append(resource)
                        seen_links.add(link)
                
                merged_resources.extend(unique_links)
            else:
                # Other resource types - keep all
                merged_resources.extend(resources)
        
        merged['resources'] = merged_resources
        
        return merged

class FAQProcessor:
    """Main processor that coordinates validation and merging"""
    
    def __init__(self):
        self.validator = FAQValidator()
        self.merger = SmartFAQMerger()
        self.logger = logging.getLogger(__name__)
    
    def process_faq_data(self, new_data: List[Dict], existing_data: List[Dict] = None,
                        validate: bool = True, merge_strategy: str = "smart") -> Dict[str, Any]:
        """
        Process FAQ data with validation and intelligent merging
        
        Returns:
            Dictionary with processed data and reports
        """
        result = {
            'processed_data': [],
            'validation_report': {},
            'merge_report': {},
            'success': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Validation phase
            if validate:
                validation_report = self._validate_faq_list(new_data)
                result['validation_report'] = validation_report
                
                if validation_report['critical_errors'] > 0:
                    result['success'] = False
                    result['errors'] = validation_report['error_details']
                    return result
                
                result['warnings'] = validation_report['warning_details']
            
            # Merging phase
            if existing_data is not None:
                merged_data, merge_report = self.merger.merge_faqs(
                    existing_data, new_data, merge_strategy
                )
                result['processed_data'] = merged_data
                result['merge_report'] = merge_report
            else:
                result['processed_data'] = new_data
                result['merge_report'] = {
                    'strategy': 'new',
                    'total': len(new_data),
                    'added': len(new_data)
                }
            
            return result
            
        except Exception as e:
            result['success'] = False
            result['errors'].append(f"Processing error: {str(e)}")
            self.logger.error(f"FAQ processing error: {e}")
            return result
    
    def _validate_faq_list(self, faq_data: List[Dict]) -> Dict[str, Any]:
        """Validate entire FAQ list"""
        report = {
            'total_entries': len(faq_data),
            'valid_entries': 0,
            'entries_with_warnings': 0,
            'entries_with_errors': 0,
            'critical_errors': 0,
            'error_details': [],
            'warning_details': [],
            'entry_reports': []
        }
        
        for i, entry in enumerate(faq_data):
            entry_validation = self.validator.validate_entry(entry, i + 1)
            
            if entry_validation['errors']:
                report['entries_with_errors'] += 1
                report['critical_errors'] += len(entry_validation['errors'])
                report['error_details'].extend(entry_validation['errors'])
            else:
                report['valid_entries'] += 1
            
            if entry_validation['warnings']:
                report['entries_with_warnings'] += 1
                report['warning_details'].extend(entry_validation['warnings'])
            
            report['entry_reports'].append({
                'entry_id': i + 1,
                'query': entry.get('query', 'Unknown'),
                'errors': len(entry_validation['errors']),
                'warnings': len(entry_validation['warnings']),
                'details': entry_validation
            })
        
        return report

def main():
    """CLI interface for testing the FAQ processor"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Smart FAQ Processor")
    parser.add_argument("input_file", help="Input FAQ JSON file")
    parser.add_argument("--existing", help="Existing FAQ file to merge with")
    parser.add_argument("--output", help="Output file (default: processed_faq.json)")
    parser.add_argument("--strategy", choices=['smart', 'append', 'replace'], 
                       default='smart', help="Merge strategy")
    parser.add_argument("--validate", action='store_true', default=True,
                       help="Enable validation")
    
    args = parser.parse_args()
    
    # Load input data
    with open(args.input_file, 'r', encoding='utf-8') as f:
        new_data = json.load(f)
    
    existing_data = None
    if args.existing:
        with open(args.existing, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    
    # Process
    processor = FAQProcessor()
    result = processor.process_faq_data(
        new_data, existing_data, args.validate, args.strategy
    )
    
    # Output results
    output_file = args.output or "processed_faq.json"
    
    if result['success']:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result['processed_data'], f, ensure_ascii=False, indent=2)
        
        print(f"✅ Processing successful! Output: {output_file}")
        
        if result['merge_report']:
            mr = result['merge_report']
            print(f"📊 Merge Report: {mr.get('added', 0)} added, {mr.get('updated', 0)} updated")
        
        if result['warnings']:
            print(f"⚠️ {len(result['warnings'])} warnings found")
    else:
        print("❌ Processing failed:")
        for error in result['errors']:
            print(f"   - {error}")

if __name__ == "__main__":
    main()