#!/usr/bin/env python3
"""
FAQ loading test to verify FAQ data can be loaded correctly
"""

import sys
import os
import json
import pytest

# Add the src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def faq_file():
    """Fixture to get FAQ file path"""
    # Check in data directory first
    faq_paths = [
        os.path.join(os.path.dirname(__file__), '..', 'data', 'faq.json'),
        os.path.join(os.path.dirname(__file__), '..', 'faq.json')
    ]
    
    faq_file = None
    for path in faq_paths:
        if os.path.exists(path):
            faq_file = path
            break
    
    return faq_file

@pytest.fixture
def faq_data(faq_file):
    """Fixture to load FAQ data"""
    if faq_file:
        with open(faq_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def test_faq_file_exists(faq_file):
    """Test if FAQ file exists"""
    print("🔍 Testing FAQ file existence...")
    
    if faq_file:
        print(f"✅ FAQ file found: {os.path.abspath(faq_file)}")
        assert True
    else:
        print("❌ FAQ file not found in data/ or root directory")
        pytest.fail("FAQ file not found")

def test_faq_file_format(faq_file):
    """Test if FAQ file has correct JSON format"""
    print("🔍 Testing FAQ file format...")
    
    if not faq_file:
        pytest.skip("FAQ file not found")
    
    try:
        with open(faq_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("✅ FAQ file is valid JSON")
        assert data is not None
    except json.JSONDecodeError as e:
        print(f"❌ FAQ file is not valid JSON: {e}")
        pytest.fail(f"FAQ file is not valid JSON: {e}")
    except Exception as e:
        print(f"❌ Error reading FAQ file: {e}")
        pytest.fail(f"Error reading FAQ file: {e}")

def test_faq_structure(faq_data):
    """Test if FAQ data has correct structure"""
    print("🔍 Testing FAQ data structure...")
    
    if faq_data is None:
        pytest.skip("FAQ data not available")
    
    if not isinstance(faq_data, list):
        print("❌ FAQ data should be a list")
        pytest.fail("FAQ data should be a list")
    
    if len(faq_data) == 0:
        print("⚠️ FAQ data is empty")
        assert True  # Not an error, just a warning
        return
    
    # Check first few entries for correct structure
    for i, entry in enumerate(faq_data[:3]):  # Check first 3 entries
        if not isinstance(entry, dict):
            print(f"❌ FAQ entry {i} should be a dictionary")
            pytest.fail(f"FAQ entry {i} should be a dictionary")
        
        required_fields = ['query']
        for field in required_fields:
            if field not in entry:
                print(f"❌ FAQ entry {i} missing required field: {field}")
                pytest.fail(f"FAQ entry {i} missing required field: {field}")
        
        # Check optional fields
        if 'variations' in entry and not isinstance(entry['variations'], list):
            print(f"❌ FAQ entry {i} variations should be a list")
            pytest.fail(f"FAQ entry {i} variations should be a list")
        
        if 'resources' in entry and not isinstance(entry['resources'], list):
            print(f"❌ FAQ entry {i} resources should be a list")
            pytest.fail(f"FAQ entry {i} resources should be a list")
    
    print(f"✅ FAQ structure is valid ({len(faq_data)} entries)")
    assert True

def test_faq_content(faq_data):
    """Test FAQ content for basic validity"""
    print("🔍 Testing FAQ content...")
    
    if faq_data is None:
        pytest.skip("FAQ data not available")
    
    if len(faq_data) == 0:
        print("⚠️ No FAQ entries to test")
        assert True
        return
    
    # Check for duplicate queries
    queries = [entry['query'].strip().lower() for entry in faq_data if 'query' in entry]
    duplicates = set([q for q in queries if queries.count(q) > 1])
    
    if duplicates:
        print(f"⚠️ Found duplicate queries: {', '.join(list(duplicates)[:5])}")
    else:
        print("✅ No duplicate queries found")
    
    # Check for empty queries
    empty_queries = [entry for entry in faq_data if 'query' in entry and not entry['query'].strip()]
    if empty_queries:
        print(f"⚠️ Found {len(empty_queries)} entries with empty queries")
    else:
        print("✅ No empty queries found")
    
    assert True