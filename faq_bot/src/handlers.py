import logging
import os
from aiogram import types, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramRetryAfter, TelegramNetworkError
from aiogram.filters import Command, CommandStart

from utils import send_file_with_retry, remove_keyboard, send_callback_answer

router = Router()

# Dictionary to track users waiting for authentication
waiting_for_password = set()

def check_authentication(message: Message, db, config) -> bool:
    """Check if user is authenticated"""
    if not message.from_user:
        return False
    
    user_id = message.from_user.id
    
    # Check if user is admin (admin doesn't need authentication)
    if user_id == config.ADMIN_ID:
        return True
    
    # Check in database
    return db.is_user_authenticated(user_id)

def check_authentication_for_callback(callback: CallbackQuery, db, config) -> bool:
    """Check authentication for callback query"""
    if not callback.from_user:
        return False
    
    user_id = callback.from_user.id
    
    # Check if user is admin
    if user_id == config.ADMIN_ID:
        return True
    
    # Check in database
    return db.is_user_authenticated(user_id)

# retry_file_operation function moved to utils.py

async def auto_send_single_resource(message: Message, resource):
    """Automatically sends a single resource without confirmation"""
    try:
        if resource.get('type') == 'file':
            # Send files
            files = resource.get('files', [])
            if not files:
                return False
            
            sent_files = []
            for file_path in files:
                if not file_path or not os.path.exists(file_path):
                    logging.warning(f"File not found: {file_path}")
                    continue
                    
                # Check file size
                try:
                    file_size = os.path.getsize(file_path)
                    if file_size > 50 * 1024 * 1024:  # 50MB
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
                    logging.error(f"Error auto-sending file: {send_error}")
                    continue
            
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

def should_auto_send_resource(resources):
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

def create_resource_selection_keyboard(match, index):
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
async def file_selection_callback(callback: CallbackQuery, faq_loader):
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
            
        # Check file size (maximum 50MB for Telegram)
        try:
            file_size = os.path.getsize(file_path)
            if file_size > 50 * 1024 * 1024:  # 50MB
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
            except:
                pass  # If even callback.answer doesn't work
            return
        
        # Remove keyboard (with message availability check)
        await remove_keyboard(callback.message)
        
    except Exception as e:
        logging.error(f"Error in file selection handler: {str(e)}")
        await send_callback_answer(callback, "❌ An error occurred")

@router.callback_query(F.data.startswith("link_"))
async def link_selection_callback(callback: CallbackQuery, faq_loader):
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
            except:
                pass  # If even callback.answer doesn't work
            return
        
        # Remove keyboard (with message availability check)
        await remove_keyboard(callback.message)
        
    except Exception as e:
        logging.error(f"Error in link selection handler: {str(e)}")
        await send_callback_answer(callback, "❌ An error occurred")

@router.callback_query(F.data.startswith("tv_year_"))
async def tv_year_selection_callback(callback: CallbackQuery, db, config, faq_loader):
    """TV summary table year selection handler"""
    # Check authentication
    if not callback.from_user or not check_authentication_for_callback(callback, db, config):
        await callback.answer(
            "🔒 Session expired. Run /start to re-authenticate.",
            show_alert=True
        )
        return
    
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
                        if file_size > 50 * 1024 * 1024:  # 50MB
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
async def soundbar_year_selection_callback(callback: CallbackQuery, db, config, faq_loader):
    """Soundbar summary table year selection handler"""
    # Check authentication
    if not callback.from_user or not check_authentication_for_callback(callback, db, config):
        await callback.answer(
            "🔒 Session expired. Run /start to re-authenticate.",
            show_alert=True
        )
        return
    
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
                        if file_size > 50 * 1024 * 1024:  # 50MB
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
async def resource_selection_callback(callback: CallbackQuery, faq_loader, db, config):
    """Resource selection handler"""
    # Check authentication
    if not callback.from_user or not check_authentication_for_callback(callback, db, config):
        await callback.answer(
            "🔒 Session expired. Run /start to re-authenticate.",
            show_alert=True
        )
        return
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
            
            sent_files = []
            for file_path in files:
                if not file_path or not os.path.exists(file_path):
                    logging.warning(f"File not found: {file_path}")
                    continue
                    
                # Check file size
                try:
                    file_size = os.path.getsize(file_path)
                    if file_size > 50 * 1024 * 1024:  # 50MB
                        logging.warning(f"File too large: {file_path}")
                        continue
                except OSError as e:
                    logging.error(f"Error checking file size: {e}")
                    continue
                
                # Send file with retries on errors
                try:
                    await send_file_with_retry(callback.message, file_path)
                    sent_files.append(os.path.basename(file_path))
                    logging.info(f"Successfully sent file: {file_path}")
                except Exception as send_error:
                    logging.error(f"Error sending file: {send_error}")
                    # Continue with next file
                    continue
            
            # Send additional text if present
            if 'additional_text' in resource:
                try:
                    await callback.message.answer(resource['additional_text'])
                except Exception as text_error:
                    logging.error(f"Error sending text: {text_error}")
            
            if sent_files:
                try:
                    await callback.answer(f"✅ Sent: {', '.join(sent_files)}")
                except:
                    pass
            else:
                try:
                    await callback.answer("❌ Failed to send files")
                except:
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
                except:
                    pass
                return
        
        # Remove keyboard
        await remove_keyboard(callback.message)
        
    except Exception as e:
        logging.error(f"Error in resource selection handler: {str(e)}")
        await send_callback_answer(callback, "❌ An error occurred")

