#!/usr/bin/env python3
"""
Comprehensive tests for the Modern FAQ GUI and Optimized Processor
Tests functionality, performance, and user experience
"""

import os
import sys
import unittest
import tempfile
import json
import csv
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock
import threading
import time

# Add utils to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

try:
    from optimized_processor import OptimizedFAQManager, OptimizedFileProcessor, FAQEntry, SmartFAQMerger
    from modern_faq_gui import ModernFAQGUI, ProcessingJob
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all required modules are in the utils directory")
    sys.exit(1)

class TestOptimizedProcessor(unittest.TestCase):
    """Test the optimized processing algorithms"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.processor = OptimizedFileProcessor()
        
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_csv_detection(self):
        """Test CSV format detection"""
        # Create test CSV files with different delimiters
        test_files = [
            ('comma.csv', 'query,variations,response\n"Test question","var1;var2","Test response"'),
            ('semicolon.csv', 'query;variations;response\n"Test question";"var1;var2";"Test response"'),
            ('tab.csv', 'query\tvariations\tresponse\n"Test question"\t"var1;var2"\t"Test response"')
        ]
        
        for filename, content in test_files:
            file_path = os.path.join(self.temp_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Test detection
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                delimiter, encoding = loop.run_until_complete(
                    self.processor._detect_csv_format(Path(file_path))
                )
                
                if 'comma' in filename:
                    self.assertEqual(delimiter, ',')
                elif 'semicolon' in filename:
                    self.assertEqual(delimiter, ';')
                elif 'tab' in filename:
                    self.assertEqual(delimiter, '\t')
                
                self.assertEqual(encoding, 'utf-8')
            finally:
                loop.close()
    
    def test_csv_processing(self):
        """Test CSV file processing"""
        # Create test CSV
        csv_file = os.path.join(self.temp_dir, 'test.csv')
        with open(csv_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['query', 'variations', 'response', 'files'])
            writer.writerow(['Как подать заявление?', 'подача заявления;подать документы', 'Инструкция по подаче', 'file1.pdf'])
            writer.writerow(['Какие документы нужны?', 'необходимые документы;список документов', 'Список документов', 'file2.pdf;file3.docx'])
        
        # Process file
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            entries = loop.run_until_complete(self.processor.process_file_async(csv_file))
            
            self.assertEqual(len(entries), 2)
            
            # Check first entry
            entry1 = entries[0]
            self.assertEqual(entry1.query, 'Как подать заявление?')
            self.assertIn('подача заявления', entry1.variations)
            self.assertIn('подать документы', entry1.variations)
            self.assertEqual(entry1.response, 'Инструкция по подаче')
            
            # Check second entry  
            entry2 = entries[1]
            self.assertEqual(entry2.query, 'Какие документы нужны?')
            self.assertIn('необходимые документы', entry2.variations)
            self.assertIn('список документов', entry2.variations)
            
        finally:
            loop.close()
    
    def test_json_processing(self):
        """Test JSON file processing"""
        # Create test JSON
        json_file = os.path.join(self.temp_dir, 'test.json')
        test_data = [
            {
                "query": "Тестовый вопрос 1",
                "variations": ["вариант 1", "вариант 2"],
                "response": "Тестовый ответ 1",
                "resources": [
                    {
                        "type": "file",
                        "title": "Материалы",
                        "files": ["test1.pdf"]
                    }
                ]
            },
            {
                "query": "Тестовый вопрос 2",
                "variations": [],
                "response": "Тестовый ответ 2",
                "resources": []
            }
        ]
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        # Process file
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            entries = loop.run_until_complete(self.processor.process_file_async(json_file))
            
            self.assertEqual(len(entries), 2)
            self.assertEqual(entries[0].query, "Тестовый вопрос 1")
            self.assertEqual(len(entries[0].variations), 2)
            self.assertEqual(len(entries[0].resources), 1)
            
        finally:
            loop.close()

class TestSmartMerger(unittest.TestCase):
    """Test the smart FAQ merging algorithms"""
    
    def setUp(self):
        """Set up test environment"""
        self.merger = SmartFAQMerger(similarity_threshold=0.8)
    
    def test_exact_duplicate_detection(self):
        """Test detection of exact duplicates"""
        entry1 = FAQEntry(
            query="Как подать заявление?",
            variations=["подача заявления"],
            response="Инструкция по подаче",
            resources=[]
        )
        
        entry2 = FAQEntry(
            query="Как подать заявление?",
            variations=["подача заявления"],
            response="Инструкция по подаче",
            resources=[]
        )
        
        # Ensure same hash for identical content
        self.assertEqual(entry1.metadata['hash'], entry2.metadata['hash'])
        
        # Test merging
        merged, stats = self.merger.merge_entries([entry1], [entry2])
        
        self.assertEqual(len(merged), 1)  # Should not add duplicate
        self.assertEqual(stats['duplicates'], 1)
        self.assertEqual(stats['added'], 0)
    
    def test_similar_entry_merging(self):
        """Test merging of similar entries"""
        entry1 = FAQEntry(
            query="Как подать заявление?",
            variations=["подача заявления"],
            response="Краткий ответ",
            resources=[]
        )
        
        entry2 = FAQEntry(
            query="Как подавать заявление в организацию?",  # Similar but longer
            variations=["подача документов"],
            response="Подробный ответ с инструкциями",
            resources=[{"type": "file", "files": ["instruction.pdf"]}]
        )
        
        # Different hashes but similar content
        self.assertNotEqual(entry1.metadata['hash'], entry2.metadata['hash'])
        
        # Test merging
        merged, stats = self.merger.merge_entries([entry1], [entry2])
        
        self.assertEqual(len(merged), 1)  # Should merge into one
        self.assertEqual(stats['merged'], 1)
        
        # Check merged result
        merged_entry = merged[0]
        self.assertIn("организацию", merged_entry.query)  # Should use longer query
        self.assertIn("подача заявления", merged_entry.variations)
        self.assertIn("подача документов", merged_entry.variations)
        self.assertEqual(len(merged_entry.resources), 1)  # Should include resources
    
    def test_different_entries(self):
        """Test handling of completely different entries"""
        entry1 = FAQEntry(
            query="Как подать заявление?",
            variations=[],
            response="Ответ 1",
            resources=[]
        )
        
        entry2 = FAQEntry(
            query="Какие документы нужны для получения справки?",
            variations=[],
            response="Ответ 2",
            resources=[]
        )
        
        # Test merging
        merged, stats = self.merger.merge_entries([entry1], [entry2])
        
        self.assertEqual(len(merged), 2)  # Should keep both
        self.assertEqual(stats['added'], 1)
        self.assertEqual(stats['merged'], 0)

class TestFAQManager(unittest.TestCase):
    """Test the FAQ Manager with async operations"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.faq_file = os.path.join(self.temp_dir, 'faq.json')
        self.backup_dir = os.path.join(self.temp_dir, 'backups')
        self.manager = OptimizedFAQManager(self.faq_file, self.backup_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_bulk_import_performance(self):
        """Test bulk import performance with multiple files"""
        # Create test files
        test_files = []
        
        for i in range(3):
            csv_file = os.path.join(self.temp_dir, f'test_{i}.csv')
            with open(csv_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['query', 'response'])
                for j in range(10):
                    writer.writerow([f'Вопрос {i}-{j}', f'Ответ {i}-{j}'])
            test_files.append(csv_file)
        
        # Test bulk import
        start_time = time.time()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            new_count, total_count = loop.run_until_complete(
                self.manager.bulk_import_async(test_files, merge=False)
            )
            
            processing_time = time.time() - start_time
            
            self.assertEqual(new_count, 30)  # 3 files × 10 entries
            self.assertEqual(total_count, 30)
            self.assertLess(processing_time, 5)  # Should complete in under 5 seconds
            
            # Verify FAQ file was created
            self.assertTrue(os.path.exists(self.faq_file))
            
            # Verify content
            with open(self.faq_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.assertEqual(len(data), 30)
                
        finally:
            loop.close()

class TestModernGUI(unittest.TestCase):
    """Test the Modern GUI interface"""
    
    def setUp(self):
        """Set up test environment"""
        # Skip GUI tests if no display available
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()  # Hide window
            self.root = root
            self.gui_available = True
        except Exception:
            self.gui_available = False
            self.skipTest("GUI not available in test environment")
    
    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self, 'root'):
            self.root.destroy()
    
    def test_gui_initialization(self):
        """Test GUI initialization"""
        if not self.gui_available:
            return
            
        try:
            app = ModernFAQGUI(self.root)
            
            # Check that main components are created
            self.assertIsNotNone(app.loader)
            self.assertIsNotNone(app.optimized_manager)
            self.assertIsNone(app.current_job)
            self.assertFalse(app.is_processing)
            
        except Exception as e:
            self.fail(f"GUI initialization failed: {e}")
    
    def test_format_detection(self):
        """Test automatic format detection"""
        if not self.gui_available:
            return
            
        app = ModernFAQGUI(self.root)
        
        # Test different file extensions
        test_cases = [
            ('test.csv', 'csv'),
            ('test.xlsx', 'excel'),
            ('test.json', 'json'),
            ('test.txt', 'txt'),
            ('/path/to/folder', 'folder'),
            ('unknown.xyz', 'csv')  # Default fallback
        ]
        
        for path, expected_format in test_cases:
            with patch('os.path.isdir') as mock_isdir:
                mock_isdir.return_value = (expected_format == 'folder')
                
                detected_format = app.detect_format(path)
                self.assertEqual(detected_format, expected_format)

class TestPerformanceBenchmarks(unittest.TestCase):
    """Performance benchmarks and stress tests"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.processor = OptimizedFileProcessor()
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_large_csv_processing(self):
        """Test processing of large CSV files"""
        # Create large CSV file
        csv_file = os.path.join(self.temp_dir, 'large_test.csv')
        with open(csv_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['query', 'variations', 'response'])
            
            # Write 1000 entries
            for i in range(1000):
                writer.writerow([
                    f'Тестовый вопрос номер {i}',
                    f'вариант {i};альтернатива {i}',
                    f'Подробный ответ на вопрос номер {i} с дополнительной информацией'
                ])
        
        # Test processing time
        start_time = time.time()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            entries = loop.run_until_complete(self.processor.process_file_async(csv_file))
            
            processing_time = time.time() - start_time
            
            self.assertEqual(len(entries), 1000)
            self.assertLess(processing_time, 10)  # Should complete in under 10 seconds
            
            # Verify entry quality
            sample_entry = entries[0]
            self.assertTrue(sample_entry.query.startswith('Тестовый вопрос'))
            self.assertEqual(len(sample_entry.variations), 2)
            
        finally:
            loop.close()
    
    def test_memory_efficiency(self):
        """Test memory usage during processing"""
        import psutil
        import gc
        
        process = psutil.Process()
        
        # Get baseline memory
        gc.collect()
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create and process multiple files
        csv_files = []
        for i in range(5):
            csv_file = os.path.join(self.temp_dir, f'memory_test_{i}.csv')
            with open(csv_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['query', 'response'])
                for j in range(200):
                    writer.writerow([f'Вопрос {i}-{j}', f'Ответ {i}-{j}'])
            csv_files.append(csv_file)
        
        # Process files
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            for csv_file in csv_files:
                entries = loop.run_until_complete(self.processor.process_file_async(csv_file))
                self.assertEqual(len(entries), 200)
            
            # Check memory usage
            gc.collect()
            peak_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = peak_memory - baseline_memory
            
            # Memory increase should be reasonable (less than 100MB for this test)
            self.assertLess(memory_increase, 100)
            
        finally:
            loop.close()

def run_performance_test():
    """Run a quick performance demonstration"""
    print("🚀 Running Performance Tests...")
    print("=" * 50)
    
    # Create test environment
    temp_dir = tempfile.mkdtemp()
    processor = OptimizedFileProcessor()
    
    try:
        # Create test CSV with 500 entries
        csv_file = os.path.join(temp_dir, 'performance_test.csv')
        print(f"📁 Creating test file with 500 entries...")
        
        with open(csv_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['query', 'variations', 'response', 'files'])
            
            for i in range(500):
                writer.writerow([
                    f'Как решить проблему номер {i}?',
                    f'проблема {i};вопрос {i};помощь {i}',
                    f'Для решения проблемы номер {i} следуйте инструкциям...',
                    f'solution_{i}.pdf;guide_{i}.docx'
                ])
        
        file_size = os.path.getsize(csv_file) / 1024  # KB
        print(f"📊 Test file size: {file_size:.1f} KB")
        
        # Test processing
        print("⚡ Processing with optimized algorithms...")
        start_time = time.time()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            entries = loop.run_until_complete(processor.process_file_async(csv_file))
            processing_time = time.time() - start_time
            
            print(f"✅ Processed {len(entries)} entries in {processing_time:.2f} seconds")
            print(f"⚡ Performance: {len(entries)/processing_time:.0f} entries/second")
            print(f"💾 Memory efficient: {file_size/processing_time:.1f} KB/second")
            
            # Validate quality
            sample = entries[0]
            print(f"🔍 Sample entry:")
            print(f"   Query: {sample.query}")
            print(f"   Variations: {len(sample.variations)} found")
            print(f"   Hash: {sample.metadata.get('hash', 'N/A')}")
            
        finally:
            loop.close()
    
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    print("=" * 50)
    print("✅ Performance test completed!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Modern FAQ GUI and Optimized Processor')
    parser.add_argument('--performance', action='store_true', help='Run performance demonstration')
    parser.add_argument('--unit-tests', action='store_true', help='Run unit tests')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    
    args = parser.parse_args()
    
    if args.performance or args.all:
        run_performance_test()
        print()
    
    if args.unit_tests or args.all:
        # Run unit tests
        print("🧪 Running Unit Tests...")
        unittest.main(argv=[''], exit=False, verbosity=2)
    
    if not any([args.performance, args.unit_tests, args.all]):
        # Default: run performance test
        run_performance_test()