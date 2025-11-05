import logging
import os
from typing import Set, Dict, Any, Optional, List, Tuple
from aiogram import types, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramRetryAfter, TelegramNetworkError
from aiogram.filters import Command, CommandStart

from utils import send_file_with_retry, remove_keyboard, send_callback_answer, send_resource_files

router = Router()

# Dictionary to track users waiting for authentication
waiting_for_password: Set[int] = set()

def check_authentication(message: Message, db: Any, config: Any) -> bool:
    """Check if user is authenticated"""
    if not message.from_user:
        return False
    
    user_id = message.from_user.id
    
    # Check if user is admin (admin doesn't need authentication)
    if user_id == config.ADMIN_ID:
        return True
    
    # Check in database
    return db.is_user_authenticated(user_id)

def check_authentication_for_callback(callback: CallbackQuery, db: Any, config: Any) -> bool:
    """Check authentication for callback query"""
    if not callback.from_user:
        return False
    
    user_id = callback.from_user.id
    
    # Check if user is admin
    if user_id == config.ADMIN_ID:
        return True
    
    # Check in database
    return db.is_user_authenticated(user_id)

async def auto_send_single_resource(message: Message, resource: Dict[str, Any]) -> bool:
    """Automatically sends a single resource without confirmation"""
    try:
        if resource.get('type') == 'file':
            # Send files
            files = resource.get('files', [])
            if not files:
                return False
            
            sent_files = await send_resource_files(message, files)
            # Send additional text if present
            if 'additional_text' in resource:
                try:
                    await message.answer(resource['additional_text'])
                except Exception as text_error:
                    logging.error(f"Error sending additional text: {text_error}")
            
            return len(sent_files) > 0
                    
        elif resource.get('type') == 'link':
            # Send link
            link = resource.get('link')
            if not link:
                return False
                
            try:
                await message.answer(link)
                logging.info(f"Successfully sent link: {link}")
                return True
            except Exception as send_error:
                logging.error(f"Error auto-sending link: {send_error}")
                return False
        
        return False
        
    except Exception as e:
        logging.error(f"Error in auto_send_single_resource: {str(e)}")
        return False

def should_auto_send_resource(resources: List[Dict[str, Any]]) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """Determines if a resource should be sent automatically"""
    if not resources or len(resources) != 1:
        return False, None
    
    resource = resources[0]
    
    # If auto_send: true is explicitly specified, then auto-send
    if resource.get('auto_send') is True:
        return True, resource
    
    # For links, always auto-send
    if resource.get('type') == 'link':
        return True, resource
    
    # For files - only if one file
    if resource.get('type') == 'file':
        files = resource.get('files', [])
        if len(files) == 1:
            return True, resource
    
    return False, None

