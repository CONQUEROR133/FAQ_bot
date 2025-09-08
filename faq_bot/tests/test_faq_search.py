#!/usr/bin/env python3
"""
FAQ search functionality test to verify search and embedding functionality
"""

import sys
import os

# Add the src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_faq_loader_import():
    """Test if FAQ loader can be imported"""
    print("🔍 Testing FAQ loader import...")
    
    try:
        from faq_loader import FAQLoader
        print("✅ FAQ loader imported successfully")
        return True
    except Exception as e:
        print(f"❌ FAQ loader import failed: {e}")
        return False

def test_faq_loader_initialization():
    """Test if FAQ loader can be initialized"""
    print("🔍 Testing FAQ loader initialization...")
    
    try:
        from faq_loader import FAQLoader
        
        # Try to initialize with default paths
        loader = FAQLoader()
        print("✅ FAQ loader initialized successfully")
        
        # Check that paths are set
        if hasattr(loader, 'faq_file') and loader.faq_file:
            print(f"✅ FAQ file path set: {loader.faq_file}")
        
        if hasattr(loader, 'embeddings_file') and loader.embeddings_file:
            print(f"✅ Embeddings file path set: {loader.embeddings_file}")
            
        if hasattr(loader, 'index_file') and loader.index_file:
            print(f"✅ Index file path set: {loader.index_file}")
        
        return True
    except Exception as e:
        print(f"❌ FAQ loader initialization failed: {e}")
        return False

def test_embedding_model_loading():
    """Test if embedding model can be loaded"""
    print("🔍 Testing embedding model loading...")
    
    try:
        from sentence_transformers import SentenceTransformer
        import torch
        
        # Try to load a small model for testing
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        print("✅ Embedding model loaded successfully")
        
        # Test basic encoding
        test_sentences = ["тестовый вопрос", "пример запроса"]
        embeddings = model.encode(test_sentences)
        print(f"✅ Embedding generation works: {len(embeddings)} embeddings generated")
        
        return True
    except Exception as e:
        print(f"❌ Embedding model loading failed: {e}")
        return False

def test_cache_directory():
    """Test if cache directory exists and is writable"""
    print("🔍 Testing cache directory...")
    
    try:
        # Check cache directory
        cache_dir = os.path.join(os.path.dirname(__file__), '..', 'cache')
        os.makedirs(cache_dir, exist_ok=True)
        
        if os.path.exists(cache_dir):
            print("✅ Cache directory exists")
        else:
            print("❌ Cache directory does not exist")
            return False
        
        # Test write access
        test_file = os.path.join(cache_dir, 'test_write.tmp')
        with open(test_file, 'w') as f:
            f.write('test')
        
        if os.path.exists(test_file):
            os.remove(test_file)
            print("✅ Cache directory is writable")
            return True
        else:
            print("❌ Cache directory is not writable")
            return False
            
    except Exception as e:
        print(f"❌ Cache directory test failed: {e}")
        return False

def main():
    print("🧠 FAQ Search Functionality Tests")
    print("=" * 40)
    
    tests = [
        ("FAQ Loader Import", test_faq_loader_import()),
        ("FAQ Loader Initialization", test_faq_loader_initialization()),
        ("Embedding Model Loading", test_embedding_model_loading()),
        ("Cache Directory", test_cache_directory())
    ]
    
    success_count = 0
    for test_name, result in tests:
        if result:
            success_count += 1
            print(f"✅ {test_name} passed")
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 40)
    print(f"📊 Results: {success_count}/{len(tests)} tests passed")
    
    if success_count == len(tests):
        print("🎉 All FAQ search tests passed!")
        return 0
    else:
        print("⚠️ Some FAQ search tests failed. Please check the issues above.")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)