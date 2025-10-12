#!/usr/bin/env python3
"""
Utility script to aggregate and analyze bot statistics from JSON log files.
"""

import json
import os
import argparse
import csv
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
import shutil
import logging

def setup_logging():
    """Setup logging for stats clearing operations"""
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(logs_dir / "stats_clear.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def parse_log_file(log_file_path):
    """
    Parse a JSON log file and extract relevant statistics.
    
    Args:
        log_file_path (str): Path to the log file
        
    Returns:
        list: List of parsed log entries
    """
    log_entries = []
    
    # Try different encodings
    encodings = ['utf-8', 'cp1251', 'cp866', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(log_file_path, 'r', encoding=encoding) as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        entry = json.loads(line.strip())
                        log_entries.append(entry)
                    except json.JSONDecodeError as e:
                        print(f"Warning: Skipping invalid JSON on line {line_num}: {e}")
                        continue
            print(f"Successfully read log file with {encoding} encoding")
            break
        except UnicodeDecodeError:
            print(f"Failed to read with {encoding} encoding, trying next...")
            continue
        except FileNotFoundError:
            print(f"Error: Log file not found: {log_file_path}")
            return []
        except Exception as e:
            print(f"Error reading log file with {encoding}: {e}")
            continue
    else:
        print("Error: Could not read log file with any encoding")
        return []
        
    return log_entries

def get_total_requests(log_entries):
    """
    Count total requests from log entries.
    
    Args:
        log_entries (list): List of log entries
        
    Returns:
        int: Total number of requests
    """
    return len([entry for entry in log_entries if 'message_id' in entry])

def get_top_queries(log_entries, top_n=20):
    """
    Get the top N queries by count.
    
    Args:
        log_entries (list): List of log entries
        top_n (int): Number of top queries to return
        
    Returns:
        list: List of tuples (query, count)
    """
    query_counter = Counter()
    
    for entry in log_entries:
        # Look for user messages
        if entry.get('handler') == 'message_handler' and 'message' in entry:
            message = entry['message']
            if message.startswith('User message received:'):
                # Extract the actual query from the message
                query = message.replace('User message received: ', '').rstrip('.')
                query_counter[query] += 1
    
    return query_counter.most_common(top_n)

def export_to_csv(log_entries, output_file):
    """
    Export log entries to CSV format.
    
    Args:
        log_entries (list): List of log entries
        output_file (str): Output CSV file path
    """
    if not log_entries:
        print("No data to export")
        return
        
    # Define CSV headers
    headers = ['timestamp', 'level', 'logger', 'message', 'user_id', 'chat_id', 'message_id', 'handler']
    
    # Try different encodings for CSV export
    encodings = ['utf-8', 'cp1251']
    
    for encoding in encodings:
        try:
            with open(output_file, 'w', newline='', encoding=encoding) as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                
                for entry in log_entries:
                    row = {
                        'timestamp': entry.get('ts', ''),
                        'level': entry.get('level', ''),
                        'logger': entry.get('logger', ''),
                        'message': entry.get('message', ''),
                        'user_id': entry.get('user_id', ''),
                        'chat_id': entry.get('chat_id', ''),
                        'message_id': entry.get('message_id', ''),
                        'handler': entry.get('handler', '')
                    }
                    writer.writerow(row)
                    
            print(f"CSV export completed: {output_file} with {encoding} encoding")
            break
        except Exception as e:
            print(f"Error exporting to CSV with {encoding}: {e}")
            continue
    else:
        print("Error: Could not export CSV with any encoding")

def clear_stats(log_file_path, archive=True):
    """
    Clear statistics by deleting or archiving log files.
    
    Args:
        log_file_path (str): Path to the main log file
        archive (bool): Whether to archive files instead of deleting them
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger = setup_logging()
    
    # Try multiple paths to find the logs directory, prioritizing the project directory
    project_dir = Path(__file__).parent.parent
    possible_paths = [
        project_dir / log_file_path,  # Project directory (priority)
        Path(log_file_path),  # Relative to current directory
        Path.cwd() / log_file_path,  # Current working directory
    ]
    
    log_path = None
    logs_dir = None
    
    for path in possible_paths:
        if path.parent.exists():
            log_path = path
            logs_dir = path.parent
            break
    
    if log_path is None or logs_dir is None:
        print(f"Error: Could not find logs directory")
        logger.error(f"Could not find logs directory")
        return False
    
    # Create archive directory if archiving
    archive_dir = None
    if archive:
        archive_dir = logs_dir / "archive" / datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created archive directory: {archive_dir}")
    
    cleared_files = []
    
    # Find all log files (main log and backups)
    log_files = list(logs_dir.glob("bot.log*"))
    
    if not log_files:
        print("No log files found to clear")
        logger.info("No log files found to clear")
        return True
    
    # Process each log file
    for log_file in log_files:
        try:
            if archive and archive_dir:
                # Archive the file
                destination = archive_dir / log_file.name
                shutil.move(str(log_file), str(destination))
                cleared_files.append(f"Archived: {log_file.name}")
                logger.info(f"Archived {log_file.name} to {destination}")
            else:
                # Delete the file
                log_file.unlink()
                cleared_files.append(f"Deleted: {log_file.name}")
                logger.info(f"Deleted {log_file.name}")
        except Exception as e:
            error_msg = f"Error processing {log_file.name}: {e}"
            print(f"Error: {error_msg}")
            logger.error(error_msg)
            return False
    
    # Summary
    print(f"\nStatistics cleared successfully!")
    if archive:
        print(f"Files archived to: {archive_dir}")
    for file_info in cleared_files:
        print(f"  - {file_info}")
    
    logger.info(f"Statistics cleared. Files processed: {len(cleared_files)}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Aggregate and analyze bot statistics from JSON log files")
    parser.add_argument('--log-file', '-l', 
                        default='logs/bot.log',
                        help='Path to the log file (default: logs/bot.log)')
    parser.add_argument('--top-queries', '-t', 
                        type=int, 
                        default=20,
                        help='Number of top queries to display (default: 20)')
    parser.add_argument('--csv-export', '-c',
                        help='Export to CSV file')
    parser.add_argument('--csv-only', 
                        action='store_true',
                        help='Only export to CSV, do not display statistics')
    parser.add_argument('--clear-stats', 
                        action='store_true',
                        help='Clear all statistics by archiving log files')
    
    args = parser.parse_args()
    
    # Handle stats clearing
    if args.clear_stats:
        print("Clearing statistics...")
        # Use the default log file path
        success = clear_stats('logs/bot.log')
        if success:
            print("Statistics cleared successfully!")
        else:
            print("Error clearing statistics!")
        return
    
    # Resolve log file path
    log_file_path = Path(args.log_file).resolve()
    
    # Check if log file exists
    if not log_file_path.exists():
        # Try relative to script location
        script_dir = Path(__file__).parent
        log_file_path = (script_dir.parent / args.log_file).resolve()
        
        if not log_file_path.exists():
            print(f"⚠️  Warning: Log file not found: {args.log_file}")
            print("📊 No statistics available yet. The bot may not have processed any requests.")
            return
    
    print(f"Parsing log file: {log_file_path}")
    
    # Parse log entries
    log_entries = parse_log_file(log_file_path)
    
    if not log_entries:
        print("📊 No log entries found. Statistics will be available after the bot processes requests.")
        return
    
    print(f"Found {len(log_entries)} log entries")
    
    # Handle CSV export only mode
    if args.csv_only and args.csv_export:
        export_to_csv(log_entries, args.csv_export)
        return
    
    # Display statistics
    print("\n" + "="*50)
    print("BOT STATISTICS")
    print("="*50)
    
    total_requests = get_total_requests(log_entries)
    print(f"Total requests: {total_requests}")
    
    print(f"\nTop {args.top_queries} queries:")
    print("-" * 30)
    top_queries = get_top_queries(log_entries, args.top_queries)
    
    if top_queries:
        for i, (query, count) in enumerate(top_queries, 1):
            print(f"{i:2d}. {query} ({count} times)")
    else:
        print("No queries found in logs")
    
    # Handle CSV export
    if args.csv_export:
        export_to_csv(log_entries, args.csv_export)

if __name__ == "__main__":
    main()
