def create_resource_selection_keyboard(match: Dict[str, Any], index: int) -> InlineKeyboardMarkup:
    """Creates a keyboard for resource selection"""
    keyboard = []
    
    # Add buttons for resources
    if 'resources' in match:
        for i, resource in enumerate(match['resources']):
            title = resource.get('title', 'Resource')
            callback_data = f"resource_{index}_{i}"
            
            # Add appropriate icon
            if resource.get('type') == 'file':
                icon = "📄"
            elif resource.get('type') == 'link':
                icon = "🔗"
            else:
                icon = "📎"
            
            keyboard.append([InlineKeyboardButton(
                text=f"{icon} {title}",
                callback_data=callback_data
            )])
    
    # "Cancel" button
    keyboard.append([InlineKeyboardButton(
        text="❌ Cancel",
        callback_data="cancel"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@router.callback_query(F.data.startswith("file_"))
async def file_selection_callback(callback: CallbackQuery, faq_loader: Any) -> None:
    """File selection handler"""
    try:
        # Check for callback.data presence
        if not callback.data:
            await callback.answer("❌ Invalid data")
            return
            
        # Parse callback_data: file_{index}_{file_key}_{file_index}
        parts = callback.data.split("_")
        if len(parts) < 4:
            await callback.answer("❌ Invalid data format")
            return
            
        index = int(parts[1])
        file_key = parts[2]
        file_index = int(parts[3])
        
        if not faq_loader.faq or index >= len(faq_loader.faq):
            await callback.answer("❌ Invalid index")
            return
            
        match = faq_loader.faq[index]
        
        if file_key not in match:
            await callback.answer("❌ File not found")
            return
            
        files = match[file_key] if isinstance(match[file_key], list) else [match[file_key]]
        
        if file_index >= len(files):
            await callback.answer("❌ Invalid file index")
            return
            
        file_path = files[file_index]
        
        if not file_path or not os.path.exists(file_path):
            logging.warning(f"File not found: {file_path}")
            await callback.answer("❌ File not found on disk")
            return
            
        # Check file size (maximum configured size)
        try:
            file_size = os.path.getsize(file_path)
            max_file_size_bytes = config.MAX_FILE_SIZE_MB * 1024 * 1024
            if file_size > max_file_size_bytes:
                await callback.answer("❌ File too large")
                return
        except OSError as e:
            logging.error(f"Error checking file size: {e}")
            await callback.answer("❌ File access error")
            return
            
        # Check callback.message availability
        if not callback.message:
            await callback.answer("❌ Message unavailable")
            return
            
        # Send selected file with error handling
        try:
            if not callback.message:
                await callback.answer("❌ Message unavailable")
                return
                
            await send_file_with_retry(callback.message, file_path)
            await callback.answer("✅ File sent")
            logging.info(f"Successfully sent file: {file_path}")
        except Exception as send_error:
            logging.error(f"Error sending file: {send_error}")
            try:
                await callback.answer("❌ Error sending file. Try again later.")
            except Exception:
                pass  # If even callback.answer doesn't work
            return
        
        # Remove keyboard (with message availability check)
        await remove_keyboard(callback.message)
        
    except Exception as e:
        logging.error(f"Error in file selection handler: {str(e)}")
        await send_callback_answer(callback, "❌ An error occurred")

@router.callback_query(F.data.startswith("link_"))
async def link_selection_callback(callback: CallbackQuery, faq_loader: Any) -> None:
    """Link selection handler"""
    try:
        # Check for callback.data presence
        if not callback.data:
            await callback.answer("❌ Invalid data")
            return
            
        # Parse callback_data: link_{index}
        parts = callback.data.split("_")
        if len(parts) < 2:
            await callback.answer("❌ Invalid data format")
            return
            
        index = int(parts[1])
        
        if not faq_loader.faq or index >= len(faq_loader.faq):
            await callback.answer("❌ Invalid index")
            return
            
        match = faq_loader.faq[index]
        
        if 'link' not in match:
            await callback.answer("❌ Link not found")
            return
            
        # Check callback.message availability
        if not callback.message:
            await callback.answer("❌ Message unavailable")
            return
            
        # Send link with error handling
        try:
            await callback.message.answer(match['link'])
            await callback.answer("✅ Link sent")
        except Exception as send_error:
            logging.error(f"Error sending link: {send_error}")
            try:
                await callback.answer("❌ Error sending link")
            except Exception:
                pass  # If even callback.answer doesn't work
            return
        
        # Remove keyboard (with message availability check)
        await remove_keyboard(callback.message)
        
    except Exception as e:
        logging.error(f"Error in link selection handler: {str(e)}")
        await send_callback_answer(callback, "❌ An error occurred")

@router.callback_query(F.data.startswith("tv_year_"))
async def tv_year_selection_callback(callback: CallbackQuery, db: Any, config: Any, faq_loader: Any) -> None:
    """TV summary table year selection handler"""
    try:
        # Check for callback.data presence
        if not callback.data:
            await callback.answer("❌ Invalid data")
            return
            
        # Parse year from callback_data
        year = callback.data.split("_")[-1]
        
        if year not in ["2024", "2025"]:
            await callback.answer("❌ Invalid year")
            return
        
        # Check callback.message availability
        if not callback.message:
            await callback.answer("❌ Message unavailable")
            return
        
        # Search for corresponding entry in FAQ
        if not faq_loader.faq:
            await callback.answer("❌ Data not loaded")
            return
        
        # Find entry by year
        target_query = f"Сводная таблица ТВ {year}"
        target_index = None
        
        for i, item in enumerate(faq_loader.faq):
            if item.get("query") == target_query:
                target_index = i
                break
        
        if target_index is None:
            await callback.answer("❌ Entry not found")
            logging.error(f"Entry not found for query: {target_query}")
            return
        
        match = faq_loader.faq[target_index]
        
        # Send response
        await callback.message.answer(match['response'])
        
        # Send file
        if 'resources' in match and match['resources']:
            resource = match['resources'][0]  # Take first resource
            if resource.get('type') == 'file':
                files = resource.get('files', [])
                if files:
                    file_path = files[0]  # Take first file
                    
                    # Check if file exists before attempting to send
                    if not os.path.exists(file_path):
                        error_msg = f"❌ File not found: {file_path}. Please contact the administrator."
                        await callback.answer(error_msg)
                        logging.error(f"File not found: {file_path} for query: {target_query}")
                        await callback.message.answer("Sorry, the file for 'Сводное 2025 года' is not available. Contact the admin.")
                        return
                    
                    # Check file size
                    try:
                        file_size = os.path.getsize(file_path)
                        max_file_size_bytes = config.MAX_FILE_SIZE_MB * 1024 * 1024
                        if file_size > max_file_size_bytes:
                            await callback.answer("❌ File too large")
                            return
                    except OSError as e:
                        logging.error(f"Error checking file size: {e}")
                        await callback.answer("❌ File access error")
                        return
                    
                    # Send file
                    try:
                        await send_file_with_retry(callback.message, file_path)
                        await callback.answer("✅ File sent")
                        logging.info(f"Successfully sent file: {file_path}")
                    except Exception as send_error:
                        logging.error(f"Error sending file: {send_error}")
                        await callback.answer("❌ Error sending file. Please try again later.")
                        await callback.message.answer("Sorry, there was an error sending the file. Please try again later.")
                        return
                else:
                    await callback.answer("❌ No files found for this resource")
                    logging.warning(f"No files found for resource in query: {target_query}")
                    return
            else:
                await callback.answer("❌ Invalid resource type")
                logging.warning(f"Invalid resource type for query: {target_query}")
                return
        else:
            await callback.answer("❌ No resources found")
            logging.warning(f"No resources found for query: {target_query}")
            return
        
        # Remove keyboard
        await remove_keyboard(callback.message)
        
    except Exception as e:
        logging.error(f"Error in TV year selection handler: {str(e)}")
        await send_callback_answer(callback, "❌ An error occurred")

@router.callback_query(F.data.startswith("soundbar_year_"))
async def soundbar_year_selection_callback(callback: CallbackQuery, db: Any, config: Any, faq_loader: Any) -> None:
    """Soundbar summary table year selection handler"""
    try:
        # Check for callback.data presence
        if not callback.data:
            await callback.answer("❌ Invalid data")
            return
            
        # Parse year from callback_data
        year = callback.data.split("_")[-1]
        
        if year not in ["2024", "2025"]:
            await callback.answer("❌ Invalid year")
            return
        
        # Check callback.message availability
        if not callback.message:
            await callback.answer("❌ Message unavailable")
            return
        
        # Search for corresponding entry in FAQ
        if not faq_loader.faq:
            await callback.answer("❌ Data not loaded")
            return
        
        # Find entry by year
        target_query = f"Сводная саундбар {year}"
        target_index = None
        
        for i, item in enumerate(faq_loader.faq):
            if item.get("query") == target_query:
                target_index = i
                break
        
        if target_index is None:
            await callback.answer("❌ Entry not found")
            logging.error(f"Entry not found for query: {target_query}")
            return
        
        match = faq_loader.faq[target_index]
        
        # Send response
        await callback.message.answer(match['response'])
        
        # Send file
        if 'resources' in match and match['resources']:
            resource = match['resources'][0]  # Take first resource
            if resource.get('type') == 'file':
                files = resource.get('files', [])
                if files:
                    file_path = files[0]  # Take first file
                    
                    # Check if file exists before attempting to send
                    if not os.path.exists(file_path):
                        error_msg = f"❌ File not found: {file_path}. Please contact the administrator."
                        await callback.answer(error_msg)
                        logging.error(f"File not found: {file_path} for query: {target_query}")
                        await callback.message.answer("Sorry, the file is not available. Contact the admin.")
                        return
                    
                    # Check file size
                    try:
                        file_size = os.path.getsize(file_path)
                        max_file_size_bytes = config.MAX_FILE_SIZE_MB * 1024 * 1024
                        if file_size > max_file_size_bytes:
                            await callback.answer("❌ File too large")
                            return
                    except OSError as e:
                        logging.error(f"Error checking file size: {e}")
                        await callback.answer("❌ File access error")
                        return
                    
                    # Send file
                    try:
                        await send_file_with_retry(callback.message, file_path)
                        await callback.answer("✅ File sent")
                        logging.info(f"Successfully sent file: {file_path}")
                    except Exception as send_error:
                        logging.error(f"Error sending file: {send_error}")
                        await callback.answer("❌ Error sending file")
                        await callback.message.answer("Sorry, there was an error sending the file. Please try again later.")
                        return
                else:
                    await callback.answer("❌ No files found for this resource")
                    logging.warning(f"No files found for resource in query: {target_query}")
                    return
            else:
                await callback.answer("❌ Invalid resource type")
                logging.warning(f"Invalid resource type for query: {target_query}")
                return
        else:
            await callback.answer("❌ No resources found")
            logging.warning(f"No resources found for query: {target_query}")
            return
        
        # Remove keyboard
        await remove_keyboard(callback.message)
        
    except Exception as e:
        logging.error(f"Error in soundbar year selection handler: {str(e)}")
        await send_callback_answer(callback, "❌ An error occurred")

@router.callback_query(F.data.startswith("resource_"))
async def resource_selection_callback(callback: CallbackQuery, faq_loader: Any, db: Any, config: Any) -> None:
    """Resource selection handler"""
    try:
        # Check for callback.data presence
        if not callback.data:
            await callback.answer("❌ Invalid data")
            return
            
        # Parse callback_data: resource_{index}_{resource_index}
        parts = callback.data.split("_")
        if len(parts) < 3:
            await callback.answer("❌ Invalid data format")
            return
            
        index = int(parts[1])
        resource_index = int(parts[2])
        
        if not faq_loader.faq or index >= len(faq_loader.faq):
            await callback.answer("❌ Invalid index")
            return
            
        match = faq_loader.faq[index]
        
        if 'resources' not in match or resource_index >= len(match['resources']):
            await callback.answer("❌ Resource not found")
            return
            
        resource = match['resources'][resource_index]
        
        # Check callback.message availability
        if not callback.message:
            await callback.answer("❌ Message unavailable")
            return
        
        # Handle different resource types
        if resource.get('type') == 'file':
            # Send files
            files = resource.get('files', [])
            if not files:
                await callback.answer("❌ Files not found")
                return
            
            sent_files = await send_resource_files(callback.message, files)
            
            # Send additional text if present
            if 'additional_text' in resource:
                try:
                    await callback.message.answer(resource['additional_text'])
                except Exception as text_error:
                    logging.error(f"Error sending text: {text_error}")
            
            if sent_files:
                try:
                    await callback.answer(f"✅ Sent: {', '.join(sent_files)}")
                except Exception:
                    pass
            else:
                try:
                    await callback.answer("❌ Failed to send files")
                except Exception:
                    pass
                    
        elif resource.get('type') == 'link':
            # Send link
            link = resource.get('link')
            if not link:
                await callback.answer("❌ Link not found")
                return
                
            try:
                await callback.message.answer(link)
                await callback.answer("✅ Link sent")
            except Exception as send_error:
                logging.error(f"Error sending link: {send_error}")
                try:
                    await callback.answer("❌ Error sending link")
                except Exception:
                    pass
                return
        
        # Remove keyboard
        await remove_keyboard(callback.message)
        
    except Exception as e:
        logging.error(f"Error in resource selection handler: {str(e)}")
        await send_callback_answer(callback, "❌ An error occurred")

@router.callback_query(F.data == "cancel")
async def cancel_selection_callback(callback: CallbackQuery, db: Any, config: Any) -> None:
    """Selection cancellation handler"""
    try:
        if callback.message and hasattr(callback.message, 'edit_text') and not isinstance(callback.message, types.InaccessibleMessage):
            await callback.message.edit_text("❌ Selection cancelled")
        else:
            # If we can't edit the message, just respond
            await callback.answer("❌ Selection cancelled")
            return
    except Exception as e:
        logging.warning(f"Failed to edit message: {e}")
        await callback.answer("❌ Selection cancelled")
        return
        
    await callback.answer()

@router.callback_query(F.data == "vsk_pamytka")
async def vsk_pamytka_callback(callback: CallbackQuery, db: Any, config: Any) -> None:
    """VSK memo selection handler"""
    try:
        # Check callback.message availability
        if not callback.message:
            await callback.answer("❌ Message unavailable")
            return
        
        # Send memo file
        file_path = config.VSK_MEMO_PATH
        
        if os.path.exists(file_path):
            # Check file size
            try:
                file_size = os.path.getsize(file_path)
                max_file_size_bytes = config.MAX_FILE_SIZE_MB * 1024 * 1024
                if file_size > max_file_size_bytes:
                    await callback.answer("❌ File too large")
                    return
            except OSError as e:
                logging.error(f"Error checking file size: {e}")
                await callback.answer("❌ File access error")
                return
            
            # Send file
            try:
                await send_file_with_retry(callback.message, file_path)
                await callback.answer("✅ File sent")
                logging.info(f"Successfully sent file: {file_path}")
            except Exception as send_error:
                logging.error(f"Error sending file: {send_error}")
                await callback.answer("❌ Error sending file")
                return
        else:
            await callback.answer("❌ File not found")
            return
            
        # Remove keyboard
        await remove_keyboard(callback.message)
        
    except Exception as e:
        logging.error(f"Error in VSK memo selection handler: {str(e)}")
        await send_callback_answer(callback, "❌ An error occurred")

@router.callback_query(F.data == "vsk_zayavlenie")
async def vsk_zayavlenie_callback(callback: CallbackQuery, db: Any, config: Any) -> None:
    """VSK claim form selection handler"""
    try:
        # Check callback.message availability
        if not callback.message:
            await callback.answer("❌ Message unavailable")
            return
        
        # Send claim form files
        files_to_send = [
            config.VSK_CLAIM_FORM_DOCX,
            config.VSK_CLAIM_FORM_XLSX
        ]
        
        sent_files = await send_resource_files(callback.message, files_to_send)
        
        # Send additional text
        additional_text = (
            "What documents are needed to accept a device for insurance in 1C:\n"
            "- Insurance claim form (Templates + instructions above)\n"
            "- Copy of passport (Main page + registration)\n"
            "- Copy/original of Receipt\n"
            "- Insurance contract"
        )
        
        try:
            await callback.message.answer(additional_text)
        except Exception as text_error:
            logging.error(f"Error sending text: {text_error}")
        
        if sent_files:
            await callback.answer(f"✅ Sent: {', '.join(sent_files)}")
        else:
            await callback.answer("❌ Failed to send files")
        
        # Remove keyboard
        await remove_keyboard(callback.message)
        
    except Exception as e:
        logging.error(f"Error in VSK claim form selection handler: {str(e)}")
        await send_callback_answer(callback, "❌ An error occurred")

@router.callback_query(F.data == "summary_tv")
async def summary_tv_callback(callback: CallbackQuery, db: Any, config: Any) -> None:
    """TV summary table selection handler"""
    try:
        # Check callback.message availability
        if not callback.message:
            await callback.answer("❌ Message unavailable")
            return
        
        # Create keyboard with year selection for TV
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📺 TV 2024", callback_data="tv_year_2024")],
            [InlineKeyboardButton(text="📺 TV 2025", callback_data="tv_year_2025")],
            [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")]
        ])
        
        # Check if message is available for editing
        if hasattr(callback.message, 'edit_text') and not isinstance(callback.message, types.InaccessibleMessage):
            await callback.message.edit_text("Select TV summary table year:", reply_markup=keyboard)
        else:
            # If we can't edit the message, send a new one
            await callback.message.answer("Select TV summary table year:", reply_markup=keyboard)
        await callback.answer()
        
    except Exception as e:
        logging.error(f"Error in TV summary table selection handler: {str(e)}")
        await send_callback_answer(callback, "❌ An error occurred")

@router.callback_query(F.data == "summary_soundbar")
async def summary_soundbar_callback(callback: CallbackQuery, db: Any, config: Any) -> None:
    """Soundbar summary table selection handler"""
    try:
        # Check callback.message availability
        if not callback.message:
            await callback.answer("❌ Message unavailable")
            return
        
        # Create keyboard with year selection for soundbar
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎵 Soundbar 2024", callback_data="soundbar_year_2024")],
            [InlineKeyboardButton(text="🎵 Soundbar 2025", callback_data="soundbar_year_2025")],
            [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")]
        ])
        
        # Check if message is available for editing
        if hasattr(callback.message, 'edit_text') and not isinstance(callback.message, types.InaccessibleMessage):
            await callback.message.edit_text("Select soundbar summary table year:", reply_markup=keyboard)
        else:
            # If we can't edit the message, send a new one
            await callback.message.answer("Select soundbar summary table year:", reply_markup=keyboard)
        await callback.answer()
        
    except Exception as e:
        logging.error(f"Error in soundbar summary table selection handler: {str(e)}")
        await send_callback_answer(callback, "❌ An error occurred")

@router.message(CommandStart())
async def start_handler(message: Message, db: Any, config: Any) -> None:
    """/start command handler with authentication"""
    if not message.from_user:
        return
        
    user_id = message.from_user.id
    chat_id = message.chat.id if message.chat else None
    message_id = message.message_id
    
    # Custom logging with required fields
    import logging
    logging.getLogger().info(
        "Start command received",
        extra={
            'user_id': user_id,
            'chat_id': chat_id,
            'message_id': message_id,
            'handler': 'start_handler'
        }
    )
    
    # Check authentication
    if check_authentication(message, db, config):
        await message.answer(
            "🎉 Привет! Я FAQ-бот помощник для сотрудников.\n"
            "📝 Задай вопрос, и я найду нужную информацию."
        )
    else:
        # User is not authenticated
        waiting_for_password.add(user_id)
        await message.answer(
            "🔒 Для доступа к боту требуется аутентификация.\n"
            "📝 Введи пароль для доступа:"
        )

@router.message(Command("help"))
async def help_handler(message: Message, db: Any, config: Any) -> None:
    """/help command handler with authentication check"""
    if not message.from_user:
        return
    
    user_id = message.from_user.id
    chat_id = message.chat.id if message.chat else None
    message_id = message.message_id
    
    # Custom logging with required fields
    import logging
    logging.getLogger().info(
        "Help command received",
        extra={
            'user_id': user_id,
            'chat_id': chat_id,
            'message_id': message_id,
            'handler': 'help_handler'
        }
    )
    
    # Check authentication
    if not check_authentication(message, db, config):
        await message.answer(
            "🔒 To access the bot, run the /start command and enter the password."
        )
        return
    
    help_text = (
        "🤖 <b>FAQ Bot Commands</b>\n\n"
        "/start - Start the bot and authenticate\n"
        "/help - Show this help message\n"
        "/stats - Show usage statistics\n"
        "/export_stats - Export detailed statistics\n"
        "/clear_stats - Clear statistics (admin only)\n"
        "/access - Manage user access (admin only)\n\n"
        "📝 Simply send a question in natural language and I'll find the most relevant answer for you."
    )
    
    await message.answer(help_text, parse_mode='HTML')

@router.message(Command("stats"))
async def stats_handler(message: Message, db: Any, config: Any) -> None:
    """Command to show statistics"""
    if not message.from_user:
        return
    
    user_id = message.from_user.id
    chat_id = message.chat.id if message.chat else None
    message_id = message.message_id
    
    # Custom logging with required fields
    import logging
    logging.getLogger().info(
        "Stats command received",
        extra={
            'user_id': user_id,
            'chat_id': chat_id,
            'message_id': message_id,
            'handler': 'stats_handler'
        }
    )
    
    # Check authentication
    if not check_authentication(message, db, config):
        await message.answer(
            "🔒 To access the bot, run the /start command and enter the password."
        )
        return
    
    try:
        stats = db.get_stats()
        
        # Format similarity score distribution
        similarity_distribution = ""
        if stats.similarity_score_distribution:
            similarity_distribution = "\n📊 <b>Similarity Score Distribution:</b>\n"
            for range_name, count in sorted(stats.similarity_score_distribution.items(), 
                                           key=lambda x: x[0], reverse=True):
                similarity_distribution += f"  {range_name}: {count} queries\n"
        
        # Format popular queries
        popular_queries = ""
        if stats.popular_queries:
            popular_queries = "\n🔥 <b>Top 10 Popular Queries:</b>\n"
            for i, (query, count) in enumerate(stats.popular_queries, 1):
                popular_queries += f"  {i}. {query} ({count} times)\n"
        
        stats_message = (
            f"📈 <b>Bot Statistics</b>\n\n"
            f"Total queries: <b>{stats.total_queries}</b>\n"
            f"Success rate: <b>{stats.success_rate:.2f}%</b>\n"
            f"Unanswered questions: <b>{stats.unanswered_questions}</b>\n"
            f"Bad words detected: <b>{stats.bad_words_count}</b>\n"
            f"Authenticated users: <b>{stats.authenticated_users_count}</b>\n"
            f"Average response time: <b>{stats.avg_response_time:.2f} ms</b>\n"
            f"Cache hit rate: <b>{stats.cache_hit_rate:.2f}%</b>\n"
            f"Average query length: <b>{stats.avg_query_length:.2f} characters</b>\n"
            f"{similarity_distribution}"
            f"{popular_queries}"
        )
        
        await message.answer(stats_message, parse_mode='HTML')
        
    except Exception as e:
        logging.error(f"Error getting stats: {str(e)}")
        await message.answer("⚠️ An error occurred while retrieving statistics.")

@router.message(Command("export_stats"))
async def export_stats_handler(message: Message, db: Any, config: Any) -> None:
    """Command to export statistics"""
    if not message.from_user:
        return
    
    user_id = message.from_user.id
    chat_id = message.chat.id if message.chat else None
    message_id = message.message_id
    
    # Custom logging with required fields
    import logging
    logging.getLogger().info(
        "Export stats command received",
        extra={
            'user_id': user_id,
            'chat_id': chat_id,
            'message_id': message_id,
            'handler': 'export_stats_handler'
        }
    )
    
    # Check authentication
    if not check_authentication(message, db, config):
        await message.answer(
            "🔒 To access the bot, run the /start command and enter the password."
        )
        return
    
    try:
        filename = db.export_stats_to_file()
        if filename and os.path.exists(filename):
            # Send file
            try:
                await message.answer_document(types.FSInputFile(filename))
                # Clean up the file after sending
                os.remove(filename)
            except Exception as e:
                logging.error(f"Error sending stats file: {str(e)}")
                await message.answer("⚠️ An error occurred while sending the statistics file.")
        else:
            await message.answer("⚠️ Failed to export statistics.")
            
    except Exception as e:
        logging.error(f"Error exporting stats: {str(e)}")
        await message.answer("⚠️ An error occurred while exporting statistics.")

@router.message(Command("access"))
async def access_handler(
    message: Message, 
    db: Any,
    config: Any
) -> None:
    """Command to manage user access (admin only)"""
    if not message.from_user:
        return
    
    user_id = message.from_user.id
    chat_id = message.chat.id if message.chat else None
    message_id = message.message_id
    
    # Custom logging with required fields
    import logging
    logging.getLogger().info(
        "Access command received",
        extra={
            'user_id': user_id,
            'chat_id': chat_id,
            'message_id': message_id,
            'handler': 'access_handler'
        }
    )
    
    # Check authentication and admin rights
    if not check_authentication(message, db, config):
        await message.answer(
            "🔒 To access the bot, run the /start command and enter the password."
        )
        return
    
    if message.from_user.id != config.ADMIN_ID:
        await message.answer("⛔ У тебя нет прав на эту команду.")
        return

    try:
        auth_count = db.get_authenticated_users_count()
        await message.answer(
            f"🔒 <b>Управление доступом</b>\n\n"
            f"👥 Всего пользователей с доступом: <b>{auth_count}</b>\n\n"
            f"📋 Чтобы посмотреть полный список, используй команду /export_stats",
            parse_mode='HTML'
        )
        
    except Exception as e:
        logging.error(f"Error getting user list: {str(e)}")
        await message.answer("⚠️ При получении списка пользователей произошла ошибка.")

@router.message(Command("clear_stats"))
async def clear_stats_handler(
    message: Message, 
    db: Any,
    config: Any
) -> None:
    """Command to clear statistics (admin only)"""
    if not message.from_user:
        return
    
    user_id = message.from_user.id
    chat_id = message.chat.id if message.chat else None
    message_id = message.message_id
    
    # Custom logging with required fields
    import logging
    logging.getLogger().info(
        "Clear stats command received",
        extra={
            'user_id': user_id,
            'chat_id': chat_id,
            'message_id': message_id,
            'handler': 'clear_stats_handler'
        }
    )
    
    # Check authentication and admin rights
    if not check_authentication(message, db, config):
        await message.answer(
            "🔒 To access the bot, run the /start command and enter the password."
        )
        return
    
    if message.from_user.id != config.ADMIN_ID:
        await message.answer("⛔ У тебя нет прав на эту команду.")
        return
    
    # Create confirmation keyboard
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Confirm", callback_data="clear_stats_confirm")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="clear_stats_cancel")]
    ])
    
    await message.answer(
        "⚠️ <b>Обнуление статистики</b>\n\n"
        "Все файлы логов будут заархивированы, а статистика начнётся заново.\n"
        "Ты точно хочешь продолжить?",
        parse_mode='HTML',
        reply_markup=keyboard
    )

