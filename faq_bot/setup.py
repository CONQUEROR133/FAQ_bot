#!/usr/bin/env python3
"""
Cross-platform setup tool for FAQ Bot
Provides a comprehensive interface for setting up, training, and running the FAQ bot
"""

import subprocess
import sys
import os
import platform

def print_header():
    """Print the header for the setup tool"""
    print("=" * 50)
    print("           FAQ Bot Setup Tool")
    print("=" * 50)
    print()

def print_menu():
    """Print the main menu options"""
    print("Select an option:")
    print("1. Setup Bot (Install dependencies and prepare environment)")
    print("2. Train Bot (Train the ML model with your FAQ data)")
    print("3. Start Bot (Run the Telegram bot)")
    print("4. Clean Cache (Remove cached files)")
    print("5. Check Status (Verify system requirements)")
    print("6. Run Tests (Execute test suite)")
    print("0. Exit")
    print()

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    # Try installing from requirements.txt first
    if os.path.exists("requirements.txt"):
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            print("✅ Dependencies installed from requirements.txt")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install from requirements.txt")
    
    # Fallback to installing key packages
    packages = [
        "aiogram==3.3.0",
        "sentence-transformers==2.2.2", 
        "faiss-cpu==1.7.4",
        "python-dotenv==1.1.1",
        "psutil==7.0.0",
        "pytest==8.4.2"
    ]
    
    try:
        for package in packages:
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def setup_environment():
    """Set up the environment"""
    print("🔧 Setting up environment...")
    
    # Create necessary directories
    dirs = ["cache", "data", "logs"]
    for dir_name in dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"✅ Created directory: {dir_name}")
    
    # Create .env template if it doesn't exist
    if not os.path.exists(".env"):
        with open(".env", "w", encoding="utf-8") as f:
            f.write("""# Telegram Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here
ADMIN_ID=your_telegram_user_id_here
ACCESS_PASSWORD=your_access_password_here

# ML Model Configuration
MODEL_NAME=ai-forever/ru-en-RoSBERTa
SIMILARITY_THRESHOLD=0.75
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
        print("✅ Created .env template. Please edit it with your data.")
    
    # Create faq.json template if it doesn't exist
    if not os.path.exists("data/faq.json"):
        with open("data/faq.json", "w", encoding="utf-8") as f:
            f.write("[]")
        print("✅ Created faq.json template")

def run_setup():
    """Run the setup process"""
    print("🔧 Setting up bot...")
    
    try:
        # Install dependencies
        if not install_dependencies():
            return False
            
        # Set up environment
        setup_environment()
        
        print("✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit the .env file with your configuration")
        print("2. Add your FAQ data to data/faq.json")
        print("3. Run option 2 to train the bot")
        return True
        
    except Exception as e:
        print(f"❌ Error running setup: {e}")
        return False

def run_train():
    """Run the training process"""
    print("🧠 Training bot...")
    try:
        # Run the training script
        result = subprocess.run([sys.executable, "train_model.py"])
        if result.returncode == 0:
            print("✅ Training completed successfully!")
            return True
        else:
            print(f"❌ Training failed with error code {result.returncode}")
            return False
    except Exception as e:
        print(f"❌ Error running training: {e}")
        return False

def run_start():
    """Start the bot"""
    print("🤖 Starting bot...")
    try:
        # Run the main script
        result = subprocess.run([sys.executable, "src/main.py"])
        if result.returncode == 0:
            print("✅ Bot finished successfully!")
            return True
        else:
            print(f"❌ Bot stopped with error code {result.returncode}")
            return False
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        return False

def run_clean():
    """Clean cache files"""
    print("🗑️ Cleaning cache...")
    try:
        # Remove cache files
        if os.path.exists("cache"):
            shutil.rmtree("cache")
            os.makedirs("cache")
            print("✅ Cache cleaned successfully!")
            return True
        else:
            print("⚠️ Cache directory not found")
            return True
    except Exception as e:
        print(f"❌ Error cleaning cache: {e}")
        return False

def run_check_status():
    """Check system status"""
    print("🔍 Checking status...")
    try:
        # Check Python version
        print(f"✅ Python {sys.version}")
        
        # Check platform
        print(f"✅ Platform: {platform.system()} {platform.release()}")
        
        # Check dependencies
        required_packages = [
            "aiogram",
            "sentence_transformers", 
            "faiss",
            "dotenv",
            "psutil"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package} installed")
            except ImportError:
                missing_packages.append(package)
                print(f"❌ {package} not installed")
        
        if missing_packages:
            print(f"⚠️ Missing packages: {', '.join(missing_packages)}")
            return False
        else:
            print("✅ All required packages installed")
            return True
            
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return False

def run_tests():
    """Run the test suite"""
    print("🧪 Running tests...")
    try:
        # Run the test runner
        result = subprocess.run([sys.executable, "tests/run_all_tests.py"])
        if result.returncode == 0:
            print("✅ Tests completed successfully!")
            return True
        else:
            print(f"❌ Tests failed with error code {result.returncode}")
            return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def main():
    """Main function"""
    while True:
        # Clear screen (works on Windows and Unix-like systems)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print_header()
        print_menu()
        
        try:
            choice = input("Enter your choice (0-6): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                run_setup()
                input("\nPress Enter to continue...")
            elif choice == "2":
                if run_train():
                    input("\nPress Enter to continue...")
                else:
                    input("\nPress Enter to continue...")
            elif choice == "3":
                if run_start():
                    input("\nPress Enter to continue...")
                else:
                    input("\nPress Enter to continue...")
            elif choice == "4":
                if run_clean():
                    input("\nPress Enter to continue...")
                else:
                    input("\nPress Enter to continue...")
            elif choice == "5":
                if run_check_status():
                    input("\nPress Enter to continue...")
                else:
                    input("\nPress Enter to continue...")
            elif choice == "6":
                if run_tests():
                    input("\nPress Enter to continue...")
                else:
                    input("\nPress Enter to continue...")
            else:
                print("❌ Invalid choice. Please enter a number between 0-6.")
                input("\nPress Enter to continue...")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()