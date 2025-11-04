#!/usr/bin/env python3
"""
Cleanup script for FAQ Bot
Removes unnecessary files and directories to create a minimal, cross-platform version
"""

import os
import shutil

def remove_files_and_dirs():
    """Remove unnecessary files and directories"""
    # List of files/directories to remove
    to_remove = [
        # Windows-specific batch files
        '0_Setup.bat',
        '1_Start_Bot.bat',
        '2_Stop_bot.bat',
        '3_Clean_All.bat',
        '4_Train_Model.bat',
        '5_Check_Status.bat',
        '6_Clear_Stats.bat',
        'optimized_clean.bat',
        'optimized_setup.bat',
        'optimized_start_bot.bat',
        'optimized_train_model.bat',
        'setup.bat',
        'start.bat',
        'start.py',
        'start_bot.py',
        'run_bot.py',
        
        # PowerShell scripts (if any)
        '*.ps1',
        
        # Redundant documentation
        'CONSOLIDATED_DOCUMENTATION.md',
        'FINAL_PROJECT_SUMMARY.md',
        'LOGS_AND_ANALYTICS_GUIDE.md',
        'OPTIMIZED_SCRIPTS.md',
        'PRODUCTION_SETUP.md',
        'PROJECT_ORGANIZATION_SUMMARY.md',
        
        # Cache directories
        '.pytest_cache',
        'backups',
        'venv',
        
        # Template files (if not needed)
        'templates',
        
        # Tools directory (if empty or not needed)
        # 'tools',
        
        # Files directory (check if needed)
        # 'files'
    ]
    
    print("🧹 Cleaning up unnecessary files and directories...")
    
    removed_count = 0
    for item in to_remove:
        if os.path.exists(item):
            try:
                if os.path.isfile(item):
                    os.remove(item)
                    print(f"✅ Removed file: {item}")
                elif os.path.isdir(item):
                    shutil.rmtree(item)
                    print(f"✅ Removed directory: {item}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Error removing {item}: {e}")
        elif '*' in item:  # Handle glob patterns
            import glob
            matches = glob.glob(item)
            for match in matches:
                try:
                    if os.path.isfile(match):
                        os.remove(match)
                        print(f"✅ Removed file: {match}")
                    elif os.path.isdir(match):
                        shutil.rmtree(match)
                        print(f"✅ Removed directory: {match}")
                    removed_count += 1
                except Exception as e:
                    print(f"❌ Error removing {match}: {e}")
    
    print(f"\n🎉 Cleanup completed! Removed {removed_count} items.")

if __name__ == "__main__":
    remove_files_and_dirs()