@router.callback_query(F.data == "clear_stats_confirm")
async def clear_stats_confirm_callback(callback: CallbackQuery, db: Any, config: Any) -> None:
    """Callback handler for confirming stats clearing"""
    # Check authentication and admin rights
    if not callback.from_user or callback.from_user.id != config.ADMIN_ID:
        await callback.answer("⛔ You don't have permission to execute this command.", show_alert=True)
        return
    
    try:
        # Archive log files
        from pathlib import Path
        import shutil
        from datetime import datetime
        
        # Setup logging for stats clearing
        logs_dir = Path("logs")
        if not logs_dir.exists():
            await callback.answer("❌ Logs directory not found", show_alert=True)
            return
        
        # Create archive directory
        archive_dir = logs_dir / "archive" / datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all log files (main log and backups)
        log_files = list(logs_dir.glob("bot.log*"))
        
        if not log_files:
            await callback.message.edit_text("✅ No log files found to clear. Statistics are already clean!")
            await callback.answer("No log files found")
            return
        
        # Archive each log file
        archived_files = []
        for log_file in log_files:
            try:
                destination = archive_dir / log_file.name
                shutil.move(str(log_file), str(destination))
                archived_files.append(log_file.name)
            except Exception as e:
                logging.error(f"Error archiving {log_file.name}: {e}")
        
        # Update message with success information
        success_message = (
            "✅ <b>Statistics Cleared Successfully!</b>\n\n"
            f"Archived {len(archived_files)} log files to:\n"
            f"<code>{archive_dir.relative_to(logs_dir.parent)}</code>\n\n"
            "New statistics will start from now."
        )
        
        await callback.message.edit_text(success_message, parse_mode='HTML')
        await callback.answer("Statistics cleared successfully!")
        
        # Log the action
        logging.info(f"Statistics cleared by user {callback.from_user.id}. Archived {len(archived_files)} files to {archive_dir}")
        
    except Exception as e:
        logging.error(f"Error clearing statistics: {str(e)}")
        await callback.message.edit_text("❌ An error occurred while clearing statistics. Please check the logs.")
        await callback.answer("Error clearing statistics", show_alert=True)

