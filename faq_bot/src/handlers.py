import logging
import os
import asyncio
from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramRetryAfter, TelegramNetworkError, TelegramBadRequest

router = Router()

# Словарь для отслеживания пользователей, ожидающих аутентификации
waiting_for_password = set()

def check_authentication(message: Message, db, config) -> bool:
    """Проверяет, аутентифицирован ли пользователь"""
    if not message.from_user:
        return False
    
    user_id = message.from_user.id
    
    # Проверяем, является ли пользователь админом (админ не нуждается в аутентификации)
    if user_id == config.ADMIN_ID:
        return True
    
    # Проверяем в базе данных
    return db.is_user_authenticated(user_id)

def check_authentication_for_callback(callback: CallbackQuery, db, config) -> bool:
    """Проверяет аутентификацию для callback query"""
    if not callback.from_user:
        return False
    
    user_id = callback.from_user.id
    
    # Проверяем, является ли пользователь админом
    if user_id == config.ADMIN_ID:
        return True
    
    # Проверяем в базе данных
    return db.is_user_authenticated(user_id)

async def retry_file_operation(operation, max_retries=3, delay=1):
    """Повторяет операцию с файлом при ошибках сети"""
    for attempt in range(max_retries):
        try:
            return await operation()
        except (TelegramNetworkError, ConnectionError, OSError) as e:
            if attempt == max_retries - 1:
                raise e
            wait_time = delay * (attempt + 1)
            logging.warning(f"Попытка {attempt + 1}/{max_retries} неудачна: {e}. Повтор через {wait_time} сек.")
            await asyncio.sleep(wait_time)
        except TelegramRetryAfter as e:
            logging.warning(f"Требуется ожидание {e.retry_after} сек.")
            await asyncio.sleep(e.retry_after)
        except Exception as e:
            # Для других ошибок не повторяем
            raise e
    return None

async def auto_send_single_resource(message: Message, resource):
    """Автоматически отправляет единственный ресурс без подтверждения"""
    try:
        if resource.get('type') == 'file':
            # Отправляем файлы
            files = resource.get('files', [])
            if not files:
                return False
            
            sent_files = []
            for file_path in files:
                if not file_path or not os.path.exists(file_path):
                    logging.warning(f"Файл не найден: {file_path}")
                    continue
                    
                # Проверяем размер файла
                try:
                    file_size = os.path.getsize(file_path)
                    if file_size > 50 * 1024 * 1024:  # 50MB
                        logging.warning(f"Файл слишком большой: {file_path}")
                        continue
                except OSError as e:
                    logging.error(f"Ошибка проверки размера файла: {e}")
                    continue
                
                # Отправляем файл с повторами
                try:
                    async def send_file():
                        return await message.answer_document(types.FSInputFile(file_path))
                    
                    await retry_file_operation(send_file)
                    sent_files.append(os.path.basename(file_path))
                    logging.info(f"Автоматически отправлен файл: {file_path}")
                except Exception as send_error:
                    logging.error(f"Ошибка авто-отправки файла: {send_error}")
                    continue
            
            # Отправляем дополнительный текст, если есть
            if 'additional_text' in resource:
                try:
                    await message.answer(resource['additional_text'])
                except Exception as text_error:
                    logging.error(f"Ошибка отправки доп. текста: {text_error}")
            
            return len(sent_files) > 0
                    
        elif resource.get('type') == 'link':
            # Отправляем ссылку
            link = resource.get('link')
            if not link:
                return False
                
            try:
                await message.answer(link)
                logging.info(f"Автоматически отправлена ссылка: {link}")
                return True
            except Exception as send_error:
                logging.error(f"Ошибка авто-отправки ссылки: {send_error}")
                return False
        
        return False
        
    except Exception as e:
        logging.error(f"Ошибка в auto_send_single_resource: {str(e)}")
        return False

def should_auto_send_resource(resources):
    """Определяет, нужно ли автоматически отправлять ресурс"""
    if not resources or len(resources) != 1:
        return False, None
    
    resource = resources[0]
    
    # Для ссылок всегда авто-отправка
    if resource.get('type') == 'link':
        return True, resource
    
    # Для файлов - только если один файл
    if resource.get('type') == 'file':
        files = resource.get('files', [])
        if len(files) == 1:
            return True, resource
    
    return False, None

