#!/bin/bash

# Start script for FAQ Bot on Ubuntu VPS
# Hardware: Intel Xeon 2 GHz (1 core), 512 MB RAM, 10 GB HDD

echo "🚀 Starting FAQ Bot..."

# Change to the parent directory
cd ..

# Check if virtual environment exists
if [ ! -f "venv/bin/activate" ]; then
    echo "❌ Virtual environment not found. Run 0_Setup.sh first."
    cd Linux_Start
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Set environment variables optimized for VPS
export BATCH_SIZE=8
export CACHE_SIZE=100
export EMBEDDING_CACHE_SIZE=200

# Start the bot from the correct directory
echo "🤖 Bot is starting..."
python run_bot.py

# Change back to Linux_Start directory when script ends
cd Linux_Start