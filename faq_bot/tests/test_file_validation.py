#!/usr/bin/env python3
"""
Test file validation to ensure all FAQ entries have valid file paths
"""

import sys
import os

# Add the src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_file_validation():
    """Test if all file paths in FAQ are valid"""
    print("🔍 Testing FAQ file path validation...")
    
    try:
        from utils import validate_faq_files
        
        # Get the FAQ file path
        faq_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'faq.json')
        
        if not os.path.exists(faq_file_path):
            print("❌ FAQ file not found")
            return False
        
        # Validate files
        missing_files, valid_files = validate_faq_files(faq_file_path)
        
        print(f"✅ Validated {len(valid_files)} file paths")
        
        if missing_files:
            print(f"❌ Found {len(missing_files)} missing files:")
            for mf in missing_files[:5]:  # Show first 5 missing files
                print(f"   - {mf['file_path']} (query: {mf['query']})")
            if len(missing_files) > 5:
                print(f"   ... and {len(missing_files) - 5} more")
            return False
        else:
            print("✅ All file paths are valid")
            return True
            
    except Exception as e:
        print(f"❌ File validation test failed: {e}")
        return False

def test_specific_tv_files():
    """Test specific TV summary files that were reported as missing"""
    print("🔍 Testing specific TV summary files...")
    
    # Get the project root directory
    project_root = os.path.join(os.path.dirname(__file__), '..')
    
    # Check if the specific files exist
    tv_2025_file = os.path.join(project_root, "files", "190625_СводнаяТВ+AI 2025.pdf")
    soundbar_2025_file = os.path.join(project_root, "files", "photo_2025-09-08_20-59-17.jpg")
    
    if os.path.exists(tv_2025_file):
        print(f"✅ TV 2025 file exists: {os.path.relpath(tv_2025_file, project_root)}")
        tv_2025_exists = True
    else:
        print(f"❌ TV 2025 file not found: {os.path.relpath(tv_2025_file, project_root)}")
        tv_2025_exists = False
    
    if os.path.exists(soundbar_2025_file):
        print(f"✅ Soundbar 2025 file exists: {os.path.relpath(soundbar_2025_file, project_root)}")
        soundbar_2025_exists = True
    else:
        print(f"❌ Soundbar 2025 file not found: {os.path.relpath(soundbar_2025_file, project_root)}")
        soundbar_2025_exists = False
    
    return tv_2025_exists and soundbar_2025_exists

def main():
    """Main test function"""
    print("⚙️ File Validation Tests")
    print("=" * 40)
    
    # Run tests
    validation_result = test_file_validation()
    files_result = test_specific_tv_files()
    
    print("\n" + "=" * 40)
    
    if validation_result and files_result:
        print("🎉 All file validation tests passed!")
        return 0
    else:
        print("⚠️ Some file validation tests failed. Please check the issues above.")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)