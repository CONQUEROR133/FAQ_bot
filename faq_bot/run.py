#!/usr/bin/env python3
"""
Main entry point for FAQ Bot
Cross-platform script to run the bot with different options
"""

import argparse
import subprocess
import sys
import os

def main():
    parser = argparse.ArgumentParser(description="FAQ Bot Runner")
    parser.add_argument("action", choices=["setup", "train", "start", "clean", "test", "status"], 
                        help="Action to perform")
    parser.add_argument("--dev", action="store_true", help="Install development dependencies")
    
    args = parser.parse_args()
    
    if args.action == "setup":
        # Run setup
        setup_bot(args.dev)
    elif args.action == "train":
        # Run training
        train_bot()
    elif args.action == "start":
        # Start bot
        start_bot()
    elif args.action == "clean":
        # Clean cache
        clean_cache()
    elif args.action == "test":
        # Run tests
        run_tests()
    elif args.action == "status":
        # Check status
        check_status()

def setup_bot(dev_mode=False):
    """Setup the bot environment"""
    print("🔧 Setting up FAQ Bot...")
    
    # Install dependencies
    try:
        if os.path.exists("requirements.txt"):
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        else:
            # Install key packages directly
            packages = [
                "aiogram==3.3.0",
                "sentence-transformers==2.2.2", 
                "faiss-cpu==1.7.4",
                "python-dotenv==1.1.1",
                "psutil==7.0.0"
            ]
            
            for package in packages:
                subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
                
        if dev_mode:
            # Install development dependencies
            dev_packages = ["pytest==8.4.2"]
            for package in dev_packages:
                subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
                
        print("✅ Dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False
    
    # Create directories
    dirs = ["cache", "data", "logs"]
    for dir_name in dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"✅ Created directory: {dir_name}")
    
    # Create .env if it doesn't exist
    if not os.path.exists(".env"):
        with open(".env", "w", encoding="utf-8") as f:
            f.write("""# Telegram Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here
ADMIN_ID=your_telegram_user_id_here
ACCESS_PASSWORD=your_access_password_here

# ML Model Configuration
MODEL_NAME=ai-forever/ru-en-RoSBERTa
SIMILARITY_THRESHOLD=0.66
BATCH_SIZE=16
CACHE_SIZE=500
EMBEDDING_CACHE_SIZE=1000

# Network Configuration
REQUEST_TIMEOUT=30
CONNECT_TIMEOUT=30
READ_TIMEOUT=30
MAX_RETRIES=3
RETRY_DELAY=1
""")
        print("✅ Created .env template. Please edit it with your configuration.")
    
    # Create faq.json if it doesn't exist
    if not os.path.exists("data/faq.json"):
        with open("data/faq.json", "w", encoding="utf-8") as f:
            f.write("[]")
        print("✅ Created faq.json template")
    
    print("🎉 Setup completed successfully!")
    return True

def train_bot():
    """Train the bot model"""
    print("🧠 Training FAQ Bot...")
    try:
        result = subprocess.run([sys.executable, "train_model.py"])
        if result.returncode == 0:
            print("✅ Training completed successfully!")
            return True
        else:
            print(f"❌ Training failed")
            return False
    except Exception as e:
        print(f"❌ Error during training: {e}")
        return False

def start_bot():
    """Start the bot"""
    print("🤖 Starting FAQ Bot...")
    try:
        result = subprocess.run([sys.executable, "src/main.py"])
        if result.returncode == 0:
            print("✅ Bot stopped successfully")
            return True
        else:
            print(f"❌ Bot stopped with error")
            return False
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        return False

def clean_cache():
    """Clean cache files"""
    print("🗑️ Cleaning cache...")
    import shutil
    try:
        if os.path.exists("cache"):
            shutil.rmtree("cache")
            os.makedirs("cache")
            print("✅ Cache cleaned successfully")
            return True
        else:
            print("⚠️ Cache directory not found")
            return True
    except Exception as e:
        print(f"❌ Error cleaning cache: {e}")
        return False

def run_tests():
    """Run tests"""
    print("🧪 Running tests...")
    try:
        result = subprocess.run([sys.executable, "tests/run_all_tests.py"])
        if result.returncode == 0:
            print("✅ Tests completed successfully")
            return True
        else:
            print("❌ Tests failed")
            return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def check_status():
    """Check system status"""
    print("🔍 Checking system status...")
    try:
        # Check Python
        print(f"✅ Python {sys.version}")
        
        # Check required packages
        required_packages = [
            ("aiogram", "aiogram"),
            ("sentence_transformers", "sentence-transformers"),
            ("faiss", "faiss-cpu"),
            ("dotenv", "python-dotenv"),
            ("psutil", "psutil")
        ]
        
        missing = []
        for import_name, package_name in required_packages:
            try:
                __import__(import_name)
                print(f"✅ {package_name} installed")
            except ImportError:
                missing.append(package_name)
                print(f"❌ {package_name} not installed")
        
        if missing:
            print(f"⚠️ Missing packages: {', '.join(missing)}")
            return False
        else:
            print("✅ All required packages are installed")
            return True
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return False

if __name__ == "__main__":
    main()