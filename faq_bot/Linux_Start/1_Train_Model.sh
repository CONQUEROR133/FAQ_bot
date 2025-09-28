#!/bin/bash

# Model training script for FAQ Bot on Ubuntu VPS with limited resources
# Hardware: Intel Xeon 2 GHz (1 core), 512 MB RAM, 10 GB HDD

echo "🧠 Training model on VPS with limited resources..."

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

# Run model training with resource constraints
echo "🚀 Starting model training with optimized settings..."
python train_model.py

# Change back to Linux_Start directory when script ends
cd Linux_Start

echo "✅ Model training completed!"