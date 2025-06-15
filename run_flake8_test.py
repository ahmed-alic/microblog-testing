"""
Script to run flake8 directly with verbose output
"""
import subprocess
import os
import sys

print("Starting flake8 test script...")

# Get the base directory of the project
base_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(base_dir, 'app')

print(f"Project base directory: {base_dir}")
print(f"Application directory: {app_dir}")

# Check if flake8 is available
try:
    print("Checking flake8 version:")
    version_result = subprocess.run(
        ['flake8', '--version'], 
        capture_output=True, 
        text=True,
        check=True
    )
    print(f"Flake8 version: {version_result.stdout.strip()}")
except Exception as e:
    print(f"Error checking flake8 version: {e}")
    sys.exit(1)

# Run flake8 on the app directory
print(f"\nRunning flake8 on {app_dir}...")
try:
    result = subprocess.run(
        ['flake8', app_dir],
        capture_output=True,
        text=True
    )
    
    print(f"Flake8 return code: {result.returncode}")
    
    if result.stdout:
        print("\nFlake8 output:")
        print(result.stdout)
    else:
        print("\nNo output from flake8 (no violations found)")
        
    if result.stderr:
        print("\nFlake8 stderr:")
        print(result.stderr)
        
    if result.returncode == 0:
        print("\n✅ SUCCESS: No flake8 violations found!")
    else:
        print("\n❌ FAILURE: Flake8 found code style issues")
        
except Exception as e:
    print(f"Error running flake8: {e}")
    sys.exit(1)
