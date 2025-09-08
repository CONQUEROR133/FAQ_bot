import sys
import os
print("Python path:")
for path in sys.path:
    print(f"  {path}")

print("\nCurrent directory:", os.getcwd())
print("Files in current directory:")
for file in os.listdir('.'):
    print(f"  {file}")

try:
    from faq_loader import FAQLoader
    print("\nImport successful!")
    print(f"FAQLoader class: {FAQLoader}")
except Exception as e:
    print(f"\nImport failed with error: {e}")
    import traceback
    traceback.print_exc()