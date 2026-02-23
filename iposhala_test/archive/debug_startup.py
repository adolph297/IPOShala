
import sys
import os
import traceback

# Add current dir to path
sys.path.append(os.getcwd())

try:
    print("Attempting to import iposhala_test.main...")
    from iposhala_test import main
    print("SUCCESS: Imported main")
except Exception:
    print("FAILURE: Import failed")
    traceback.print_exc()
