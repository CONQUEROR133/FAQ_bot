#!/usr/bin/env python3
"""
Cleanup script for FAQ Bot
This script removes unnecessary files and optimizes the directory structure
"""

import os
import sys
import shutil
from pathlib import Path

def cleanup_unnecessary_files():
    """Remove unnecessary files and optimize directory structure"""
    base_dir = Path(__file__).parent
    
    # Files/directories to remove if they exist
    unnecessary_items = [
        'training.log',  # Old training log file
        'backups',  # Backup directory (if empty)
    ]
    
    removed_items = []
    
    for item in unnecessary_items:
        item_path = base_dir / item
        if item_path.exists():
            try:
                if item_path.is_file():
                    item_path.unlink()
                    removed_items.append(f"Removed file: {item}")
                elif item_path.is_dir():
                    # Only remove directory if it's empty
                    if not any(item_path.iterdir()):
                        shutil.rmtree(item_path)
                        removed_items.append(f"Removed directory: {item}")
            except Exception as e:
                print(f"Warning: Could not remove {item}: {e}")
    
    return removed_items

def optimize_cache():
    """Optimize cache directory"""
    base_dir = Path(__file__).parent
    cache_dir = base_dir / 'cache'
    
    if not cache_dir.exists():
        cache_dir.mkdir(parents=True, exist_ok=True)
        return ["Created cache directory"]
    
    # Check cache size
    total_size = 0
    for file_path in cache_dir.rglob('*'):
        if file_path.is_file():
            total_size += file_path.stat().st_size
    
    size_mb = total_size / (1024 * 1024)
    
    if size_mb > 100:  # If cache is larger than 100MB
        return [f"Cache directory is {size_mb:.2f}MB - consider running 3_Clean_All.bat to clear cache"]
    
    return [f"Cache directory is {size_mb:.2f}MB - within acceptable limits"]

def main():
    """Main cleanup function"""
    print("🧹 FAQ Bot Cleanup Script")
    print("=" * 30)
    
    # Cleanup unnecessary files
    removed_items = cleanup_unnecessary_files()
    for item in removed_items:
        print(f"✅ {item}")
    
    # Optimize cache
    cache_items = optimize_cache()
    for item in cache_items:
        print(f"ℹ️  {item}")
    
    if not removed_items and "within acceptable limits" in cache_items[0]:
        print("✅ No cleanup needed - directory structure is already optimized")
    
    print("\n🎉 Cleanup completed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())