@router.callback_query(F.data == "clear_stats_cancel")
async def clear_stats_cancel_callback(callback: CallbackQuery, db: Any, config: Any) -> None:
    """Callback handler for canceling stats clearing"""
    # Check authentication and admin rights
    if not callback.from_user or callback.from_user.id != config.ADMIN_ID:
        await callback.answer("⛔ You don't have permission to execute this command.", show_alert=True)
        return
    
    await callback.message.edit_text("❌ Statistics clearing cancelled.")
    await callback.answer("Cancelled")

# Handler for special "TV Summary" request
@router.message(F.text.func(lambda text: text and "сводная" in text.lower() and "тв" in text.lower()))
async def tv_summary_handler(
    message: Message, 
    db: Any,
    config: Any
) -> None:
    """Handler for "TV Summary" requests - shows year selection buttons"""
    if not message.text or not (text := message.text.strip()):
        return
    
    if not message.from_user:
        return
    
    # Check authentication
    if not check_authentication(message, db, config):
        await message.answer(
            "🔒 To access the bot, run the /start command and enter the password."
        )
        return
    
    # Create keyboard with year selection
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📺 TV 2024", callback_data="tv_year_2024")],
        [InlineKeyboardButton(text="📺 TV 2025", callback_data="tv_year_2025")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")]
    ])
    
    await message.answer("Select TV summary table year:", reply_markup=keyboard)