def create_resource_selection_keyboard(match, index):
    """Создает клавиатуру для выбора ресурсов"""
    keyboard = []
    
    # Добавляем кнопки для ресурсов
    if 'resources' in match:
        for i, resource in enumerate(match['resources']):
            title = resource.get('title', 'Ресурс')
            callback_data = f"resource_{index}_{i}"
            
            # Добавляем соответствующую иконку
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
    
    # Кнопка "Отмена"
    keyboard.append([InlineKeyboardButton(
        text="❌ Отмена",
        callback_data="cancel"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@router.callback_query(F.data.startswith("file_"))
async def file_selection_callback(callback: CallbackQuery, faq_loader):
    """Обработчик выбора файла"""
    try:
        # Проверяем наличие callback.data
        if not callback.data:
            await callback.answer("❌ Неверные данные")
            return
            
        # Парсим callback_data: file_{index}_{file_key}_{file_index}
        parts = callback.data.split("_")
        if len(parts) < 4:
            await callback.answer("❌ Неверный формат данных")
            return
            
        index = int(parts[1])
        file_key = parts[2]
        file_index = int(parts[3])
        
        if not faq_loader.faq or index >= len(faq_loader.faq):
            await callback.answer("❌ Неверный индекс")
            return
            
        match = faq_loader.faq[index]
        
        if file_key not in match:
            await callback.answer("❌ Файл не найден")
            return
            
        files = match[file_key] if isinstance(match[file_key], list) else [match[file_key]]
        
        if file_index >= len(files):
            await callback.answer("❌ Неверный индекс файла")
            return
            
        file_path = files[file_index]
        
        if not file_path or not os.path.exists(file_path):
            logging.warning(f"Файл не найден: {file_path}")
            await callback.answer("❌ Файл не найден на диске")
            return
            
        # Проверяем размер файла (максимум 50MB для Telegram)
        try:
            file_size = os.path.getsize(file_path)
            if file_size > 50 * 1024 * 1024:  # 50MB
                await callback.answer("❌ Файл слишком большой")
                return
        except OSError as e:
            logging.error(f"Ошибка проверки размера файла: {e}")
            await callback.answer("❌ Ошибка доступа к файлу")
            return
            
        # Проверяем доступность callback.message
        if not callback.message:
            await callback.answer("❌ Сообщение недоступно")
            return
            
        # Отправляем выбранный файл с обработкой ошибок
        try:
            if not callback.message:
                await callback.answer("❌ Сообщение недоступно")
                return
                
            async def send_file():
                if callback.message:
                    return await callback.message.answer_document(types.FSInputFile(file_path))
                return None
            
            await retry_file_operation(send_file)
            await callback.answer("✅ Файл отправлен")
            logging.info(f"Успешно отправлен файл: {file_path}")
        except Exception as send_error:
            logging.error(f"Ошибка отправки файла: {send_error}")
            try:
                await callback.answer("❌ Ошибка отправки файла. Попробуйте позже.")
            except:
                pass  # Если даже callback.answer не работает
            return
        
        # Удаляем клавиатуру (с проверкой доступности сообщения)
        try:
            if callback.message and hasattr(callback.message, 'edit_reply_markup') and not isinstance(callback.message, types.InaccessibleMessage):
                await callback.message.edit_reply_markup(reply_markup=None)
        except Exception as edit_error:
            logging.warning(f"Не удалось удалить клавиатуру: {edit_error}")
        
    except Exception as e:
        logging.error(f"Ошибка при обработке выбора файла: {str(e)}")
        await callback.answer("❌ Произошла ошибка")

@router.callback_query(F.data.startswith("link_"))
async def link_selection_callback(callback: CallbackQuery, faq_loader):
    """Обработчик выбора ссылки"""
    try:
        # Проверяем наличие callback.data
        if not callback.data:
            await callback.answer("❌ Неверные данные")
            return
            
        # Парсим callback_data: link_{index}
        parts = callback.data.split("_")
        if len(parts) < 2:
            await callback.answer("❌ Неверный формат данных")
            return
            
        index = int(parts[1])
        
        if not faq_loader.faq or index >= len(faq_loader.faq):
            await callback.answer("❌ Неверный индекс")
            return
            
        match = faq_loader.faq[index]
        
        if 'link' not in match:
            await callback.answer("❌ Ссылка не найдена")
            return
            
        # Проверяем доступность callback.message
        if not callback.message:
            await callback.answer("❌ Сообщение недоступно")
            return
            
        # Отправляем ссылку с обработкой ошибок
        try:
            await callback.message.answer(match['link'])
            await callback.answer("✅ Ссылка отправлена")
        except Exception as send_error:
            logging.error(f"Ошибка отправки ссылки: {send_error}")
            try:
                await callback.answer("❌ Ошибка отправки ссылки")
            except:
                pass  # Если даже callback.answer не работает
            return
        
        # Удаляем клавиатуру (с проверкой доступности сообщения)
        try:
            if callback.message and hasattr(callback.message, 'edit_reply_markup') and not isinstance(callback.message, types.InaccessibleMessage):
                await callback.message.edit_reply_markup(reply_markup=None)
        except Exception as edit_error:
            logging.warning(f"Не удалось удалить клавиатуру: {edit_error}")
        
    except Exception as e:
        logging.error(f"Ошибка при обработке выбора ссылки: {str(e)}")
        await callback.answer("❌ Произошла ошибка")

@router.callback_query(F.data.startswith("tv_year_"))
async def tv_year_selection_callback(callback: CallbackQuery, db, config, faq_loader):
    """Обработчик выбора года для сводной таблицы ТВ"""
    # Проверяем аутентификацию
    if not callback.from_user or not check_authentication_for_callback(callback, db, config):
        await callback.answer(
            "🔒 Сессия истекла. Выполните /start для повторной аутентификации.",
            show_alert=True
        )
        return
    
    try:
        # Проверяем наличие callback.data
        if not callback.data:
            await callback.answer("❌ Неверные данные")
            return
            
        # Парсим год из callback_data
        year = callback.data.split("_")[-1]
        
        if year not in ["2024", "2025"]:
            await callback.answer("❌ Неверный год")
            return
        
        # Проверяем доступность callback.message
        if not callback.message:
            await callback.answer("❌ Сообщение недоступно")
            return
        
        # Ищем соответствующую запись в FAQ
        if not faq_loader.faq:
            await callback.answer("❌ Данные не загружены")
            return
        
        # Находим запись по году
        target_query = f"Сводная таблица ТВ {year}"
        target_index = None
        
        for i, item in enumerate(faq_loader.faq):
            if item.get("query") == target_query:
                target_index = i
                break
        
        if target_index is None:
            await callback.answer("❌ Запись не найдена")
            return
        
        match = faq_loader.faq[target_index]
        
        # Отправляем ответ
        await callback.message.answer(match['response'])
        
        # Отправляем файл
        if 'resources' in match and match['resources']:
            resource = match['resources'][0]  # Берем первый ресурс
            if resource.get('type') == 'file':
                files = resource.get('files', [])
                if files:
                    file_path = files[0]  # Берем первый файл
                    
                    if os.path.exists(file_path):
                        # Проверяем размер файла
                        try:
                            file_size = os.path.getsize(file_path)
                            if file_size > 50 * 1024 * 1024:  # 50MB
                                await callback.answer("❌ Файл слишком большой")
                                return
                        except OSError as e:
                            logging.error(f"Ошибка проверки размера файла: {e}")
                            await callback.answer("❌ Ошибка доступа к файлу")
                            return
                        
                        # Отправляем файл
                        try:
                            async def send_file():
                                if callback.message:
                                    return await callback.message.answer_document(types.FSInputFile(file_path))
                                return None
                            
                            await retry_file_operation(send_file)
                            await callback.answer("✅ Файл отправлен")
                            logging.info(f"Успешно отправлен файл: {file_path}")
                        except Exception as send_error:
                            logging.error(f"Ошибка отправки файла: {send_error}")
                            await callback.answer("❌ Ошибка отправки файла")
                            return
                    else:
                        await callback.answer("❌ Файл не найден")
                        return
        
        # Удаляем клавиатуру
        try:
            if callback.message and hasattr(callback.message, 'edit_reply_markup') and not isinstance(callback.message, types.InaccessibleMessage):
                await callback.message.edit_reply_markup(reply_markup=None)
        except Exception as edit_error:
            logging.warning(f"Не удалось удалить клавиатуру: {edit_error}")
        
    except Exception as e:
        logging.error(f"Ошибка при обработке выбора года ТВ: {str(e)}")
        await callback.answer("❌ Произошла ошибка")

@router.callback_query(F.data.startswith("soundbar_year_"))
async def soundbar_year_selection_callback(callback: CallbackQuery, db, config, faq_loader):
    """Обработчик выбора года для сводной таблицы саундбаров"""
    # Проверяем аутентификацию
    if not callback.from_user or not check_authentication_for_callback(callback, db, config):
        await callback.answer(
            "🔒 Сессия истекла. Выполните /start для повторной аутентификации.",
            show_alert=True
        )
        return
    
    try:
        # Проверяем наличие callback.data
        if not callback.data:
            await callback.answer("❌ Неверные данные")
            return
            
        # Парсим год из callback_data
        year = callback.data.split("_")[-1]
        
        if year not in ["2024", "2025"]:
            await callback.answer("❌ Неверный год")
            return
        
        # Проверяем доступность callback.message
        if not callback.message:
            await callback.answer("❌ Сообщение недоступно")
            return
        
        # Ищем соответствующую запись в FAQ
        if not faq_loader.faq:
            await callback.answer("❌ Данные не загружены")
            return
        
        # Находим запись по году
        target_query = f"Сводная саундбар {year}"
        target_index = None
        
        for i, item in enumerate(faq_loader.faq):
            if item.get("query") == target_query:
                target_index = i
                break
        
        if target_index is None:
            await callback.answer("❌ Запись не найдена")
            return
        
        match = faq_loader.faq[target_index]
        
        # Отправляем ответ
        await callback.message.answer(match['response'])
        
        # Отправляем файл
        if 'resources' in match and match['resources']:
            resource = match['resources'][0]  # Берем первый ресурс
            if resource.get('type') == 'file':
                files = resource.get('files', [])
                if files:
                    file_path = files[0]  # Берем первый файл
                    
                    if os.path.exists(file_path):
                        # Проверяем размер файла
                        try:
                            file_size = os.path.getsize(file_path)
                            if file_size > 50 * 1024 * 1024:  # 50MB
                                await callback.answer("❌ Файл слишком большой")
                                return
                        except OSError as e:
                            logging.error(f"Ошибка проверки размера файла: {e}")
                            await callback.answer("❌ Ошибка доступа к файлу")
                            return
                        
                        # Отправляем файл
                        try:
                            async def send_file():
                                if callback.message:
                                    return await callback.message.answer_document(types.FSInputFile(file_path))
                                return None
                            
                            await retry_file_operation(send_file)
                            await callback.answer("✅ Файл отправлен")
                            logging.info(f"Успешно отправлен файл: {file_path}")
                        except Exception as send_error:
                            logging.error(f"Ошибка отправки файла: {send_error}")
                            await callback.answer("❌ Ошибка отправки файла")
                            return
                    else:
                        await callback.answer("❌ Файл не найден")
                        return
        
        # Удаляем клавиатуру
        try:
            if callback.message and hasattr(callback.message, 'edit_reply_markup') and not isinstance(callback.message, types.InaccessibleMessage):
                await callback.message.edit_reply_markup(reply_markup=None)
        except Exception as edit_error:
            logging.warning(f"Не удалось удалить клавиатуру: {edit_error}")
        
    except Exception as e:
        logging.error(f"Ошибка при обработке выбора года саундбаров: {str(e)}")
        await callback.answer("❌ Произошла ошибка")

@router.callback_query(F.data.startswith("resource_"))
async def resource_selection_callback(callback: CallbackQuery, faq_loader, db, config):
    """Обработчик выбора ресурса"""
    # Проверяем аутентификацию
    if not callback.from_user or not check_authentication_for_callback(callback, db, config):
        await callback.answer(
            "🔒 Сессия истекла. Выполните /start для повторной аутентификации.",
            show_alert=True
        )
        return
    try:
        # Проверяем наличие callback.data
        if not callback.data:
            await callback.answer("❌ Неверные данные")
            return
            
        # Парсим callback_data: resource_{index}_{resource_index}
        parts = callback.data.split("_")
        if len(parts) < 3:
            await callback.answer("❌ Неверный формат данных")
            return
            
        index = int(parts[1])
        resource_index = int(parts[2])
        
        if not faq_loader.faq or index >= len(faq_loader.faq):
            await callback.answer("❌ Неверный индекс")
            return
            
        match = faq_loader.faq[index]
        
        if 'resources' not in match or resource_index >= len(match['resources']):
            await callback.answer("❌ Ресурс не найден")
            return
            
        resource = match['resources'][resource_index]
        
        # Проверяем доступность callback.message
        if not callback.message:
            await callback.answer("❌ Сообщение недоступно")
            return
        
        # Обрабатываем разные типы ресурсов
        if resource.get('type') == 'file':
            # Отправляем файлы
            files = resource.get('files', [])
            if not files:
                await callback.answer("❌ Файлы не найдены")
                return
            
            sent_files = []
            for file_path in files:
                if not file_path or not os.path.exists(file_path):
                    logging.warning(f"Файл не найден: {file_path}")
                    continue
                    
                # Проверяем размер файла
                try:
                    file_size = os.path.getsize(file_path)
                    if file_size > 50 * 1024 * 1024:  # 50MB
                        logging.warning(f"Файл слишком большой: {file_path}")
                        continue
                except OSError as e:
                    logging.error(f"Ошибка проверки размера файла: {e}")
                    continue
                
                # Отправляем файл с повторами при ошибках
                try:
                    async def send_file():
                        if callback.message:
                            return await callback.message.answer_document(types.FSInputFile(file_path))
                        return None
                    
                    await retry_file_operation(send_file)
                    sent_files.append(os.path.basename(file_path))
                    logging.info(f"Успешно отправлен файл: {file_path}")
                except Exception as send_error:
                    logging.error(f"Ошибка отправки файла: {send_error}")
                    # Продолжаем с следующим файлом
                    continue
            
            # Отправляем дополнительный текст, если есть
            if 'additional_text' in resource:
                try:
                    await callback.message.answer(resource['additional_text'])
                except Exception as text_error:
                    logging.error(f"Ошибка отправки текста: {text_error}")
            
            if sent_files:
                try:
                    await callback.answer(f"✅ Отправлено: {', '.join(sent_files)}")
                except:
                    pass
            else:
                try:
                    await callback.answer("❌ Не удалось отправить файлы")
                except:
                    pass
                    
        elif resource.get('type') == 'link':
            # Отправляем ссылку
            link = resource.get('link')
            if not link:
                await callback.answer("❌ Ссылка не найдена")
                return
                
            try:
                await callback.message.answer(link)
                await callback.answer("✅ Ссылка отправлена")
            except Exception as send_error:
                logging.error(f"Ошибка отправки ссылки: {send_error}")
                try:
                    await callback.answer("❌ Ошибка отправки ссылки")
                except:
                    pass
                return
        
        # Удаляем клавиатуру
        try:
            if callback.message and hasattr(callback.message, 'edit_reply_markup') and not isinstance(callback.message, types.InaccessibleMessage):
                await callback.message.edit_reply_markup(reply_markup=None)
        except Exception as edit_error:
            logging.warning(f"Не удалось удалить клавиатуру: {edit_error}")
        
    except Exception as e:
        logging.error(f"Ошибка при обработке выбора ресурса: {str(e)}")
        try:
            await callback.answer("❌ Произошла ошибка")
        except:
            pass

@router.callback_query(F.data == "cancel")
async def cancel_selection_callback(callback: CallbackQuery, db, config):
    """Обработчик отмены выбора"""
    # Проверяем аутентификацию
    if not callback.from_user or not check_authentication_for_callback(callback, db, config):
        await callback.answer(
            "🔒 Сессия истекла. Выполните /start для повторной аутентификации.",
            show_alert=True
        )
        return
    try:
        if callback.message and hasattr(callback.message, 'edit_text') and not isinstance(callback.message, types.InaccessibleMessage):
            await callback.message.edit_text("❌ Выбор отменен")
        else:
            # Если не можем редактировать сообщение, просто отвечаем
            await callback.answer("❌ Выбор отменен")
            return
    except Exception as e:
        logging.warning(f"Не удалось редактировать сообщение: {e}")
        await callback.answer("❌ Выбор отменен")
        return
        
    await callback.answer()

@router.callback_query(F.data == "vsk_pamytka")
async def vsk_pamytka_callback(callback: CallbackQuery, db, config):
    """Обработчик выбора памятки ВСК"""
    # Проверяем аутентификацию
    if not callback.from_user or not check_authentication_for_callback(callback, db, config):
        await callback.answer(
            "🔒 Сессия истекла. Выполните /start для повторной аутентификации.",
            show_alert=True
        )
        return
    
    try:
        # Проверяем доступность callback.message
        if not callback.message:
            await callback.answer("❌ Сообщение недоступно")
            return
        
        # Отправляем файл памятки
        file_path = "files/Памятка_по_программам_страхования_в_ВСК_сен_24.pdf"
        
        if os.path.exists(file_path):
            # Проверяем размер файла
            try:
                file_size = os.path.getsize(file_path)
                if file_size > 50 * 1024 * 1024:  # 50MB
                    await callback.answer("❌ Файл слишком большой")
                    return
            except OSError as e:
                logging.error(f"Ошибка проверки размера файла: {e}")
                await callback.answer("❌ Ошибка доступа к файлу")
                return
            
            # Отправляем файл
            try:
                async def send_file():
                    if callback.message:
                        return await callback.message.answer_document(types.FSInputFile(file_path))
                    return None
                
                await retry_file_operation(send_file)
                await callback.answer("✅ Файл отправлен")
                logging.info(f"Успешно отправлен файл: {file_path}")
            except Exception as send_error:
                logging.error(f"Ошибка отправки файла: {send_error}")
                await callback.answer("❌ Ошибка отправки файла")
                return
        else:
            await callback.answer("❌ Файл не найден")
            return
        
        # Удаляем клавиатуру
        try:
            if callback.message and hasattr(callback.message, 'edit_reply_markup') and not isinstance(callback.message, types.InaccessibleMessage):
                await callback.message.edit_reply_markup(reply_markup=None)
        except Exception as edit_error:
            logging.warning(f"Не удалось удалить клавиатуру: {edit_error}")
        
    except Exception as e:
        logging.error(f"Ошибка при обработке выбора памятки ВСК: {str(e)}")
        await callback.answer("❌ Произошла ошибка")

@router.callback_query(F.data == "vsk_zayavlenie")
async def vsk_zayavlenie_callback(callback: CallbackQuery, db, config):
    """Обработчик выбора заявления ВСК"""
    # Проверяем аутентификацию
    if not callback.from_user or not check_authentication_for_callback(callback, db, config):
        await callback.answer(
            "🔒 Сессия истекла. Выполните /start для повторной аутентификации.",
            show_alert=True
        )
        return
    
    try:
        # Проверяем доступность callback.message
        if not callback.message:
            await callback.answer("❌ Сообщение недоступно")
            return
        
        # Отправляем файлы заявления
        files_to_send = [
            "files/Заявление ВСК.docx",
            "files/Заявление о СС_ВСК.xlsx"
        ]
        
        sent_files = []
        for file_path in files_to_send:
            if os.path.exists(file_path):
                # Проверяем размер файла
                try:
                    file_size = os.path.getsize(file_path)
                    if file_size > 50 * 1024 * 1024:  # 50MB
                        logging.warning(f"Файл слишком большой: {file_path}")
                        continue
                except OSError as e:
                    logging.error(f"Ошибка проверки размера файла {file_path}: {e}")
                    continue
                
                # Отправляем файл
                try:
                    async def send_file():
                        if callback.message:
                            return await callback.message.answer_document(types.FSInputFile(file_path))
                        return None
                    
                    await retry_file_operation(send_file)
                    sent_files.append(os.path.basename(file_path))
                    logging.info(f"Успешно отправлен файл: {file_path}")
                except Exception as send_error:
                    logging.error(f"Ошибка отправки файла {file_path}: {send_error}")
                    # Продолжаем с следующим файлом
                    continue
            else:
                logging.warning(f"Файл не найден: {file_path}")
        
        # Отправляем дополнительный текст
        additional_text = (
            "Какие документы нужны для принятия устройства по страхованию в 1С:\n"
            "- Заявление о страховом случае (Шаблоны + инструкция выше)\n"
            "- Копия паспорта (Основной разворот + прописка)\n"
            "- Копия/оригинал Чека\n"
            "- Договор страхования"
        )
        
        try:
            await callback.message.answer(additional_text)
        except Exception as text_error:
            logging.error(f"Ошибка отправки текста: {text_error}")
        
        if sent_files:
            await callback.answer(f"✅ Отправлено: {', '.join(sent_files)}")
        else:
            await callback.answer("❌ Не удалось отправить файлы")
        
        # Удаляем клавиатуру
        try:
            if callback.message and hasattr(callback.message, 'edit_reply_markup') and not isinstance(callback.message, types.InaccessibleMessage):
                await callback.message.edit_reply_markup(reply_markup=None)
        except Exception as edit_error:
            logging.warning(f"Не удалось удалить клавиатуру: {edit_error}")
        
    except Exception as e:
        logging.error(f"Ошибка при обработке выбора заявления ВСК: {str(e)}")
        await callback.answer("❌ Произошла ошибка")

@router.callback_query(F.data == "summary_tv")
async def summary_tv_callback(callback: CallbackQuery, db, config):
    """Обработчик выбора сводной таблицы ТВ"""
    # Проверяем аутентификацию
    if not callback.from_user or not check_authentication_for_callback(callback, db, config):
        await callback.answer(
            "🔒 Сессия истекла. Выполните /start для повторной аутентификации.",
            show_alert=True
        )
        return
    
    try:
        # Проверяем доступность callback.message
        if not callback.message:
            await callback.answer("❌ Сообщение недоступно")
            return
        
        # Создаем клавиатуру с выбором года для ТВ
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📺 ТВ 2024", callback_data="tv_year_2024")],
            [InlineKeyboardButton(text="📺 ТВ 2025", callback_data="tv_year_2025")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
        ])
        
        # Проверяем, что сообщение доступно для редактирования
        if hasattr(callback.message, 'edit_text') and not isinstance(callback.message, types.InaccessibleMessage):
            await callback.message.edit_text("Выберите год сводной таблицы ТВ:", reply_markup=keyboard)
        else:
            # Если не можем редактировать сообщение, отправляем новое
            await callback.message.answer("Выберите год сводной таблицы ТВ:", reply_markup=keyboard)
        await callback.answer()
        
    except Exception as e:
        logging.error(f"Ошибка при обработке выбора сводной таблицы ТВ: {str(e)}")
        await callback.answer("❌ Произошла ошибка")

@router.callback_query(F.data == "summary_soundbar")
async def summary_soundbar_callback(callback: CallbackQuery, db, config):
    """Обработчик выбора сводной таблицы саундбара"""
    # Проверяем аутентификацию
    if not callback.from_user or not check_authentication_for_callback(callback, db, config):
        await callback.answer(
            "🔒 Сессия истекла. Выполните /start для повторной аутентификации.",
            show_alert=True
        )
        return
    
    try:
        # Проверяем доступность callback.message
        if not callback.message:
            await callback.answer("❌ Сообщение недоступно")
            return
        
        # Создаем клавиатуру с выбором года для саундбара
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎵 Саундбар 2024", callback_data="soundbar_year_2024")],
            [InlineKeyboardButton(text="🎵 Саундбар 2025", callback_data="soundbar_year_2025")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
        ])
        
        # Проверяем, что сообщение доступно для редактирования
        if hasattr(callback.message, 'edit_text') and not isinstance(callback.message, types.InaccessibleMessage):
            await callback.message.edit_text("Выберите год сводной таблицы саундбаров:", reply_markup=keyboard)
        else:
            # Если не можем редактировать сообщение, отправляем новое
            await callback.message.answer("Выберите год сводной таблицы саундбаров:", reply_markup=keyboard)
        await callback.answer()
        
    except Exception as e:
        logging.error(f"Ошибка при обработке выбора сводной таблицы саундбара: {str(e)}")
        await callback.answer("❌ Произошла ошибка")

@router.message(CommandStart())
async def start_handler(message: Message, db, config):
    """Обработчик команды /start с аутентификацией"""
    if not message.from_user:
        return
        
    user_id = message.from_user.id
    
    # Проверяем аутентификацию
    if check_authentication(message, db, config):
        await message.answer(
            "🎉 Привет! Я FAQ-бот для сотрудников.\n"
            "📝 Задай вопрос, и я найду нужную информацию."
        )
    else:
        # Пользователь не аутентифицирован
        waiting_for_password.add(user_id)
        await message.answer(
            "🔒 Для доступа к боту требуется аутентификация.\n"
            "📝 Пожалуйста, введите пароль доступа:"
        )

@router.message(Command("help"))
async def help_handler(message: Message, db, config):
    """Обработчик команды /help с проверкой аутентификации"""
    if not check_authentication(message, db, config):
        await message.answer(
            "🔒 Для доступа к боту выполните команду /start и введите пароль."
        )
        return
        
    help_text = (
        "🤖 <b>Помощь по боту</b>\n\n"
        "📝 Просто задайте вопрос, и я постараюсь найти на него ответ в базе знаний.\n\n"
        "🛠️ Доступные команды:\n"
        "/start - Начать диалог\n"
        "/help - Получить справку\n"
    )
    
    # Добавляем админские команды, если это админ
    if message.from_user and message.from_user.id == config.ADMIN_ID:
        help_text += (
            "\n🔧 <b>Админские команды:</b>\n"
            "/stats - Статистика работы\n"
            "/export_stats - Экспорт полной статистики\n"
            "/auth_users - Управление аутентификацией\n"
        )
    
    help_text += "\n🔒 Бот доступен только аутентифицированным сотрудникам."
    await message.answer(help_text, parse_mode="HTML")

# Обработчики команд должны быть ВЫШЕ обработчика текста
@router.message(Command("stats"))
async def stats_handler(
    message: Message, 
    db,
    config
):
    if not message.from_user or message.from_user.id != config.ADMIN_ID:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return

    try:
        stats = db.get_stats()
        response = (
            "📊 <b>Статистика бота</b>\n\n"
            f"• Всего запросов: <b>{stats.total_queries}</b>\n"
            f"• Успешных ответов: <b>{stats.success_rate:.2f}%</b>\n"
            f"• Неотвеченных вопросов: <b>{stats.unanswered_questions}</b>\n"
            f"• Зафиксировано матов: <b>{stats.bad_words_count}</b>\n"
            f"🔒 Аутентифицированных пользователей: <b>{stats.authenticated_users_count}</b>\n\n"
            "🔝 <b>Топ-5 популярных запросов:</b>\n"
        )
        
        for i, (query, count) in enumerate(stats.popular_queries[:5], 1):
            response += f"{i}. {query} - <b>{count}</b> запросов\n"
            
        await message.answer(response, parse_mode='HTML')
        
    except Exception as e:
        logging.error(f"Ошибка получения статистики: {str(e)}")
        await message.answer("⚠ Произошла ошибка при получении статистики.")

@router.message(Command("export_stats"))
async def export_stats_handler(
    message: Message, 
    db,
    config
):
    if not message.from_user or message.from_user.id != config.ADMIN_ID:
        await message.answer("⛔ У вас нет прав для выполнения этой команды.")
        return
        
    try:
        filename = db.export_stats_to_file()
        
        async def send_stats_file():
            return await message.answer_document(
                types.FSInputFile(filename),
                caption="📁 Полный отчет по статистике"
            )
        
        await retry_file_operation(send_stats_file)
        os.remove(filename)
        logging.info("Успешно отправлен файл статистики")
    except Exception as e:
        logging.error(f"Ошибка экспорта статистики: {str(e)}")
        await message.answer("⚠ Произошла ошибка при экспорте статистики.")

@router.message(Command("auth_users"))
async def auth_users_handler(
    message: Message, 
    db,
    config
):
    """Команда для просмотра аутентифицированных пользователей (только для админа)"""
    if not message.from_user or message.from_user.id != config.ADMIN_ID:
        await message.answer("⛔ У вас нет прав для выполнения этой команды.")
        return

    try:
        auth_count = db.get_authenticated_users_count()
        await message.answer(
            f"🔒 <b>Управление аутентификацией</b>\n\n"
            f"👥 Всего аутентифицированных пользователей: <b>{auth_count}</b>\n\n"
            f"📋 Для получения полного списка используйте /export_stats",
            parse_mode='HTML'
        )
        
    except Exception as e:
        logging.error(f"Ошибка получения списка пользователей: {str(e)}")
        await message.answer("⚠ Произошла ошибка при получении списка пользователей.")

# Обработчик для специального запроса "Сводная ТВ"
@router.message(F.text.func(lambda text: text and "сводная" in text.lower() and "тв" in text.lower()))
async def tv_summary_handler(
    message: Message, 
    db,
    config
):
    """Обработчик для запросов типа "Сводная ТВ" - показывает кнопки выбора года"""
    if not message.text or not (text := message.text.strip()):
        return
    
    if not message.from_user:
        return
    
    # Проверяем аутентификацию
    if not check_authentication(message, db, config):
        await message.answer(
            "🔒 Для доступа к боту выполните команду /start и введите пароль."
        )
        return
    
    # Создаем клавиатуру с выбором года
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📺 ТВ 2024", callback_data="tv_year_2024")],
        [InlineKeyboardButton(text="📺 ТВ 2025", callback_data="tv_year_2025")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
    ])
    
    await message.answer("Выберите год сводной таблицы ТВ:", reply_markup=keyboard)

