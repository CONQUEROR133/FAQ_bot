# 📚 FAQ Loader - Supported File Formats Guide

## ✅ **SUPPORTED FORMATS** (for FAQ text data)

### **1. 📊 CSV Files (.csv)**
**Purpose**: Spreadsheet data with FAQ questions and answers
**Example structure**:
```
query,response,category
"How to reset password?","Click Settings > Reset Password","Account"
"What is FAQ bot?","Automated question answering system","General"
```

### **2. 📈 Excel Files (.xlsx, .xls)**
**Purpose**: Microsoft Excel spreadsheets with FAQ data
**Structure**: Similar to CSV but in Excel format
- Column A: query (questions)
- Column B: response (answers)  
- Column C: category (optional)
- Additional columns for resources, links, etc.

### **3. 🔄 JSON Files (.json)**
**Purpose**: Structured data format for complex FAQ entries
**Example structure**:
```json
[
  {
    "query": "How to reset password?",
    "response": "Click Settings > Reset Password",
    "category": "Account",
    "resources": [
      {"type": "link", "url": "https://example.com/help"}
    ]
  }
]
```

### **4. 📝 Text Files (.txt)**
**Purpose**: Simple question-answer pairs
**Example format**:
```
Q: How to reset password?
A: Click Settings > Reset Password

Q: What is FAQ bot?  
A: Automated question answering system
```

---

## ❌ **NOT SUPPORTED FORMATS**

### **🖼️ Image Files (.jpg, .png, .gif, .bmp, etc.)**
**Why not supported**: 
- FAQ system processes **text data** (questions, answers, resources)
- Images contain visual data, not structured FAQ text
- Cannot extract meaningful FAQ content from images

**What to do instead**:
1. **If image contains text**: Use OCR software to extract text, then save as CSV/Excel/TXT
2. **If image is a resource**: Add image path/URL to FAQ data files as a resource
3. **For visual FAQ guides**: Create text-based FAQ entries that reference the images

---

## 💡 **How to Convert Your Data**

### **From Images with Text**:
1. Use OCR tools (Google Docs, Adobe Acrobat, online OCR)
2. Extract text from images
3. Format as CSV or Excel with query/response columns
4. Import using FAQ loader

### **From Other Documents**:
- **PDF**: Copy text to CSV/Excel
- **Word documents**: Save as text, format as FAQ pairs
- **Websites**: Copy FAQ sections to structured format

### **Creating FAQ from Scratch**:
1. Use **Option [5] Create Templates** in 4_load_files.bat
2. Edit the generated template files
3. Add your FAQ questions and answers
4. Import using the GUI

---

## 🚀 **Quick Start Guide**

1. **Run**: `4_load_files.bat`
2. **Choose**: Option [1] GUI Interface  
3. **Click**: "📄 Add Files" button
4. **Select**: Only FAQ data files (CSV, Excel, JSON, TXT)
5. **Configure**: Processing options as needed
6. **Click**: "🚀 Process Files"

---

## ❓ **Need Help?**

- **Templates**: Use option [5] in 4_load_files.bat to create example files
- **File Format**: Check examples in `templates/` folder  
- **Validation**: Use "✅ Validate Files" button before processing
- **Issues**: Check the log output for detailed error messages

**Remember**: FAQ system is designed for **text-based question-answer data**, not images or media files!