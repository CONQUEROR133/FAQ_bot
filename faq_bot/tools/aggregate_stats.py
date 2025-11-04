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

def get_response_time_stats(log_entries):
    """
    Get response time statistics.
    
    Args:
        log_entries (list): List of log entries
        
    Returns:
        dict: Dictionary with response time statistics
    """
    response_times = []
    
    for entry in log_entries:
        if entry.get('handler') == 'message_handler_result' and 'response_time' in entry:
            response_times.append(entry['response_time'])
    
    if not response_times:
        return {}
    
    return {
        'count': len(response_times),
        'avg': sum(response_times) / len(response_times),
        'min': min(response_times),
        'max': max(response_times),
        'median': sorted(response_times)[len(response_times) // 2]
    }

def get_cache_hit_stats(log_entries):
    """
    Get cache hit statistics.
    
    Args:
        log_entries (list): List of log entries
        
    Returns:
        dict: Dictionary with cache hit statistics
    """
    cache_hits = 0
    total_queries = 0
    
    for entry in log_entries:
        if entry.get('handler') == 'message_handler_result' and 'cache_hit' in entry:
            total_queries += 1
            if entry.get('cache_hit'):
                cache_hits += 1
    
    if total_queries == 0:
        return {}
    
    return {
        'total': total_queries,
        'hits': cache_hits,
        'hit_rate': (cache_hits / total_queries) * 100
    }

def get_similarity_score_distribution(log_entries):
    """
    Get similarity score distribution.
    
    Args:
        log_entries (list): List of log entries
        
    Returns:
        dict: Dictionary with similarity score distribution
    """
    distribution = defaultdict(int)
    
    for entry in log_entries:
        if entry.get('handler') == 'message_handler_result' and 'query_similarity' in entry:
            similarity = entry['query_similarity']
            if similarity >= 0.9:
                distribution['0.9-1.0'] += 1
            elif similarity >= 0.8:
                distribution['0.8-0.9'] += 1
            elif similarity >= 0.7:
                distribution['0.7-0.8'] += 1
            elif similarity >= 0.6:
                distribution['0.6-0.7'] += 1
            elif similarity >= 0.5:
                distribution['0.5-0.6'] += 1
            else:
                distribution['<0.5'] += 1
    
    return dict(distribution)

def get_query_length_stats(log_entries):
    """
    Get query length statistics.
    
    Args:
        log_entries (list): List of log entries
        
    Returns:
        dict: Dictionary with query length statistics
    """
    query_lengths = []
    
    for entry in log_entries:
        if entry.get('handler') == 'message_handler' and 'query_length' in entry:
            query_lengths.append(entry['query_length'])
    
    if not query_lengths:
        return {}
    
    return {
        'count': len(query_lengths),
        'avg': sum(query_lengths) / len(query_lengths),
        'min': min(query_lengths),
        'max': max(query_lengths),
        'median': sorted(query_lengths)[len(query_lengths) // 2]
    }

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
    headers = ['timestamp', 'level', 'logger', 'message', 'user_id', 'chat_id', 'message_id', 'handler', 
               'query_similarity', 'response_time', 'cache_hit', 'query_length']
    
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
                        'handler': entry.get('handler', ''),
                        'query_similarity': entry.get('query_similarity', ''),
                        'response_time': entry.get('response_time', ''),
                        'cache_hit': entry.get('cache_hit', ''),
                        'query_length': entry.get('query_length', '')
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
        print(f"Archived to: {archive_dir}")
    for file_info in cleared_files:
        print(f"  - {file_info}")
    
    logger.info(f"Statistics clearing completed. Files processed: {len(cleared_files)}")
    return True

def analyze_logs(log_file_path):
    """
    Analyze log files and generate detailed statistics.
    
    Args:
        log_file_path (str): Path to the main log file
    """
    print("=== DETAILED STATISTICAL ANALYSIS ===")
    
    # Parse log file
    log_entries = parse_log_file(log_file_path)
    
    if not log_entries:
        print("No log entries found for analysis")
        return
    
    print(f"Total log entries: {len(log_entries)}")
    
    # Get basic statistics
    total_requests = get_total_requests(log_entries)
    print(f"Total requests: {total_requests}")
    
    # Get top queries
    top_queries = get_top_queries(log_entries, 10)
    if top_queries:
        print("\n=== TOP 10 POPULAR QUERIES ===")
        for i, (query, count) in enumerate(top_queries, 1):
            print(f"{i}. {query} - {count} requests")
    
    # Get response time statistics
    response_stats = get_response_time_stats(log_entries)
    if response_stats:
        print("\n=== RESPONSE TIME STATISTICS ===")
        print(f"Total queries with response time: {response_stats['count']}")
        print(f"Average response time: {response_stats['avg']:.2f} ms")
        print(f"Minimum response time: {response_stats['min']} ms")
        print(f"Maximum response time: {response_stats['max']} ms")
        print(f"Median response time: {response_stats['median']} ms")
    
    # Get cache hit statistics
    cache_stats = get_cache_hit_stats(log_entries)
    if cache_stats:
        print("\n=== CACHE PERFORMANCE ===")
        print(f"Total queries: {cache_stats['total']}")
        print(f"Cache hits: {cache_stats['hits']}")
        print(f"Cache hit rate: {cache_stats['hit_rate']:.2f}%")
    
    # Get similarity score distribution
    similarity_dist = get_similarity_score_distribution(log_entries)
    if similarity_dist:
        print("\n=== SIMILARITY SCORE DISTRIBUTION ===")
        for range_name, count in sorted(similarity_dist.items(), key=lambda x: x[0], reverse=True):
            print(f"{range_name}: {count} queries")
    
    # Get query length statistics
    length_stats = get_query_length_stats(log_entries)
    if length_stats:
        print("\n=== QUERY LENGTH STATISTICS ===")
        print(f"Total queries with length data: {length_stats['count']}")
        print(f"Average query length: {length_stats['avg']:.2f} characters")
        print(f"Shortest query: {length_stats['min']} characters")
        print(f"Longest query: {length_stats['max']} characters")
        print(f"Median query length: {length_stats['median']} characters")

def main():
    parser = argparse.ArgumentParser(description="Aggregate and analyze bot statistics")
    parser.add_argument("--log-file", default="logs/bot.log", help="Path to log file")
    parser.add_argument("--export-csv", help="Export to CSV file")
    parser.add_argument("--analyze", action="store_true", help="Perform detailed analysis")
    parser.add_argument("--clear", action="store_true", help="Clear/archive statistics")
    parser.add_argument("--no-archive", action="store_true", help="Delete instead of archiving when clearing")
    
    args = parser.parse_args()
    
    if args.analyze:
        analyze_logs(args.log_file)
    
    if args.export_csv:
        log_entries = parse_log_file(args.log_file)
        export_to_csv(log_entries, args.export_csv)
    
    if args.clear:
        clear_stats(args.log_file, archive=not args.no_archive)

if __name__ == "__main__":
    main()
