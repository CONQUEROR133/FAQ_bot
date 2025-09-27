#!/bin/bash

# Model training script for FAQ Bot on Ubuntu VPS with limited resources
# Hardware: Intel Xeon 2 GHz (1 core), 512 MB RAM, 10 GB HDD

echo "🧠 Training model on VPS with limited resources..."

# Activate virtual environment
source venv/bin/activate

# Set environment variables optimized for VPS
export BATCH_SIZE=8
export CACHE_SIZE=100
export EMBEDDING_CACHE_SIZE=200

# Run model training with resource constraints
echo "🚀 Starting model training with optimized settings..."
python train_model.py

echo "✅ Model training completed!"