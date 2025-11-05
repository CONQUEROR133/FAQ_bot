import logging
import os
import asyncio
import json
from typing import Tuple, List, Dict, Any, Optional, Callable
from aiogram import types
from aiogram.exceptions import TelegramRetryAfter, TelegramNetworkError

async def retry_file_operation(operation: Callable, max_retries: int = 3, delay: int = 1) -> Any:
    """Retry file operation on network errors.
    
    Args:
        operation: Async callable to retry
        max_retries: Maximum number of retry attempts
        delay: Base delay between retries in seconds
        
    Returns:
        Any: Result of the operation
        
    Raises:
        Exception: If all retry attempts fail
    """
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

async def send_file_with_retry(message: types.Message, file_path: str) -> Optional[types.Message]:
    """Send file with retry mechanism.
    
    Args:
        message: Message object to respond to
        file_path: Path to the file to send
        
    Returns:
        Optional[types.Message]: Sent message or None if failed
    """
    async def send_file():
        if message:
            return await message.answer_document(types.FSInputFile(file_path))
        return None
    
    return await retry_file_operation(send_file)

def check_file_size(file_path: str, max_size_mb: int = 50) -> Tuple[bool, int]:
    """Check if file size is within limits.
    
    Args:
        file_path: Path to the file to check
        max_size_mb: Maximum allowed size in MB
        
    Returns:
        Tuple[bool, int]: (is_within_limit, file_size_in_bytes)
    """
    try:
        file_size = os.path.getsize(file_path)
        max_size_bytes = max_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            return False, file_size
        return True, file_size
    except OSError as e:
        logging.error(f"Error checking file size: {e}")
        return False, 0

def remove_keyboard(message: types.Message) -> Any:
    """Remove keyboard from message.
    
    Args:
        message: Message object to remove keyboard from
        
    Returns:
        Any: Result of the operation
    """
    try:
        if message and hasattr(message, 'edit_reply_markup') and not isinstance(message, types.InaccessibleMessage):
            return message.edit_reply_markup(reply_markup=None)
    except Exception as e:
        logging.warning(f"Could not remove keyboard: {e}")
    return None

def send_callback_answer(callback: types.CallbackQuery, text: str, show_alert: bool = False) -> Any:
    """Send callback answer with error handling.
    
    Args:
        callback: Callback query to answer
        text: Text to send
        show_alert: Whether to show as alert
        
    Returns:
        Any: Result of the operation
    """
    try:
        return callback.answer(text, show_alert=show_alert)
    except Exception as e:
        logging.warning(f"Could not send callback answer: {e}")
        return None

def validate_faq_files(faq_file_path: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Validate that all file paths in faq.json exist.
    
    Args:
        faq_file_path: Path to the FAQ JSON file
        
    Returns:
        Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]: (missing_files, valid_entries)
    """
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

async def send_resource_files(message: types.Message, files: List[str], max_file_size_mb: int = 50) -> List[str]:
    """Send multiple files with error handling and size checking.
    
    Args:
        message: The message object to respond to
        files: List of file paths to send
        max_file_size_mb: Maximum file size in MB
        
    Returns:
        List[str]: List of successfully sent file names
    """
    sent_files = []
    for file_path in files:
        if not file_path or not os.path.exists(file_path):
            logging.warning(f"File not found: {file_path}")
            continue
            
        # Check file size
        try:
            file_size = os.path.getsize(file_path)
            if file_size > max_file_size_mb * 1024 * 1024:
                logging.warning(f"File too large: {file_path}")
                continue
        except OSError as e:
            logging.error(f"Error checking file size: {e}")
            continue
        
        # Send file with retries
        try:
            await send_file_with_retry(message, file_path)
            sent_files.append(os.path.basename(file_path))
            logging.info(f"Successfully sent file: {file_path}")
        except Exception as send_error:
            logging.error(f"Error sending file: {send_error}")
            continue
    
    return sent_files