# Handler for special "Soundbar Summary" request
@router.message(F.text.func(lambda text: text and "сводная" in text.lower() and "саундбар" in text.lower()))
async def soundbar_summary_handler(
    message: Message, 
    db: Any,
    config: Any
) -> None:
    """Handler for "Soundbar Summary" requests - shows year selection buttons"""
    if not message.text or not (text := message.text.strip()):
        return
    
    if not message.from_user:
        return
    
    # Check authentication
    if not check_authentication(message, db, config):
        await message.answer(
            "🔒 Для доступа к боту выполните команду /start и введите пароль."
        )
        return
    
    # Create keyboard with year selection
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎵 Саундбар 2024", callback_data="soundbar_year_2024")],
        [InlineKeyboardButton(text="🎵 Саундбар 2025", callback_data="soundbar_year_2025")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
    ])
    
    await message.answer("Выберите год сводной таблицы саундбаров:", reply_markup=keyboard)

# Handler for special "VSK" request
@router.message(F.text.func(lambda text: text and "вск" in text.lower()))
async def vsk_handler(
    message: Message, 
    db: Any,
    config: Any
) -> None:
    """Handler for "VSK" requests - shows document selection buttons"""
    if not message.text or not (text := message.text.strip()):
        return
    
    if not message.from_user:
        return
    
    # Check authentication
    if not check_authentication(message, db, config):
        await message.answer(
            "🔒 To access the bot, run the /start command and enter the password."
        )
        return
    
    # Create keyboard with document selection
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 VSK Product Memo", callback_data="vsk_pamytka")],
        [InlineKeyboardButton(text="📄 VSK Insurance Claim Form", callback_data="vsk_zayavlenie")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")]
    ])
    
    await message.answer("Select the required VSK insurance document:", reply_markup=keyboard)

