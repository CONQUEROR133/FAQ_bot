#!/bin/bash

# Start script for FAQ Bot on Ubuntu VPS
# Hardware: Intel Xeon 2 GHz (1 core), 512 MB RAM, 10 GB HDD

echo "🚀 Starting FAQ Bot..."

# Activate virtual environment
source ../venv/bin/activate

# Set environment variables optimized for VPS
export BATCH_SIZE=8
export CACHE_SIZE=100
export EMBEDDING_CACHE_SIZE=200

# Start the bot from the correct directory
echo "🤖 Bot is starting..."
cd ..
python run_bot.py
cd Linux_Start