@router.callback_query(F.data == "cancel")
async def cancel_selection_callback(callback: CallbackQuery, db, config):
    """Selection cancellation handler"""
    # Check authentication
    if not callback.from_user or not check_authentication_for_callback(callback, db, config):
        await callback.answer(
            "🔒 Session expired. Run /start to re-authenticate.",
            show_alert=True
        )
        return
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
async def vsk_pamytka_callback(callback: CallbackQuery, db, config):
    """VSK memo selection handler"""
    # Check authentication
    if not callback.from_user or not check_authentication_for_callback(callback, db, config):
        await callback.answer(
            "🔒 Session expired. Run /start to re-authenticate.",
            show_alert=True
        )
        return
    
    try:
        # Check callback.message availability
        if not callback.message:
            await callback.answer("❌ Message unavailable")
            return
        
        # Send memo file
        file_path = "files/VSK_Insurance_Programs_Memo_sep_24.pdf"
        
        if os.path.exists(file_path):
            # Check file size
            try:
                file_size = os.path.getsize(file_path)
                if file_size > 50 * 1024 * 1024:  # 50MB
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
async def vsk_zayavlenie_callback(callback: CallbackQuery, db, config):
    """VSK claim form selection handler"""
    # Check authentication
    if not callback.from_user or not check_authentication_for_callback(callback, db, config):
        await callback.answer(
            "🔒 Session expired. Run /start to re-authenticate.",
            show_alert=True
        )
        return
    
    try:
        # Check callback.message availability
        if not callback.message:
            await callback.answer("❌ Message unavailable")
            return
        
        # Send claim form files
        files_to_send = [
            "files/VSK_Claim_Form.docx",
            "files/VSK_Insurance_Claim_Form.xlsx"
        ]
        
        sent_files = []
        for file_path in files_to_send:
            if os.path.exists(file_path):
                # Check file size
                try:
                    file_size = os.path.getsize(file_path)
                    if file_size > 50 * 1024 * 1024:  # 50MB
                        logging.warning(f"File too large: {file_path}")
                        continue
                except OSError as e:
                    logging.error(f"Error checking file size {file_path}: {e}")
                    continue
                
                # Send file
                try:
                    await send_file_with_retry(callback.message, file_path)
                    sent_files.append(os.path.basename(file_path))
                    logging.info(f"Successfully sent file: {file_path}")
                except Exception as send_error:
                    logging.error(f"Error sending file {file_path}: {send_error}")
                    # Continue with next file
                    continue
            else:
                logging.warning(f"File not found: {file_path}")
        
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
async def summary_tv_callback(callback: CallbackQuery, db, config):
    """TV summary table selection handler"""
    # Check authentication
    if not callback.from_user or not check_authentication_for_callback(callback, db, config):
        await callback.answer(
            "🔒 Session expired. Run /start to re-authenticate.",
            show_alert=True
        )
        return
    
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
async def summary_soundbar_callback(callback: CallbackQuery, db, config):
    """Soundbar summary table selection handler"""
    # Check authentication
    if not callback.from_user or not check_authentication_for_callback(callback, db, config):
        await callback.answer(
            "🔒 Session expired. Run /start to re-authenticate.",
            show_alert=True
        )
        return
    
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
async def start_handler(message: Message, db, config):
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
            "🎉 Hi! I'm an FAQ bot for employees.\n"
            "📝 Ask a question, and I'll find the information you need."
        )
    else:
        # User is not authenticated
        waiting_for_password.add(user_id)
        await message.answer(
            "🔒 Authentication is required to access the bot.\n"
            "📝 Please enter the access password:"
        )

@router.message(Command("help"))
async def help_handler(message: Message, db, config):
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
        "🤖 <b>Bot Help</b>\n\n"
        "📝 Just ask a question, and I'll try to find an answer in the knowledge base.\n\n"
        "🛠️ Available commands:\n"
        "/start - Start dialog\n"
        "/help - Get help\n"
    )
    
    # Add admin commands if user is admin
    if message.from_user and message.from_user.id == config.ADMIN_ID:
        help_text += (
            "\n🔧 <b>Admin commands:</b>\n"
            "/stats - Work statistics\n"
            "/export_stats - Export full statistics\n"
            "/auth_users - Authentication management\n"
        )
    
    help_text += "\n🔒 Bot is available only to authenticated employees."
    await message.answer(help_text, parse_mode="HTML")