# Handler for special "Summary" request - shows selection between TV and soundbar
@router.message(F.text.func(lambda text: text and "сводная" in text.lower() and "тв" not in text.lower() and "саундбар" not in text.lower()))
async def summary_choice_handler(
    message: Message, 
    db: Any,
    config: Any
) -> None:
    """Handler for "Summary" requests - shows selection buttons between TV and soundbar"""
    if not message.text or not (text := message.text.strip()):
        return
    
    if not message.from_user:
        return
    
    # Check authentication
    if not check_authentication(message, db, config):
        await message.answer(
            "🔒 To access the bot, run the /start command and enter the password."
        )
        return
    
    # Create keyboard with selection between TV and soundbar
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📺 TV Summary", callback_data="summary_tv")],
        [InlineKeyboardButton(text="🎵 Soundbar Summary", callback_data="summary_soundbar")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")]
    ])
    
    await message.answer("Select summary table type:", reply_markup=keyboard)

# Handler for special "Checklist", "Check list", "Verification" request
@router.message(F.text.func(lambda text: text and any(keyword in text.lower() for keyword in ["чек-лист", "чек лист", "проверка"])))
async def checklist_handler(
    message: Message, 
    db: Any,
    config: Any,
    faq_loader: Any
) -> None:
    """Handler for "Checklist", "Check list", "Verification" requests - shows selection buttons"""
    if not message.text or not (text := message.text.strip()):
        return
    
    if not message.from_user:
        return
    
    # Check authentication
    if not check_authentication(message, db, config):
        await message.answer(
            "🔒 To access the bot, run the /start command and enter the password."
        )
        return
    
    # Search for "Checklist" entry in FAQ
    if not faq_loader.faq:
        await message.answer("❌ Data not loaded")
        return
    
    target_query = "Checklist"
    target_index = None
    
    for i, item in enumerate(faq_loader.faq):
        if item.get("query") == target_query:
            target_index = i
            break
    
    if target_index is None:
        await message.answer("❌ Entry not found")
        return
    
    match = faq_loader.faq[target_index]
    
    # Send response
    await message.answer(match['response'])
    
    # Check for resources
    if 'resources' in match and match['resources']:
        # For the second resource (ROPA Checklist), check auto_send
        if len(match['resources']) >= 2:
            second_resource = match['resources'][1]
            if second_resource.get('auto_send') is True:
                # Automatically send the second resource
                success = await auto_send_single_resource(message, second_resource)
                if success:
                    # Show keyboard only for the first resource
                    if len(match['resources']) >= 1:
                        # Create keyboard only with the first resource
                        keyboard = create_resource_selection_keyboard({'resources': [match['resources'][0]]}, target_index)
                        await message.answer("👆 Select the required resource:", reply_markup=keyboard)
                    return
        
        # If no auto_send or sending failed, show all resources
        keyboard = create_resource_selection_keyboard(match, target_index)
        await message.answer("👆 Select the required resource:", reply_markup=keyboard)
    else:
        # If no resources, show message
        await message.answer("❌ No resources available")

