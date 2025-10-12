import logging
import os
import asyncio
import json
from aiogram import types
from aiogram.exceptions import TelegramRetryAfter, TelegramNetworkError

async def retry_file_operation(operation, max_retries=3, delay=1):
    """Retry file operation on network errors"""
    for attempt in range(max_retries):
        try:
            return await operation()
        except (TelegramNetworkError, ConnectionError, OSError) as e:
            if attempt == max_retries - 1:
                raise e
            wait_time = delay * (attempt + 1)
            logging.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}. Retrying in {wait_time} seconds.")
            await asyncio.sleep(wait_time)
        except TelegramRetryAfter as e:
            logging.warning(f"Waiting required {e.retry_after} seconds.")
            await asyncio.sleep(e.retry_after)
        except Exception as e:
            # For other errors, don't retry
            raise e
    return None

async def send_file_with_retry(message, file_path):
    """Send file with retry mechanism"""
    async def send_file():
        if message:
            return await message.answer_document(types.FSInputFile(file_path))
        return None
    
    return await retry_file_operation(send_file)

def check_file_size(file_path, max_size_mb=50):
    """Check if file size is within limits"""
    try:
        file_size = os.path.getsize(file_path)
        max_size_bytes = max_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            return False, file_size
        return True, file_size
    except OSError as e:
        logging.error(f"Error checking file size: {e}")
        return False, 0

def remove_keyboard(message):
    """Remove keyboard from message"""
    try:
        if message and hasattr(message, 'edit_reply_markup') and not isinstance(message, types.InaccessibleMessage):
            return message.edit_reply_markup(reply_markup=None)
    except Exception as e:
        logging.warning(f"Could not remove keyboard: {e}")
    return None

def send_callback_answer(callback, text, show_alert=False):
    """Send callback answer with error handling"""
    try:
        return callback.answer(text, show_alert=show_alert)
    except Exception as e:
        logging.warning(f"Could not send callback answer: {e}")
        return None

def validate_faq_files(faq_file_path):
    """Validate that all file paths in faq.json exist"""
    missing_files = []
    valid_entries = []
    
    try:
        with open(faq_file_path, 'r', encoding='utf-8') as f:
            faq_data = json.load(f)
        
        # Get the base directory for relative paths
        base_dir = os.path.dirname(faq_file_path)
        project_root = os.path.dirname(base_dir)  # This should be the project root
        
        for entry in faq_data:
            if 'resources' in entry:
                for resource in entry['resources']:
                    if resource.get('type') == 'file':
                        files = resource.get('files', [])
                        for file_path in files:
                            # Check if it's an absolute path or relative path
                            if os.path.isabs(file_path):
                                full_path = file_path
                            else:
                                # For relative paths, join with project root
                                full_path = os.path.join(project_root, file_path)
                            
                            if not os.path.exists(full_path):
                                missing_files.append({
                                    'query': entry.get('query', 'Unknown'),
                                    'file_path': file_path,
                                    'full_path': full_path
                                })
                                logging.warning(f"Missing file: {full_path} for query: {entry.get('query', 'Unknown')}")
                            else:
                                valid_entries.append({
                                    'query': entry.get('query', 'Unknown'),
                                    'file_path': file_path,
                                    'full_path': full_path
                                })
                                logging.info(f"Valid file: {full_path} for query: {entry.get('query', 'Unknown')}")
    
    except Exception as e:
        logging.error(f"Error validating FAQ files: {e}")
        return [], []
    
    return missing_files, valid_entries