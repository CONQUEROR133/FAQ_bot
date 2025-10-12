import re
import os

def find_russian_comments(file_path):
    """Find Russian comments in a Python file"""
    russian_comments = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines, 1):
        # Look for Russian text in comments
        if '#' in line:
            comment_part = line.split('#', 1)[1]
            if re.search(r'[а-яА-Я]', comment_part):
                russian_comments.append((i, line.strip()))
        # Look for Russian text in string literals and docstrings
        elif re.search(r'["\'].*[а-яА-Я].*["\']', line):
            russian_comments.append((i, line.strip()))
    
    return russian_comments

def scan_directory(directory):
    """Scan directory for Python files with Russian comments"""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                russian_comments = find_russian_comments(file_path)
                if russian_comments:
                    print(f"\n{file_path}:")
                    for line_num, comment in russian_comments:
                        print(f"  Line {line_num}: {comment}")

if __name__ == "__main__":
    scan_directory("src")