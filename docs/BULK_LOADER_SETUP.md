# 🚀 FAQ Bulk Loader - Complete Setup Guide

## 📋 Quick Summary

I've created a comprehensive bulk loading system that allows you to quickly and easily upload 1000+ files to your FAQ bot. You have **multiple tools** ranging from simple to advanced.

## 🎯 Available Tools

### 1. ⚡ Simple Bulk Loader (Works immediately - no dependencies)
```bash
python simple_bulk_loader.py
```
- **No external dependencies required**
- Supports CSV, JSON, folders, text lists
- Perfect for immediate use

### 2. 🖱️ GUI Interface (User-friendly)
```bash
python faq_gui.py
```
- Visual interface with buttons and dialogs
- Requires: `pip install pandas openpyxl tkinterdnd2`

### 3. 📁 Drag & Drop Interface (Fastest)
```bash
python drag_drop_loader.py
```
- Just drag files into the window
- Automatic format detection
- Requires: `pip install pandas openpyxl tkinterdnd2`

### 4. 💻 Advanced Command Line
```bash
python bulk_loader.py
```
- Full-featured with Excel support
- Requires: `pip install pandas openpyxl tkinterdnd2`

### 5. 🎮 Easy Launcher
```bash
3_bulk_loader.bat
```
- Menu-driven interface
- Choose your preferred method

## 🏁 Quick Start (Works Right Now!)

### Step 1: Create templates
```bash
python simple_bulk_loader.py --templates
```

### Step 2: Edit templates
Open `templates/simple_faq_template.csv` and add your data:
```csv
query,variations,response,files,title
"My Question 1","question 1;q1","Answer here","C:\path\to\file.pdf","Document 1"
"My Question 2","question 2;q2","Answer here","C:\path\to\file2.pdf","Document 2"
```

### Step 3: Load data
```bash
python simple_bulk_loader.py templates/simple_faq_template.csv csv
```

### Step 4: Restart bot
```bash
restart_bot.bat
```

## 💡 For 1000 Files - Best Strategies

### Strategy 1: Folder Auto-Import (Fastest)
```bash
# Put all your files in one folder
python simple_bulk_loader.py "C:\MyFiles" folder
```
- Automatically creates FAQ entries for all files
- Groups by file type
- Zero configuration needed

### Strategy 2: CSV Bulk Import (Most Organized)
```bash
# Create CSV with 1000 rows programmatically:
python -c "
import csv
with open('bulk.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['query', 'files'])
    for i in range(1000):
        writer.writerow([f'Document {i}', f'C:\\files\\doc{i}.pdf'])
"

# Then import:
python simple_bulk_loader.py bulk.csv csv
```

### Strategy 3: JSON Structured Import
```bash
# Use example_bulk_load.py for quick generation:
python example_bulk_load.py 1000
```

## 📊 Supported Formats

### CSV Format
```csv
query,variations,response,files,links,additional_text,title
"Question","alt1;alt2","Answer","file1.pdf;file2.docx","https://link.com","Extra info","Title"
```

### Text List Format
```
Question 1|file1.pdf|https://link.com|Additional info
Question 2|file2.pdf;file3.docx||Just files
Question 3||https://another-link.com|Just link
```

### JSON Format
```json
[
  {
    "query": "Question",
    "variations": ["alt1", "alt2"],
    "response": "Answer",
    "resources": [
      {
        "title": "Document",
        "type": "file",
        "files": ["file.pdf"]
      }
    ]
  }
]
```

### Folder Structure
- Just point to any folder
- Automatically processes all files
- Creates organized FAQ entries

## 🔧 Installation Options

### Option 1: Use Simple Loader (No installation needed)
```bash
# Works immediately with your existing Python
python simple_bulk_loader.py --templates
```

### Option 2: Full Installation (All features)
```bash
# Install dependencies for advanced features
pip install pandas openpyxl tkinterdnd2

# Then use any tool:
python faq_gui.py
python drag_drop_loader.py
python bulk_loader.py
```