# Handler for special "Scanner", "Scanner Connection", "Netum" request
@router.message(F.text.func(lambda text: text and any(keyword in text.lower() for keyword in ["сканер", "подключение сканеров", "netum"])))
async def scanner_handler(
    message: Message, 
    db: Any,
    config: Any,
    faq_loader: Any
) -> None:
    """Handler for "Scanner", "Scanner Connection", "Netum" requests - automatically sends files"""
    if not message.text or not (text := message.text.strip()):
        return
    
    if not message.from_user:
        return
    
    # Check authentication
    if not check_authentication(message, db, config):
        await message.answer(
            "🔒 To access the bot, run the /start command and enter the password."
        )
        return
    
    # Search for "Scanner" entry in FAQ
    if not faq_loader.faq:
        await message.answer("❌ Data not loaded")
        return
    
    target_query = "Scanner"
    target_index = None
    
    for i, item in enumerate(faq_loader.faq):
        if item.get("query") == target_query:
            target_index = i
            break
    
    if target_index is None:
        await message.answer("❌ Entry not found")
        return
    
    match = faq_loader.faq[target_index]
    
    # Send response
    await message.answer(match['response'])
    
    # Check for resources
    if 'resources' in match and match['resources']:
        # Determine if automatic sending is needed
        should_auto, single_resource = should_auto_send_resource(match['resources'])
        
        if should_auto and single_resource:
            # Automatically send the single resource
            success = await auto_send_single_resource(message, single_resource)
            if not success:
                await message.answer("❌ Failed to send files. Contact the administrator.")
        else:
            # Show keyboard for selection
            keyboard = create_resource_selection_keyboard(match, target_index)
            await message.answer("👆 Select the required resource:", reply_markup=keyboard)

