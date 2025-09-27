#!/bin/bash

# Cleanup script for FAQ Bot on Ubuntu VPS

echo "🧹 Cleaning up FAQ Bot files..."

# Remove Python cache files
echo "🗑️  Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Remove log files (keep model files)
echo "🗑️  Removing log files..."
rm -f cache/bot.log 2>/dev/null || true
rm -f cache/training.log 2>/dev/null || true

# Remove backup files
echo "🗑️  Removing backup files..."
rm -rf backups/* 2>/dev/null || true

echo "✅ Cleanup completed!"
echo "Note: Model files (faq_embeddings.pkl, faq_index.faiss) have been preserved"