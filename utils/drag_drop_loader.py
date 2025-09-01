#!/usr/bin/env python3
"""
Drag & Drop FAQ Loader - Fastest way to upload files
Just drag files/folders and they're automatically added to FAQ
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import os
import sys
import threading
from pathlib import Path
import json

# Add current directory to path for bulk_loader import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from bulk_loader import BulkFAQLoader
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure bulk_loader.py is in the same directory as this script.")
    sys.exit(1)

# Try to import tkinterdnd2, fallback to file dialog if not available
from typing import Any, Optional

# Initialize variables
DND_FILES: Optional[str] = None
TkinterDnD: Any = None
HAS_DND_SUPPORT = False

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD  # type: ignore
    HAS_DND_SUPPORT = True
except ImportError:
    print("Warning: tkinterdnd2 not found. Install it with: pip install tkinterdnd2")
    print("Falling back to file dialog interface.")
    HAS_DND_SUPPORT = False
    DND_FILES = None
    
    # Create a fallback TkinterDnD class
    class TkinterDnD:  # type: ignore
        @staticmethod
        def Tk():
            return tk.Tk()

class DragDropFAQLoader:
    def __init__(self, root):
        self.root = root
        self.root.title("Drag & Drop FAQ Loader - Перетащите файлы сюда")
        self.root.geometry("700x500")
        
        self.loader = BulkFAQLoader()
        self.processing = False
        self.create_widgets()
        self.setup_drag_drop()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🚀 Drag & Drop FAQ Loader", 
                               font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        subtitle_label = ttk.Label(main_frame, 
                                  text="Перетащите файлы или папки для мгновенного добавления в FAQ",
                                  font=("Arial", 10))
        subtitle_label.pack(pady=(0, 30))
        
        # Drop zone
        self.drop_frame = tk.Frame(main_frame, 
                                  bg="#f0f0f0", 
                                  bd=3, 
                                  relief="ridge",
                                  height=200)
        self.drop_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        self.drop_frame.pack_propagate(False)
        
        # Drop zone content
        drop_content = tk.Frame(self.drop_frame, bg="#f0f0f0")
        drop_content.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        self.drop_icon = tk.Label(drop_content, text="📁", font=("Arial", 48), bg="#f0f0f0")
        self.drop_icon.pack()
        
        if HAS_DND_SUPPORT:
            drop_text = "Перетащите файлы или папки сюда"
            hint_text = "Поддерживаются: CSV, Excel, JSON, папки с файлами, текстовые списки"
        else:
            drop_text = "Нажмите для выбора файлов"
            hint_text = "Поддерживаются: CSV, Excel, JSON, папки с файлами, текстовые списки\n(tkinterdnd2 не установлен - используется диалог выбора файлов)"
        
        self.drop_label = tk.Label(drop_content, 
                                  text=drop_text,
                                  font=("Arial", 14, "bold"),
                                  bg="#f0f0f0",
                                  fg="#666",
                                  cursor="hand2" if not HAS_DND_SUPPORT else "")
        self.drop_label.pack()
        
        self.drop_hint = tk.Label(drop_content,
                                 text=hint_text,
                                 font=("Arial", 9),
                                 bg="#f0f0f0",
                                 fg="#999")
        self.drop_hint.pack(pady=(5, 0))
        
        # Quick options
        options_frame = ttk.LabelFrame(main_frame, text="⚡ Быстрые настройки", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        opts_inner = ttk.Frame(options_frame)
        opts_inner.pack(fill=tk.X)
        
        self.merge_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(opts_inner, text="🔄 Объединить с существующими", 
                       variable=self.merge_var).pack(side=tk.LEFT)
        
        self.auto_title_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(opts_inner, text="🏷️ Автоматические названия", 
                       variable=self.auto_title_var).pack(side=tk.LEFT, padx=(20, 0))
        
        self.group_files_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(opts_inner, text="📦 Группировать по типу файла", 
                       variable=self.group_files_var).pack(side=tk.LEFT, padx=(20, 0))
        
        # Quick actions
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Button(action_frame, text="📋 Шаблоны", 
                  command=self.create_templates).pack(side=tk.LEFT)
        ttk.Button(action_frame, text="👀 Просмотр", 
                  command=self.preview_faq).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(action_frame, text="🔄 Очистить лог", 
                  command=self.clear_log).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(action_frame, text="❌ Выход", 
                  command=self.root.quit).pack(side=tk.RIGHT)
        
        # Progress
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Log
        log_frame = ttk.LabelFrame(main_frame, text="📝 Лог операций", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Initial log message
        self.log("🎯 Готов к загрузке! Перетащите файлы в область выше")
        self.log("💡 Совет: Для массовой загрузки используйте CSV/Excel шаблоны")
        
    def setup_drag_drop(self):
        """Setup drag and drop functionality"""
        if HAS_DND_SUPPORT:
            self.drop_frame.drop_target_register(DND_FILES)
            self.drop_frame.dnd_bind('<<Drop>>', self.handle_drop)
            
            # Visual feedback for drag over
            self.drop_frame.dnd_bind('<<DragEnter>>', self.on_drag_enter)
            self.drop_frame.dnd_bind('<<DragLeave>>', self.on_drag_leave)
        else:
            # Add click event for file dialog
            self.drop_frame.bind('<Button-1>', self.open_file_dialog)
            self.drop_icon.bind('<Button-1>', self.open_file_dialog)
            self.drop_label.bind('<Button-1>', self.open_file_dialog)
            self.drop_hint.bind('<Button-1>', self.open_file_dialog)
    
    def on_drag_enter(self, event):
        """Visual feedback when dragging over"""
        self.drop_frame.config(bg="#e8f5e8", relief=tk.SOLID)
        self.drop_icon.config(bg="#e8f5e8")
        self.drop_label.config(bg="#e8f5e8", text="📁 Отпустите для загрузки", fg="#2d5a2d")
        self.drop_hint.config(bg="#e8f5e8")
    
    def on_drag_leave(self, event):
        """Reset visual feedback when drag leaves"""
        self.drop_frame.config(bg="#f0f0f0", relief="ridge")
        self.drop_icon.config(bg="#f0f0f0")
        if HAS_DND_SUPPORT:
            self.drop_label.config(bg="#f0f0f0", text="Перетащите файлы или папки сюда", fg="#666")
        else:
            self.drop_label.config(bg="#f0f0f0", text="Нажмите для выбора файлов", fg="#666")
        self.drop_hint.config(bg="#f0f0f0")
    
    def handle_drop(self, event):
        """Handle dropped files/folders"""
        if self.processing:
            self.log("⚠️ Уже выполняется загрузка, подождите...")
            return
        
        # Reset visual feedback
        self.on_drag_leave(None)
        
        # Get dropped files
        files = self.root.tk.splitlist(event.data)
        
        if not files:
            self.log("❌ Нет файлов для обработки")
            return
        
        self.log(f"📥 Получено {len(files)} объект(ов):")
        for file in files:
            self.log(f"   - {os.path.basename(file)}")
        
        # Process in background thread
        thread = threading.Thread(target=self._process_dropped_files, args=(files,))
        thread.daemon = True
        thread.start()
    
    def _process_dropped_files(self, files):
        """Process dropped files in background"""
        try:
            self.processing = True
            self.root.after(0, lambda: self.progress.start())
            
            total_new = 0
            total_entries = 0
            
            for file_path in files:
                if not os.path.exists(file_path):
                    self.log(f"⚠️ Пропускаем несуществующий путь: {file_path}")
                    continue
                
                self.log(f"🔄 Обрабатываем: {os.path.basename(file_path)}")
                
                # Determine format and process
                if os.path.isdir(file_path):
                    # It's a folder
                    new_count, total_count = self.loader.bulk_import(
                        source=file_path,
                        format_type="folder",
                        merge=self.merge_var.get(),
                        group_by_extension=self.group_files_var.get(),
                        auto_title=self.auto_title_var.get()
                    )
                else:
                    # It's a file - detect format
                    ext = Path(file_path).suffix.lower()
                    
                    if ext == '.csv':
                        format_type = 'csv'
                    elif ext in ['.xlsx', '.xls']:
                        format_type = 'excel'
                    elif ext == '.json':
                        format_type = 'json'
                    elif ext == '.txt':
                        format_type = 'txt'
                    else:
                        self.log(f"⚠️ Неизвестный формат файла: {ext}")
                        continue
                    
                    new_count, total_count = self.loader.bulk_import(
                        source=file_path,
                        format_type=format_type,
                        merge=self.merge_var.get()
                    )
                
                total_new += new_count
                total_entries = total_count
                
                self.log(f"✅ {os.path.basename(file_path)}: +{new_count} записей")
            
            self.log(f"🎉 Загрузка завершена!")
            self.log(f"📊 Всего добавлено: {total_new} записей")
            self.log(f"📚 Общее количество: {total_entries} записей")
            self.log("💡 Перезапустите бота для применения изменений")
            
            # Show success notification
            self.root.after(0, lambda: messagebox.showinfo(
                "Успех!",
                f"Загрузка завершена успешно!\n\n"
                f"Добавлено: {total_new} записей\n"
                f"Всего: {total_entries} записей\n\n"
                f"Перезапустите бота для применения изменений."
            ))
            
        except Exception as e:
            error_msg = f"❌ Ошибка обработки: {str(e)}"
            self.log(error_msg)
            self.root.after(0, lambda: messagebox.showerror("Ошибка", str(e)))
        finally:
            self.processing = False
            self.root.after(0, lambda: self.progress.stop())
    
    def log(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, f"[{self.get_timestamp()}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def clear_log(self):
        """Clear log"""
        self.log_text.delete(1.0, tk.END)
        self.log("🧹 Лог очищен")
    
    def create_templates(self):
        """Create template files"""
        try:
            self.loader.create_template_files()
            self.log("📋 Шаблоны созданы в папке 'templates/'")
            messagebox.showinfo("Успех", 
                              "Шаблоны созданы в папке 'templates/'\n\n"
                              "Отредактируйте их и перетащите обратно в эту программу!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка создания шаблонов: {e}")
    
    def preview_faq(self):
        """Preview current FAQ"""
        try:
            faq_data = self.loader.load_existing_faq()
            
            # Create preview window
            preview_window = tk.Toplevel(self.root)
            preview_window.title("👀 Просмотр FAQ")
            preview_window.geometry("600x400")
            
            # Add text widget with scrollbar
            text_frame = ttk.Frame(preview_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text_widget = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD)
            text_widget.pack(fill=tk.BOTH, expand=True)
            
            # Format and display FAQ
            if faq_data:
                text_widget.insert(tk.END, f"📚 FAQ содержит {len(faq_data)} записей:\n\n")
                
                for i, entry in enumerate(faq_data, 1):
                    query = entry.get('query', 'Без названия')
                    text_widget.insert(tk.END, f"{i}. 📝 {query}\n")
                    
                    if entry.get('variations'):
                        variations = ', '.join(entry['variations'])
                        text_widget.insert(tk.END, f"   🔄 Варианты: {variations}\n")
                    
                    resources_count = 0
                    if entry.get('resources'):
                        for resource in entry['resources']:
                            if resource.get('type') == 'file':
                                files = resource.get('files', [])
                                resources_count += len(files)
                                text_widget.insert(tk.END, f"   📁 Файлы: {len(files)} шт.\n")
                            elif resource.get('type') == 'link':
                                resources_count += 1
                                link = resource.get('link', '')
                                text_widget.insert(tk.END, f"   🔗 Ссылка: {link}\n")
                    
                    if resources_count == 0:
                        text_widget.insert(tk.END, f"   ❓ Нет ресурсов\n")
                    
                    text_widget.insert(tk.END, "\n")
                
                # Summary
                total_files = sum(
                    len(res.get('files', [])) 
                    for entry in faq_data 
                    for res in entry.get('resources', []) 
                    if res.get('type') == 'file'
                )
                total_links = sum(
                    1 
                    for entry in faq_data 
                    for res in entry.get('resources', []) 
                    if res.get('type') == 'link'
                )
                
                text_widget.insert(tk.END, f"📊 Сводка:\n")
                text_widget.insert(tk.END, f"   📝 Записей: {len(faq_data)}\n")
                text_widget.insert(tk.END, f"   📁 Файлов: {total_files}\n")
                text_widget.insert(tk.END, f"   🔗 Ссылок: {total_links}\n")
                
            else:
                text_widget.insert(tk.END, "📝 FAQ пуст. Перетащите файлы для загрузки.")
                
            text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка просмотра FAQ: {e}")
    
    def open_file_dialog(self, event=None):
        """Open file dialog when drag and drop is not available"""
        if self.processing:
            self.log("⚠️ Уже выполняется загрузка, подождите...")
            return
        
        # Ask user what to select
        choice = messagebox.askyesnocancel(
            "Выбор файлов",
            "Выберите тип:\n\n"
            "• Да - Выбрать файлы\n"
            "• Нет - Выбрать папку\n"
            "• Отмена - Отменить"
        )
        
        if choice is None:  # Cancel
            return
        elif choice:  # Yes - files
            files = filedialog.askopenfilenames(
                title="Выберите файлы для загрузки",
                filetypes=[
                    ("Все поддерживаемые", "*.csv;*.xlsx;*.xls;*.json;*.txt"),
                    ("CSV файлы", "*.csv"),
                    ("Excel файлы", "*.xlsx;*.xls"),
                    ("JSON файлы", "*.json"),
                    ("Текстовые файлы", "*.txt"),
                    ("Все файлы", "*.*")
                ]
            )
            if files:
                self.process_selected_files(list(files))
        else:  # No - folder
            folder = filedialog.askdirectory(
                title="Выберите папку для загрузки"
            )
            if folder:
                self.process_selected_files([folder])
    
    def process_selected_files(self, files):
        """Process selected files (same as handle_drop but for file dialog)"""
        if not files:
            self.log("❌ Нет файлов для обработки")
            return
        
        self.log(f"📥 Выбрано {len(files)} объект(ов):")
        for file in files:
            self.log(f"   - {os.path.basename(file)}")
        
        # Process in background thread
        thread = threading.Thread(target=self._process_dropped_files, args=(files,))
        thread.daemon = True
        thread.start()


def main():
    if HAS_DND_SUPPORT:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    
    app = DragDropFAQLoader(root)
    root.mainloop()


if __name__ == "__main__":
    main()