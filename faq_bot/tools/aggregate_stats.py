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
    
    args = parser.parse_args()
    
    # Resolve log file path
    log_file_path = Path(args.log_file).resolve()
    
    # Check if log file exists
    if not log_file_path.exists():
        # Try relative to script location
        script_dir = Path(__file__).parent
        log_file_path = (script_dir.parent / args.log_file).resolve()
        
        if not log_file_path.exists():
            print(f"Error: Log file not found: {args.log_file}")
            return
    
    print(f"Parsing log file: {log_file_path}")
    
    # Parse log entries
    log_entries = parse_log_file(log_file_path)
    
    if not log_entries:
        print("No log entries found")
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