# Command handlers must be ABOVE text handler
@router.message(Command("stats"))
async def stats_handler(
    message: Message, 
    db,
    config
):
    if not message.from_user or message.from_user.id != config.ADMIN_ID:
        await message.answer("You don't have permission to execute this command.")
        return

    try:
        stats = db.get_stats()
        response = (
            "📊 <b>Bot Statistics</b>\n\n"
            f"• Total requests: <b>{stats.total_queries}</b>\n"
            f"• Successful responses: <b>{stats.success_rate:.2f}%</b>\n"
            f"• Unanswered questions: <b>{stats.unanswered_questions}</b>\n"
            f"• Swear words detected: <b>{stats.bad_words_count}</b>\n"
            f"🔒 Authenticated users: <b>{stats.authenticated_users_count}</b>\n\n"
            "🔝 <b>Top 5 popular queries:</b>\n"
        )
        
        for i, (query, count) in enumerate(stats.popular_queries[:5], 1):
            response += f"{i}. {query} - <b>{count}</b> requests\n"
            
        await message.answer(response, parse_mode='HTML')
        
    except Exception as e:
        logging.error(f"Error getting statistics: {str(e)}")
        await message.answer("⚠ An error occurred while getting statistics.")

@router.message(Command("export_stats"))
async def export_stats_handler(
    message: Message, 
    db,
    config
):
    if not message.from_user or message.from_user.id != config.ADMIN_ID:
        await message.answer("⛔ You don't have permission to execute this command.")
        return
        
    try:
        filename = db.export_stats_to_file()
        
        await send_file_with_retry(message, filename)
        os.remove(filename)
        logging.info("Successfully sent statistics file")
    except Exception as e:
        logging.error(f"Error exporting statistics: {str(e)}")
        await message.answer("⚠ An error occurred while exporting statistics.")

@router.message(Command("auth_users"))
async def auth_users_handler(
    message: Message, 
    db,
    config
):
    """Command to view authenticated users (admin only)"""
    if not message.from_user or message.from_user.id != config.ADMIN_ID:
        await message.answer("⛔ You don't have permission to execute this command.")
        return

    try:
        auth_count = db.get_authenticated_users_count()
        await message.answer(
            f"🔒 <b>Authentication Management</b>\n\n"
            f"👥 Total authenticated users: <b>{auth_count}</b>\n\n"
            f"📋 To get the full list, use /export_stats",
            parse_mode='HTML'
        )
        
    except Exception as e:
        logging.error(f"Error getting user list: {str(e)}")
        await message.answer("⚠ An error occurred while getting the user list.")

@router.message(Command("clear_stats"))
async def clear_stats_handler(
    message: Message, 
    db,
    config
):
    """Command to clear statistics (admin only)"""
    if not message.from_user or message.from_user.id != config.ADMIN_ID:
        await message.answer("⛔ You don't have permission to execute this command.")
        return
    
    # Create confirmation keyboard
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Confirm", callback_data="clear_stats_confirm")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="clear_stats_cancel")]
    ])
    
    await message.answer(
        "⚠️ <b>Clear Statistics</b>\n\n"
        "This will archive all log files and start fresh statistics.\n"
        "Are you sure you want to proceed?",
        parse_mode='HTML',
        reply_markup=keyboard
    )

@router.callback_query(F.data == "clear_stats_confirm")
async def clear_stats_confirm_callback(callback: CallbackQuery, db, config):
    """Callback handler for confirming stats clearing"""
    # Check authentication
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
async def clear_stats_cancel_callback(callback: CallbackQuery, db, config):
    """Callback handler for canceling stats clearing"""
    # Check authentication
    if not callback.from_user or callback.from_user.id != config.ADMIN_ID:
        await callback.answer("⛔ You don't have permission to execute this command.", show_alert=True)
        return
    
    await callback.message.edit_text("❌ Statistics clearing cancelled.")
    await callback.answer("Cancelled")

# Handler for special "TV Summary" request
@router.message(F.text.func(lambda text: text and "сводная" in text.lower() and "тв" in text.lower()))
async def tv_summary_handler(
    message: Message, 
    db,
    config
):
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
    db,
    config
):
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
    db,
    config
):
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
    db,
    config
):
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
    db,
    config,
    faq_loader
):
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
    db,
    config,
    faq_loader
):
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
    db,
    faq_loader,
    config
):
    if not message.text or not (text := message.text.strip()):
        await message.answer("Please send a text question.")
        return
    
    if not message.from_user:
        return
        
    user_id = message.from_user.id
    chat_id = message.chat.id if message.chat else None
    message_id = message.message_id
    
    # Custom logging with required fields
    import logging
    logging.getLogger().info(
        f"User message received: {text[:50]}...",
        extra={
            'user_id': user_id,
            'chat_id': chat_id,
            'message_id': message_id,
            'handler': 'message_handler'
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
    
    if not distances or not indices:
        logging.info(f"No matches found for query: '{text}'")
        await message.answer("Did not find a suitable answer. Specify your query.")
        db.log_query(text, success=False)
        db.log_unanswered_question(text)
        return

    similarity = distances[0]
    index = indices[0]
    match = faq_loader.faq[index]
    
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
    
    # Log result
    db.log_query(text, success=True)

