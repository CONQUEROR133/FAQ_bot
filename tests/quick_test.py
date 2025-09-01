#!/usr/bin/env python3
"""Simple validation script for model upgrade"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent.parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

# Verify the path exists
if not src_path.exists():
    print(f"❌ Source path does not exist: {src_path}")
    sys.exit(1)

print(f"📁 Using source path: {src_path}")
print(f"🔍 Python path updated")

# Import the modules we need
try:
    # Import config module from src
    sys.path.insert(0, str(src_path))
    
    # Use importlib for more reliable imports
    import importlib.util
    
    # Load config module
    config_spec = importlib.util.spec_from_file_location("config", src_path / "config.py")
    if config_spec is None or config_spec.loader is None:
        raise ImportError(f"Could not load config spec from {src_path / 'config.py'}")
    
    config_module = importlib.util.module_from_spec(config_spec)
    config_spec.loader.exec_module(config_module)
    
    # Load faq_loader module  
    faq_spec = importlib.util.spec_from_file_location("faq_loader", src_path / "faq_loader.py")
    if faq_spec is None or faq_spec.loader is None:
        raise ImportError(f"Could not load faq_loader spec from {src_path / 'faq_loader.py'}")
        
    faq_module = importlib.util.module_from_spec(faq_spec)
    faq_spec.loader.exec_module(faq_module)
    
    print("✅ Modules loaded successfully")
    
except ImportError as e:
    print(f"❌ Failed to import modules: {e}")
    print(f"   Source path: {src_path}")
    sys.exit(1)

def test_config():
    try:
        print(f"✅ Model: {config_module.config.MODEL_NAME}")
        print(f"✅ Threshold: {config_module.config.SIMILARITY_THRESHOLD}")
        print(f"✅ Password: {'Environment Variable' if hasattr(config_module.config, 'ACCESS_PASSWORD') else 'Hardcoded'}")
        return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def test_model_loading():
    try:
        from sentence_transformers import SentenceTransformer
        
        print(f"🔄 Loading model {config_module.config.MODEL_NAME}...")
        model = SentenceTransformer(config_module.config.MODEL_NAME)
        print(f"✅ Model loaded successfully!")
        
        # Test encoding
        test_text = "Как получить рассрочку"
        embedding = model.encode([test_text])
        print(f"✅ Embedding created: {embedding.shape}")
        return True
    except Exception as e:
        print(f"❌ Model loading error: {e}")
        return False

def test_faq_basic():
    try:
        print("🔄 Testing FAQ loader...")
        faq_loader = faq_module.FAQLoader()
        faq_loader.load_faq()
        faq_count = len(faq_loader.faq) if faq_loader.faq else 0
        print(f"✅ FAQ loaded: {faq_count} entries")
        
        faq_loader.create_embeddings()
        print("✅ Embeddings created successfully!")
        
        # Test search
        distances, indices = faq_loader.search("Как получить рассрочку", k=1)
        if distances is not None:
            print(f"✅ Search test successful: {distances[0]:.3f} similarity")
        else:
            print("⚠️ Search test: No results found")
        
        return True
    except Exception as e:
        print(f"❌ FAQ loader error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Quick Model Upgrade Validation")
    print("=" * 40)
    
    tests_passed = 0
    total_tests = 3
    
    if test_config():
        tests_passed += 1
    
    if test_model_loading():
        tests_passed += 1
    
    if test_faq_basic():
        tests_passed += 1
    
    print("=" * 40)
    print(f"Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Model upgrade successful!")
    else:
        print("⚠️ Some tests failed. Check the errors above.")