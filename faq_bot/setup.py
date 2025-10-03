#!/usr/bin/env python3
"""
Simple console setup tool for FAQ Bot
Provides a straightforward interface for setting up and training the FAQ bot
"""

import subprocess
import sys
import os

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
    print("0. Exit")
    print()

def run_setup():
    """Run the setup process"""
    print("🔧 Setting up bot...")
    try:
        # Run the setup batch file
        result = subprocess.run(["0_Setup.bat"], cwd=os.getcwd(), shell=True)
        if result.returncode == 0:
            print("✅ Setup completed successfully!")
            print("\nNext steps:")
            print("1. Edit the .env file with your configuration")
            print("2. Add your FAQ data to data/faq.json")
            print("3. Run option 2 to train the bot")
        else:
            print(f"❌ Setup failed with error code {result.returncode}")
    except Exception as e:
        print(f"❌ Error running setup: {e}")
    input("\nPress Enter to continue...")

def run_train():
    """Run the training process"""
    print("🧠 Training bot...")
    try:
        # Run the training batch file
        result = subprocess.run(["4_Train_Model.bat"], cwd=os.getcwd(), shell=True)
        if result.returncode == 0:
            print("✅ Training completed successfully!")
        else:
            print(f"❌ Training failed with error code {result.returncode}")
    except Exception as e:
        print(f"❌ Error running training: {e}")
    input("\nPress Enter to continue...")

def run_start():
    """Start the bot"""
    print("🤖 Starting bot...")
    try:
        # Run the start batch file
        result = subprocess.run(["1_Start_Bot.bat"], cwd=os.getcwd(), shell=True)
        if result.returncode == 0:
            print("✅ Bot finished successfully!")
        else:
            print(f"❌ Bot stopped with error code {result.returncode}")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
    input("\nPress Enter to continue...")

def run_clean():
    """Clean cache files"""
    print("🗑️ Cleaning cache...")
    try:
        # Run the clean batch file
        result = subprocess.run(["3_Clean_All.bat"], cwd=os.getcwd(), shell=True)
        if result.returncode == 0:
            print("✅ Cache cleaned successfully!")
        else:
            print(f"❌ Cleaning failed with error code {result.returncode}")
    except Exception as e:
        print(f"❌ Error cleaning cache: {e}")
    input("\nPress Enter to continue...")

def run_check_status():
    """Check system status"""
    print("🔍 Checking status...")
    try:
        # Run the status batch file
        result = subprocess.run(["5_Check_Status.bat"], cwd=os.getcwd(), shell=True)
        if result.returncode == 0:
            print("✅ Status check completed!")
        else:
            print(f"❌ Status check failed with error code {result.returncode}")
    except Exception as e:
        print(f"❌ Error checking status: {e}")
    input("\nPress Enter to continue...")

def main():
    """Main function"""
    while True:
        # Clear screen (works on Windows)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print_header()
        print_menu()
        
        try:
            choice = input("Enter your choice (0-5): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                run_setup()
            elif choice == "2":
                run_train()
            elif choice == "3":
                run_start()
            elif choice == "4":
                run_clean()
            elif choice == "5":
                run_check_status()
            else:
                print("❌ Invalid choice. Please enter a number between 0-5.")
                input("\nPress Enter to continue...")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()