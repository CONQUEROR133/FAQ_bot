#!/bin/bash

# Status check script for FAQ Bot on Ubuntu VPS

echo "🔍 Checking FAQ Bot status..."

# Check if bot is running
if pgrep -f "python.*run_bot.py" > /dev/null; then
    echo "✅ Bot is running"
    pids=$(pgrep -f "python.*run_bot.py")
    echo "   Process IDs: $pids"
else
    echo "❌ Bot is not running"
fi

# Check disk usage
echo "💾 Disk usage:"
df -h .

# Check memory usage
echo "🧠 Memory usage:"
free -h

# Check Python version
echo "🐍 Python version:"
python3 --version

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "🔧 Virtual environment: exists"
else
    echo "⚠️  Virtual environment: not found"
fi

# Check required files
echo "📂 Required files check:"
if [ -f ".env" ]; then
    echo "   ✅ .env file: exists"
else
    echo "   ❌ .env file: missing"
fi

if [ -f "data/faq.json" ]; then
    echo "   ✅ FAQ data: exists"
else
    echo "   ❌ FAQ data: missing"
fi

if [ -f "cache/faq_embeddings.pkl" ] && [ -f "cache/faq_index.faiss" ]; then
    echo "   ✅ Model files: exist"
else
    echo "   ⚠️  Model files: missing or incomplete"
fi