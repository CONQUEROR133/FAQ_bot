#!/usr/bin/env python3
"""
Simple test script to check if FAQ loader works
"""

import sys
import os

# Add the src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from faq_loader import FAQLoader
    print("✅ FAQ loader imported successfully")
    
    # Initialize FAQ loader
    loader = FAQLoader()
    stats = loader.load_faq()
    print(f"✅ FAQ loaded successfully: {stats.valid_queries} valid entries")
    
    # Check if we have FAQ data
    if loader.faq:
        print(f"✅ FAQ data loaded with {len(loader.faq)} entries")
        # Show first few entries
        for i, entry in enumerate(loader.faq[:3]):
            print(f"  Entry {i}: {entry.get('query', 'No query')}")
    else:
        print("❌ FAQ data is empty")
        
except Exception as e:
    print(f"❌ Error testing FAQ loader: {e}")
    import traceback
    traceback.print_exc()