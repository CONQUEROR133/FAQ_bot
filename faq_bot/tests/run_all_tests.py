#!/usr/bin/env python3
"""
Main test runner to execute all FAQ bot tests
"""

import asyncio
import sys
import os
import subprocess

def run_test_script(script_name):
    """Run a test script and return success status"""
    print(f"\n🚀 Running {script_name}...")
    print("-" * 40)
    
    try:
        # Run the test script
        result = subprocess.run([
            sys.executable, 
            os.path.join(os.path.dirname(__file__), script_name)
        ], capture_output=True, text=True, timeout=30)
        
        # Print output
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"❌ {script_name} timed out")
        return False
    except Exception as e:
        print(f"❌ {script_name} failed with exception: {e}")
        return False

async def main():
    print("🧪 FAQ Bot Comprehensive Test Suite")
    print("=" * 50)
    
    # List of test scripts to run
    test_scripts = [
        "test_bot_startup.py",
        "test_faq_loading.py",
        "test_bot_handlers.py",
        "test_faq_search.py",
        "test_health_check.py"
    ]
    
    # Run all tests
    results = []
    for script in test_scripts:
        script_path = os.path.join(os.path.dirname(__file__), script)
        if os.path.exists(script_path):
            success = run_test_script(script)
            results.append((script, success))
        else:
            print(f"⚠️ {script} not found, skipping...")
            results.append((script, False))
    
    # Print summary
    print("\n" + "=" * 50)
    print("📋 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for script, success in results:
        if success:
            passed += 1
            print(f"✅ {script}")
        else:
            print(f"❌ {script}")
    
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All tests passed! The bot is ready for deployment.")
        return 0
    elif passed >= total * 0.7:
        print("⚠️ Most tests passed, but some issues need attention.")
        return 1
    else:
        print("❌ Many tests failed. Please fix the issues before deployment.")
        return 2

if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)