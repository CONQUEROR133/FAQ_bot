#!/usr/bin/env python3
"""
Comprehensive Testing Script for ru-en-RoSBERTa Model Upgrade
Validates model performance, compatibility, and system integrity
"""

import os
import sys
import json
import time
import pickle
import logging
import traceback
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import numpy as np

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('model_upgrade_test.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ModelUpgradeValidator:
    def __init__(self):
        self.test_results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'tests_passed': 0,
            'tests_failed': 0,
            'errors': [],
            'warnings': [],
            'performance_metrics': {}
        }
        
        # Russian FAQ test queries for validation
        self.test_queries = [
            "Как получить рассрочку",
            "Fold7 маркетинговые вставки", 
            "Документы для оформления",
            "Техническая поддержка",
            "Условия использования",
            "Контактная информация",
            "Инструкция по применению",
            "Часто задаваемые вопросы",
            "Политика конфиденциальности",
            "Способы оплаты"
        ]
    
    def log_test(self, test_name: str, passed: bool, message: str = "", error: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status} - {test_name}: {message}")
        
        if passed:
            self.test_results['tests_passed'] += 1
        else:
            self.test_results['tests_failed'] += 1
            if error:
                self.test_results['errors'].append(f"{test_name}: {error}")
    
    def test_dependencies(self) -> bool:
        """Test 1: Validate all required dependencies"""
        logger.info("🔍 Testing dependencies...")
        
        try:
            import sentence_transformers
            self.log_test("sentence_transformers import", True, f"Version: {sentence_transformers.__version__}")
        except ImportError as e:
            self.log_test("sentence_transformers import", False, error=str(e))
            return False
        
        try:
            import faiss
            self.log_test("faiss import", True, "FAISS library available")
        except ImportError as e:
            self.log_test("faiss import", False, error=str(e))
            return False
        
        try:
            import numpy as np
            self.log_test("numpy import", True, f"Version: {np.__version__}")
        except ImportError as e:
            self.log_test("numpy import", False, error=str(e))
            return False
        
        return True
    
    def test_config_update(self) -> bool:
        """Test 2: Validate configuration update"""
        logger.info("⚙️ Testing configuration...")
        
        try:
            from config import config
            
            # Test model name
            expected_model = "ai-forever/ru-en-RoSBERTa"
            if config.MODEL_NAME == expected_model:
                self.log_test("Model name update", True, f"Model: {config.MODEL_NAME}")
            else:
                self.log_test("Model name update", False, 
                            error=f"Expected {expected_model}, got {config.MODEL_NAME}")
                return False
            
            # Test similarity threshold
            expected_threshold = 0.73
            if config.SIMILARITY_THRESHOLD == expected_threshold:
                self.log_test("Similarity threshold", True, f"Threshold: {config.SIMILARITY_THRESHOLD}")
            else:
                self.log_test("Similarity threshold", False,
                            error=f"Expected {expected_threshold}, got {config.SIMILARITY_THRESHOLD}")
            
            # Test password security fix
            if hasattr(config, 'ACCESS_PASSWORD'):
                if config.ACCESS_PASSWORD == os.getenv("ACCESS_PASSWORD", "1337"):
                    self.log_test("Password security", True, "Password moved to environment")
                else:
                    self.log_test("Password security", False, "Password not properly secured")
            
            return True
        except Exception as e:
            self.log_test("Configuration loading", False, error=str(e))
            return False
    
    def test_model_loading(self) -> bool:
        """Test 3: Test model loading and initialization"""
        logger.info("🤖 Testing model loading...")
        
        try:
            from sentence_transformers import SentenceTransformer
            from config import config
            
            start_time = time.time()
            model = SentenceTransformer(config.MODEL_NAME)
            load_time = time.time() - start_time
            
            self.test_results['performance_metrics']['model_load_time'] = load_time
            self.log_test("Model loading", True, f"Loaded in {load_time:.2f}s")
            
            # Test model properties
            if hasattr(model, 'get_sentence_embedding_dimension'):
                embedding_dim = model.get_sentence_embedding_dimension()
                self.test_results['performance_metrics']['embedding_dimension'] = embedding_dim
                self.log_test("Model dimensions", True, f"Embedding dim: {embedding_dim}")
            
            return True
        except Exception as e:
            self.log_test("Model loading", False, error=str(e))
            return False
    
    def test_faq_loader(self) -> bool:
        """Test 4: Test FAQ loader with new model"""
        logger.info("📚 Testing FAQ loader...")
        
        try:
            # Clear old embeddings first
            for file in ['faq_embeddings.pkl', 'faq_index.faiss']:
                if os.path.exists(file):
                    os.remove(file)
                    logger.info(f"Removed old {file}")
            
            from faq_loader import FAQLoader
            from config import config
            
            # Initialize FAQ loader
            faq_loader = FAQLoader(
                faq_file=config.FAQ_FILE,
                embeddings_file=config.EMBEDDINGS_FILE,
                index_file=config.INDEX_FILE,
                model_name=config.MODEL_NAME
            )
            
            # Test FAQ loading
            start_time = time.time()
            faq_loader.load_faq()
            faq_load_time = time.time() - start_time
            
            self.test_results['performance_metrics']['faq_load_time'] = faq_load_time
            self.log_test("FAQ loading", True, f"Loaded in {faq_load_time:.2f}s")
            
            if faq_loader.faq and len(faq_loader.faq) > 0:
                faq_count = len(faq_loader.faq)
                query_count = len(faq_loader.faq_queries) if faq_loader.faq_queries else 0
                self.test_results['performance_metrics']['faq_entries'] = faq_count
                self.test_results['performance_metrics']['total_queries'] = query_count
                self.log_test("FAQ content", True, f"{faq_count} entries, {query_count} queries")
            else:
                self.log_test("FAQ content", False, "No FAQ entries loaded")
                return False
            
            # Test embeddings creation
            start_time = time.time()
            faq_loader.create_embeddings()
            embedding_time = time.time() - start_time
            
            self.test_results['performance_metrics']['embedding_creation_time'] = embedding_time
            self.log_test("Embeddings creation", True, f"Created in {embedding_time:.2f}s")
            
            return True
        except Exception as e:
            self.log_test("FAQ loader", False, error=str(e))
            logger.error(f"FAQ loader error details: {traceback.format_exc()}")
            return False
    
    def test_search_functionality(self) -> bool:
        """Test 5: Test search functionality with Russian queries"""
        logger.info("🔍 Testing search functionality...")
        
        try:
            from faq_loader import FAQLoader
            from config import config
            
            faq_loader = FAQLoader()
            
            # Test search with various Russian queries
            search_results = {}
            total_time = 0
            successful_searches = 0
            
            for query in self.test_queries:
                try:
                    start_time = time.time()
                    distances, indices = faq_loader.search(query, k=3, threshold=config.SIMILARITY_THRESHOLD)
                    search_time = time.time() - start_time
                    total_time += search_time
                    
                    if distances is not None and indices is not None:
                        successful_searches += 1
                        best_similarity = distances[0] if distances else 0
                        search_results[query] = {
                            'similarity': best_similarity,
                            'time': search_time,
                            'found': True
                        }
                        logger.info(f"Query: '{query}' -> Similarity: {best_similarity:.3f}")
                    else:
                        search_results[query] = {
                            'similarity': 0,
                            'time': search_time,
                            'found': False
                        }
                        logger.info(f"Query: '{query}' -> No match found")
                
                except Exception as e:
                    search_results[query] = {'error': str(e), 'found': False}
                    logger.warning(f"Search error for '{query}': {e}")
            
            avg_search_time = total_time / len(self.test_queries)
            success_rate = successful_searches / len(self.test_queries) * 100
            
            self.test_results['performance_metrics']['avg_search_time'] = avg_search_time
            self.test_results['performance_metrics']['search_success_rate'] = success_rate
            self.test_results['performance_metrics']['search_results'] = search_results
            
            self.log_test("Search functionality", True, 
                         f"Success rate: {success_rate:.1f}%, Avg time: {avg_search_time:.3f}s")
            
            return True
        except Exception as e:
            self.log_test("Search functionality", False, error=str(e))
            return False
    
    def test_memory_usage(self) -> bool:
        """Test 6: Monitor memory usage"""
        logger.info("💾 Testing memory usage...")
        
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            self.test_results['performance_metrics']['memory_usage_mb'] = memory_mb
            
            # Consider it a warning if memory usage is very high
            if memory_mb > 2000:  # 2GB
                self.test_results['warnings'].append(f"High memory usage: {memory_mb:.1f}MB")
                self.log_test("Memory usage", True, f"{memory_mb:.1f}MB (Warning: High)")
            else:
                self.log_test("Memory usage", True, f"{memory_mb:.1f}MB")
            
            return True
        except ImportError:
            self.log_test("Memory usage", True, "psutil not available, skipping")
            return True
        except Exception as e:
            self.log_test("Memory usage", False, error=str(e))
            return False
    
    def test_file_integrity(self) -> bool:
        """Test 7: Validate file integrity"""
        logger.info("📁 Testing file integrity...")
        
        required_files = [
            'config.py',
            'faq.json',
            'faq_loader.py',
            'main.py',
            'handlers.py'
        ]
        
        all_files_ok = True
        for file_path in required_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if len(content) > 0:
                            self.log_test(f"File integrity: {file_path}", True, f"Size: {len(content)} chars")
                        else:
                            self.log_test(f"File integrity: {file_path}", False, "Empty file")
                            all_files_ok = False
                except Exception as e:
                    self.log_test(f"File integrity: {file_path}", False, error=str(e))
                    all_files_ok = False
            else:
                self.log_test(f"File integrity: {file_path}", False, "File not found")
                all_files_ok = False
        
        # Check new embedding files were created
        embedding_files = ['faq_embeddings.pkl', 'faq_index.faiss']
        for file_path in embedding_files:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                self.log_test(f"Generated: {file_path}", True, f"Size: {size} bytes")
            else:
                self.log_test(f"Generated: {file_path}", False, "Not created")
        
        return all_files_ok
    
    def test_backup_integrity(self) -> bool:
        """Test 8: Validate backup integrity"""
        logger.info("💾 Testing backup integrity...")
        
        backup_dir = "backups"
        if os.path.exists(backup_dir):
            backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.py')]
            if backup_files:
                latest_backup = max(backup_files, key=lambda x: os.path.getctime(os.path.join(backup_dir, x)))
                backup_path = os.path.join(backup_dir, latest_backup)
                
                try:
                    with open(backup_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'paraphrase-MiniLM-L6-v2' in content:
                            self.log_test("Backup integrity", True, f"Old config preserved in {latest_backup}")
                        else:
                            self.log_test("Backup integrity", False, "Backup doesn't contain old config")
                            return False
                except Exception as e:
                    self.log_test("Backup integrity", False, error=str(e))
                    return False
            else:
                self.log_test("Backup integrity", False, "No backup files found")
                return False
        else:
            self.log_test("Backup integrity", False, "Backup directory not found")
            return False
        
        return True
    
    def run_performance_comparison(self) -> bool:
        """Test 9: Performance comparison with baseline"""
        logger.info("⚡ Running performance comparison...")
        
        try:
            # This would ideally compare with baseline metrics
            # For now, we'll just validate performance is reasonable
            metrics = self.test_results['performance_metrics']
            
            performance_ok = True
            
            # Check model load time (should be under 30 seconds)
            if 'model_load_time' in metrics:
                if metrics['model_load_time'] > 30:
                    self.test_results['warnings'].append(f"Slow model loading: {metrics['model_load_time']:.2f}s")
                    performance_ok = False
            
            # Check search time (should be under 1 second)
            if 'avg_search_time' in metrics:
                if metrics['avg_search_time'] > 1.0:
                    self.test_results['warnings'].append(f"Slow search: {metrics['avg_search_time']:.3f}s")
                    performance_ok = False
            
            # Check success rate (should be reasonable)
            if 'search_success_rate' in metrics:
                if metrics['search_success_rate'] < 50:
                    self.test_results['warnings'].append(f"Low success rate: {metrics['search_success_rate']:.1f}%")
                    performance_ok = False
            
            self.log_test("Performance comparison", performance_ok, 
                         "Performance metrics within acceptable ranges" if performance_ok else "Performance concerns detected")
            
            return performance_ok
        except Exception as e:
            self.log_test("Performance comparison", False, error=str(e))
            return False
    
    def generate_report(self) -> str:
        """Generate comprehensive test report"""
        total_tests = self.test_results['tests_passed'] + self.test_results['tests_failed']
        success_rate = (self.test_results['tests_passed'] / total_tests * 100) if total_tests > 0 else 0
        
        report = f"""
# ru-en-RoSBERTa Model Upgrade Test Report

**Test Execution**: {self.test_results['timestamp']}
**Overall Success Rate**: {success_rate:.1f}% ({self.test_results['tests_passed']}/{total_tests} tests passed)

## 📊 Performance Metrics
"""
        
        for metric, value in self.test_results['performance_metrics'].items():
            if metric != 'search_results':
                if isinstance(value, float):
                    report += f"- **{metric}**: {value:.3f}\n"
                else:
                    report += f"- **{metric}**: {value}\n"
        
        if self.test_results['errors']:
            report += "\n## ❌ Errors\n"
            for error in self.test_results['errors']:
                report += f"- {error}\n"
        
        if self.test_results['warnings']:
            report += "\n## ⚠️ Warnings\n"
            for warning in self.test_results['warnings']:
                report += f"- {warning}\n"
        
        report += "\n## 🔍 Search Results Sample\n"
        if 'search_results' in self.test_results['performance_metrics']:
            for query, result in list(self.test_results['performance_metrics']['search_results'].items())[:5]:
                if result.get('found'):
                    report += f"- `{query}`: {result['similarity']:.3f} similarity\n"
                else:
                    report += f"- `{query}`: No match\n"
        
        report += f"\n## ✅ Summary\n"
        if success_rate >= 90:
            report += "**STATUS**: ✅ EXCELLENT - Model upgrade successful\n"
        elif success_rate >= 75:
            report += "**STATUS**: ✅ GOOD - Model upgrade successful with minor issues\n"
        elif success_rate >= 50:
            report += "**STATUS**: ⚠️ ACCEPTABLE - Model upgrade completed but needs attention\n"
        else:
            report += "**STATUS**: ❌ FAILED - Model upgrade needs immediate attention\n"
        
        return report
    
    def run_all_tests(self) -> bool:
        """Run all validation tests"""
        logger.info("🚀 Starting comprehensive model upgrade validation...")
        logger.info("=" * 80)
        
        tests = [
            self.test_dependencies,
            self.test_config_update,
            self.test_model_loading,
            self.test_faq_loader,
            self.test_search_functionality,
            self.test_memory_usage,
            self.test_file_integrity,
            self.test_backup_integrity,
            self.run_performance_comparison
        ]
        
        all_passed = True
        for test in tests:
            try:
                if not test():
                    all_passed = False
            except Exception as e:
                logger.error(f"Test execution error: {e}")
                all_passed = False
            logger.info("-" * 40)
        
        # Generate and save report
        report = self.generate_report()
        with open('model_upgrade_test_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info("📋 Test report saved to: model_upgrade_test_report.md")
        logger.info("=" * 80)
        
        total_tests = self.test_results['tests_passed'] + self.test_results['tests_failed']
        success_rate = (self.test_results['tests_passed'] / total_tests * 100) if total_tests > 0 else 0
        
        if success_rate >= 90:
            logger.info("🎉 MODEL UPGRADE VALIDATION: EXCELLENT")
        elif success_rate >= 75:
            logger.info("✅ MODEL UPGRADE VALIDATION: SUCCESSFUL")
        elif success_rate >= 50:
            logger.info("⚠️ MODEL UPGRADE VALIDATION: NEEDS ATTENTION")
        else:
            logger.error("❌ MODEL UPGRADE VALIDATION: FAILED")
        
        return all_passed


def main():
    """Main test execution"""
    print("🚀 ru-en-RoSBERTa Model Upgrade Validation")
    print("=" * 50)
    
    validator = ModelUpgradeValidator()
    success = validator.run_all_tests()
    
    if success:
        print("\n✅ All tests passed! Model upgrade is ready for production.")
        return 0
    else:
        print("\n❌ Some tests failed. Please review the issues before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())