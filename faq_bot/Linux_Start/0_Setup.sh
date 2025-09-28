#!/bin/bash

# Setup script for FAQ Bot on Ubuntu VPS
# Hardware: Intel Xeon 2 GHz (1 core), 512 MB RAM, 10 GB HDD

echo "🚀 Setting up FAQ Bot environment..."

# Update system packages
echo "🔄 Updating system packages..."
sudo apt update

# Install Python 3.8+ and pip
echo "🐍 Installing Python and pip..."
sudo apt install -y python3 python3-pip python3-venv

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt install -y build-essential libffi-dev

# Create virtual environment
echo "🔧 Creating virtual environment..."
cd ..
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install project dependencies from the correct directory
echo "📥 Installing project dependencies..."
pip install -e .
cd Linux_Start

echo "✅ Setup completed successfully!"
echo "To activate the environment, run: source ../venv/bin/activate"