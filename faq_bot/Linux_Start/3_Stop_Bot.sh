#!/bin/bash

# Stop script for FAQ Bot on Ubuntu VPS

echo "🛑 Stopping FAQ Bot..."

# Find and kill the bot process
pids=$(pgrep -f "python.*run_bot.py")
if [ -n "$pids" ]; then
    echo " Killing bot processes: $pids"
    kill $pids
    sleep 2
    # Force kill if still running
    kill -9 $pids 2>/dev/null || true
    echo "✅ Bot stopped successfully!"
else
    echo "⚠️  No bot processes found"
fi