# Обработчик для специального запроса "Сводная саундбар"
@router.message(F.text.func(lambda text: text and "сводная" in text.lower() and "саундбар" in text.lower()))
async def soundbar_summary_handler(
    message: Message, 
    db,
    config
):
    """Обработчик для запросов типа "Сводная саундбар" - показывает кнопки выбора года"""
    if not message.text or not (text := message.text.strip()):
        return
    
    if not message.from_user:
        return
    
    # Проверяем аутентификацию
    if not check_authentication(message, db, config):
        await message.answer(
            "🔒 Для доступа к боту выполните команду /start и введите пароль."
        )
        return
    
    # Создаем клавиатуру с выбором года
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎵 Саундбар 2024", callback_data="soundbar_year_2024")],
        [InlineKeyboardButton(text="🎵 Саундбар 2025", callback_data="soundbar_year_2025")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
    ])
    
    await message.answer("Выберите год сводной таблицы саундбаров:", reply_markup=keyboard)

# Обработчик для специального запроса "ВСК"
@router.message(F.text.func(lambda text: text and "вск" in text.lower()))
async def vsk_handler(
    message: Message, 
    db,
    config
):
    """Обработчик для запросов типа "ВСК" - показывает кнопки выбора документов"""
    if not message.text or not (text := message.text.strip()):
        return
    
    if not message.from_user:
        return
    
    # Проверяем аутентификацию
    if not check_authentication(message, db, config):
        await message.answer(
            "🔒 Для доступа к боту выполните команду /start и введите пароль."
        )
        return
    
    # Создаем клавиатуру с выбором документов
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Памятка по продукту ВСК", callback_data="vsk_pamytka")],
        [InlineKeyboardButton(text="📄 Заявление о страховом случае ВСК", callback_data="vsk_zayavlenie")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
    ])
    
    await message.answer("Выберите нужный документ по страхованию ВСК:", reply_markup=keyboard)

