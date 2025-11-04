#!/usr/bin/env python3
"""
Script to clear all statistics data from the FAQ bot database.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path so we can import the database module
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from database import Database
    import logging

    def setup_logging():
        """Setup logging for the clear stats operation."""
        # Create logs directory if it doesn't exist
        logs_dir = Path(__file__).parent / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(logs_dir / "stats_clear.log", encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)

    def main():
        """Main function to clear all statistics."""
        logger = setup_logging()
        
        try:
            logger.info("Starting statistics clearing process...")
            
            # Initialize database
            db = Database()
            
            # Get stats before clearing
            stats_before = db.get_stats()
            logger.info(f"Statistics before clearing: {stats_before.total_queries} queries, "
                       f"{stats_before.authenticated_users_count} users, "
                       f"{stats_before.unanswered_questions} unanswered questions")
            
            # Clear all statistics
            success = db.clear_all_stats()
            
            if success:
                logger.info("[SUCCESS] Statistics cleared successfully!")
                print("[SUCCESS] Statistics cleared successfully!")
                print(f"  - Cleared {stats_before.total_queries} queries")
                print(f"  - Cleared {stats_before.authenticated_users_count} user records")
                print(f"  - Cleared {stats_before.unanswered_questions} unanswered questions")
                print(f"  - Cleared {stats_before.bad_words_count} bad word records")
                return 0
            else:
                logger.error("[ERROR] Failed to clear statistics")
                print("[ERROR] Failed to clear statistics")
                return 1
                
        except Exception as e:
            logger.error(f"[ERROR] Error clearing statistics: {e}")
            print(f"[ERROR] Error clearing statistics: {e}")
            return 1

    if __name__ == "__main__":
        sys.exit(main())

except ImportError as e:
    print(f"[ERROR] Error importing modules: {e}")
    print("Make sure you're running this script from the project directory and all dependencies are installed.")
    sys.exit(1)