### Option 3: Auto Setup
```bash
# Run setup to install everything
setup.bat
```

## 🎯 Real-World Examples

### Example 1: 1000 PDF manuals
```bash
# Put all PDFs in a folder
mkdir "C:\Manuals"
# Copy your 1000 files there

# Auto-import all at once
python simple_bulk_loader.py "C:\Manuals" folder

# Result: FAQ entries for all PDFs created automatically
```

### Example 2: Structured department docs
```bash
# Create CSV:
echo "query,files,title" > departments.csv
echo "HR Manual,C:\docs\hr_manual.pdf,HR Documentation" >> departments.csv
echo "IT Guide,C:\docs\it_guide.pdf,IT Documentation" >> departments.csv
# ... add 1000 lines

# Import:
python simple_bulk_loader.py departments.csv csv
```

### Example 3: Mixed content (files + links)
```bash
# Create text list:
echo "Company Policy|policy.pdf|https://company.com/policy|Official policy" > mixed.txt
echo "Tech Support||https://support.company.com|Online support only" >> mixed.txt
# ... add more

# Import:
python simple_bulk_loader.py mixed.txt txt
```

## 🔄 Workflow for Regular Updates

### Daily workflow:
1. **Drag & Drop**: `python drag_drop_loader.py`
2. Drag new files into window
3. Restart bot: `restart_bot.bat`

### Bulk updates:
1. **CSV method**: Update CSV file with new entries
2. **Import**: `python simple_bulk_loader.py updated.csv csv --merge`
3. **Restart**: `restart_bot.bat`

## 🛠️ Advanced Features

### Custom separators in text files:
```bash
python simple_bulk_loader.py data.txt txt --separator "|"
```

### Replace instead of merge:
```bash
python simple_bulk_loader.py data.csv csv --replace
```

### Group files by extension:
```bash
python simple_bulk_loader.py folder folder --group_by_extension
```

## 📁 File Organization Tips

### Before bulk import:
1. **Organize files** in logical folders
2. **Use consistent naming** (makes auto-titles better)
3. **Check file paths** are accessible
4. **Create backups** (auto-created but good practice)

### File path formats:
- **Absolute**: `C:\Documents\file.pdf`
- **Relative**: `files/file.pdf` 
- **Network**: `\\server\share\file.pdf`

## 🔍 Troubleshooting

### Common issues:

**"Module not found" errors:**
```bash
pip install pandas openpyxl tkinterdnd2
```

**Files not found:**
- Check file paths in CSV/text files
- Use absolute paths: `C:\full\path\to\file.pdf`
- Ensure files exist before import

**CSV encoding issues:**
- Save CSV as UTF-8
- Use text editors that support UTF-8

**Large file limits:**
- Telegram limit: 50MB per file
- Split large files or use links

### Getting help:
1. Check logs in GUI interfaces
2. Use `--verbose` flag for detailed output
3. Check backup files in `backups/` folder

## 🎉 Success Checklist

After bulk loading:
- [ ] FAQ file updated (`faq.json` has new entries)
- [ ] Files copied to `files/` directory  
- [ ] Backup created in `backups/` directory
- [ ] Bot restarted to load new data
- [ ] Test few questions in bot to verify

## 📈 Performance Tips

### For 1000+ files:
- Use **folder import** for fastest processing
- **Group by extension** to reduce FAQ entries
- Use **CSV import** for maximum control
- **Batch process** in chunks if needed

### Memory optimization:
- Process files in smaller batches
- Use simple loader for basic needs
- Clear old backups periodically

---

## 🚀 Ready to Go!

You now have everything needed to quickly load 1000+ files:

1. **Start simple**: `python simple_bulk_loader.py --templates`
2. **Fill templates** with your data
3. **Import**: `python simple_bulk_loader.py your_data.csv csv`
4. **Restart bot**: `restart_bot.bat`
5. **Test and enjoy!**

The system is designed to be as fast and simple as possible while handling large volumes efficiently. Choose the method that works best for your workflow!