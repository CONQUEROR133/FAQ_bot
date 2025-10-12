#!/usr/bin/env python3
"""
External health check script for the FAQ bot
Can be used by monitoring systems to check bot status
"""

import sys
import os
import json
import argparse
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_bot_status():
    """Check if bot is running by checking log files"""
    try:
        log_file = os.path.join(os.path.dirname(__file__), 'logs', 'bot.log')
        
        if not os.path.exists(log_file):
            return {
                "status": "error",
                "message": "Log file not found",
                "timestamp": datetime.now().isoformat()
            }
        
        # Check if log file has recent entries
        file_modified = os.path.getmtime(log_file)
        file_age_seconds = datetime.now().timestamp() - file_modified
        
        if file_age_seconds > 300:  # 5 minutes
            return {
                "status": "warning",
                "message": "Bot may be inactive (no recent logs)",
                "last_activity": file_age_seconds,
                "timestamp": datetime.now().isoformat()
            }
        
        return {
            "status": "healthy",
            "message": "Bot is active",
            "last_activity": file_age_seconds,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Health check failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

def main():
    parser = argparse.ArgumentParser(description='FAQ Bot Health Check')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    parser.add_argument('--quiet', action='store_true', help='Only output on error')
    
    args = parser.parse_args()
    
    status = check_bot_status()
    
    if args.json:
        print(json.dumps(status, indent=2))
    elif args.quiet:
        if status['status'] == 'error':
            print(f"ERROR: {status['message']}")
            sys.exit(1)
        elif status['status'] == 'warning':
            print(f"WARNING: {status['message']}")
            sys.exit(0)
    else:
        print(f"Status: {status['status']}")
        print(f"Message: {status['message']}")
        if 'last_activity' in status:
            print(f"Last activity: {status['last_activity']} seconds ago")
    
    # Exit with appropriate code
    if status['status'] == 'error':
        sys.exit(2)
    elif status['status'] == 'warning':
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()