# This handler must be LAST, as it catches all text messages
@router.message(F.text)
async def message_handler(
    message: Message, 
    db: Any,
    faq_loader: Any,
    config: Any
) -> None:
    if not message.text or not (text := message.text.strip()):
        await message.answer("Please send a text question.")
        return
    
    if not message.from_user:
        return
        
    user_id = message.from_user.id
    chat_id = message.chat.id if message.chat else None
    message_id = message.message_id
    
    # Record start time for response time measurement
    import time
    start_time = time.time()
    
    # Custom logging with required fields
    import logging
    logging.getLogger().info(
        f"User message received: {text[:50]}...",
        extra={
            'user_id': user_id,
            'chat_id': chat_id,
            'message_id': message_id,
            'handler': 'message_handler',
            'query_length': len(text)
        }
    )
    
    # Check if user is waiting for password input
    if user_id in waiting_for_password:
        if text == config.ACCESS_PASSWORD:
            # Correct password - authenticate user
            waiting_for_password.discard(user_id)
            db.authenticate_user(message.from_user)
            await message.answer(
                "✅ Authentication successful!\n"
                "🎉 Welcome to the FAQ bot for employees!\n"
                "📝 Now you can ask questions."
            )
            logging.info(f"User {user_id} ({message.from_user.first_name}) successfully authenticated")
            return
        else:
            # Incorrect password
            await message.answer(
                "❌ Incorrect password!\n"
                "🔒 Try again or contact the administrator."
            )
            logging.warning(f"User {user_id} entered an incorrect password: {text}")
            return
    
    # Check authentication before processing the request
    if not check_authentication(message, db, config):
        await message.answer(
            "🔒 To access the bot, run the /start command and enter the password."
        )
        return

    # Check for blocked words
    if any(bad_word in text.lower() for bad_word in config.BLOCKED_WORDS):
        await message.answer("❌ Your message contains prohibited words.")
        user_id = message.from_user.id if message.from_user else "unknown"
        logging.warning(f"User {user_id} sent a prohibited message: {text}")
        if message.from_user:
            db.log_bad_word(message.from_user, text)
        return

    # Search for answer in FAQ
    distances, indices = faq_loader.search(text, threshold=config.SIMILARITY_THRESHOLD)
    
    # Calculate response time
    response_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
    
    if not distances or not indices:
        logging.info(f"No matches found for query: '{text}'")
        await message.answer("Did not find a suitable answer. Specify your query.")
        db.log_query(text, success=False, user_id=user_id, query_length=len(text), response_time_ms=response_time)
        db.log_unanswered_question(text, user_id)
        return

    similarity = distances[0]
    index = indices[0]
    match = faq_loader.faq[index]
    
    # Check if result is from cache
    is_cache_hit = getattr(faq_loader, '_last_search_cached', False)
    
    # Send main answer
    await message.answer(match['response'])

    # Check for resources
    if 'resources' in match and match['resources']:
        # Determine if automatic sending is needed
        should_auto, single_resource = should_auto_send_resource(match['resources'])
        
        if should_auto and single_resource:
            # Automatically send the single resource
            success = await auto_send_single_resource(message, single_resource)
            if not success:
                # If auto-sending failed, show the keyboard
                keyboard = create_resource_selection_keyboard(match, index)
                await message.answer("👆 Select the required resource:", reply_markup=keyboard)
        else:
            # Show keyboard for selection (multiple resources or multiple files)
            keyboard = create_resource_selection_keyboard(match, index)
            await message.answer("👆 Select the required resource:", reply_markup=keyboard)
    
    # Log result with detailed metrics
    db.log_query(
        text, 
        success=True, 
        user_id=user_id,
        similarity_score=float(similarity),
        response_time_ms=response_time,
        cache_hit=is_cache_hit,
        query_length=len(text)
    )
    
    # Detailed logging for analytics
    logging.getLogger().info(
        f"Query processed successfully: {text[:50]}...",
        extra={
            'user_id': user_id,
            'query_similarity': float(similarity),
            'response_time': response_time,
            'cache_hit': is_cache_hit,
            'handler': 'message_handler_result'
        }
    )