# Обработчик для специального запроса "Сводная" - показывает кнопки выбора между ТВ и саундбаром
@router.message(F.text.func(lambda text: text and "сводная" in text.lower() and "тв" not in text.lower() and "саундбар" not in text.lower()))
async def summary_choice_handler(
    message: Message, 
    db,
    config
):
    """Обработчик для запроса "Сводная" - показывает кнопки выбора между ТВ и саундбаром"""
    if not message.text or not (text := message.text.strip()):
        return
    
    if not message.from_user:
        return
    
    # Проверяем аутентификацию
    if not check_authentication(message, db, config):
        await message.answer(
            "🔒 Для доступа к боту выполните команду /start и введите пароль."
        )
        return
    
    # Создаем клавиатуру с выбором типа сводной
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📺 Сводная ТВ", callback_data="summary_tv")],
        [InlineKeyboardButton(text="🎵 Сводная Саундбар", callback_data="summary_soundbar")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
    ])
    
    await message.answer("Выберите тип сводной таблицы:", reply_markup=keyboard)

# Этот обработчик должен быть ПОСЛЕДНИМ, так как он ловит все текстовые сообщения
@router.message(F.text)
async def message_handler(
    message: Message, 
    db,
    faq_loader,
    config
):
    if not message.text or not (text := message.text.strip()):
        await message.answer("Отправьте текстовый вопрос.")
        return
    
    if not message.from_user:
        return
        
    user_id = message.from_user.id
    
    # Проверяем, ожидает ли пользователь ввода пароля
    if user_id in waiting_for_password:
        if text == config.ACCESS_PASSWORD:
            # Пароль верный - аутентифицируем пользователя
            waiting_for_password.discard(user_id)
            db.authenticate_user(message.from_user)
            await message.answer(
                "✅ Аутентификация успешна!\n"
                "🎉 Добро пожаловать в FAQ-бот для сотрудников!\n"
                "📝 Теперь вы можете задавать вопросы."
            )
            logging.info(f"Пользователь {user_id} ({message.from_user.first_name}) успешно аутентифицирован")
            return
        else:
            # Неверный пароль
            await message.answer(
                "❌ Неверный пароль!\n"
                "🔒 Попробуйте ещё раз или обратитесь к администратору."
            )
            logging.warning(f"Пользователь {user_id} ввёл неверный пароль: {text}")
            return
    
    # Проверяем аутентификацию перед обработкой запроса
    if not check_authentication(message, db, config):
        await message.answer(
            "🔒 Для доступа к боту выполните команду /start и введите пароль."
        )
        return

    # Проверка на запрещенные слова
    if any(bad_word in text.lower() for bad_word in config.BLOCKED_WORDS):
        await message.answer("❌ Ваше сообщение содержит недопустимые слова.")
        user_id = message.from_user.id if message.from_user else "unknown"
        logging.warning(f"Пользователь {user_id} отправил запрещенное сообщение: {text}")
        if message.from_user:
            db.log_bad_word(message.from_user, text)
        return

    # Поиск ответа в FAQ
    distances, indices = faq_loader.search(text, threshold=config.SIMILARITY_THRESHOLD)
    
    if not distances or not indices:
        logging.info(f"Не найдено совпадений для запроса: '{text}'")
        await message.answer("Не нашёл подходящего ответа. Уточните запрос.")
        db.log_query(text, success=False)
        db.log_unanswered_question(text)
        return

    similarity = distances[0]
    index = indices[0]
    match = faq_loader.faq[index]
    
    # Отправка основного ответа
    await message.answer(match['response'])

    # Проверяем, есть ли ресурсы
    if 'resources' in match and match['resources']:
        # Определяем, нужно ли автоматически отправлять
        should_auto, single_resource = should_auto_send_resource(match['resources'])
        
        if should_auto and single_resource:
            # Автоматически отправляем единственный ресурс
            success = await auto_send_single_resource(message, single_resource)
            if not success:
                # Если авто-отправка не удалась, показываем клавиатуру
                keyboard = create_resource_selection_keyboard(match, index)
                await message.answer("👆 Выберите нужный ресурс:", reply_markup=keyboard)
        else:
            # Показываем клавиатуру для выбора (несколько ресурсов или несколько файлов)
            keyboard = create_resource_selection_keyboard(match, index)
            await message.answer("👆 Выберите нужный ресурс:", reply_markup=keyboard)
    
    # Логирование результата
    db.log_query(text, success=True)