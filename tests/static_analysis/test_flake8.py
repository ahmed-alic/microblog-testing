import subprocess
import os
import sys
import pytest


def test_flake8_compliance():
    """
    Run flake8 on the application code to ensure 
    code quality standards are maintained.
    """
    # Get the base directory of the project
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Get the path to flake8 in the virtual environment
    flake8_path = os.path.join(base_dir, 'venv', 'Scripts', 'flake8.exe')
    
    try:
        print("Attempting to run flake8 test...")
        # Check if flake8 is in path and the executable exists
        if not os.path.exists(flake8_path):
            print(f"Flake8 executable not found at: {flake8_path}")
            pytest.skip(f"Flake8 executable not found at: {flake8_path}")
            
        try:
            print(f"Checking flake8 version using: {flake8_path}")
            subprocess.run([flake8_path, '--version'], check=True, capture_output=True, text=True)
            print("Flake8 version check passed")
        except Exception as e:
            print(f"Flake8 version check failed: {e}")
            pytest.skip(f"Flake8 version check failed: {e}")
            
        # Run flake8 and capture output
        app_dir = os.path.join(base_dir, 'app')
        print(f"Running flake8 on {app_dir}")
        result = subprocess.run(
            [flake8_path, app_dir],
            capture_output=True,
            text=True
        )
        
        # Print flake8 output for reporting purposes
        print(f"Flake8 return code: {result.returncode}")
        if result.stdout:
            print("Flake8 output:")
            print(result.stdout)
            issues_found = len(result.stdout.strip().split('\n'))
            print(f"Found {issues_found} code style issues")
        else:
            print("No code style issues found!")
            
        if result.stderr:
            print("Flake8 stderr:")
            print(result.stderr)
        
        # Report issues and fail the test if there are any
        if result.returncode != 0:
            print("\nFlake8 test failed: Code style issues must be fixed to maintain code quality.")
            print("Please fix the above issues before committing code.")
        
        # Assert that flake8 found no violations
        assert result.returncode == 0, f"Flake8 found code style issues\n{result.stdout}"
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"Exception occurred: {type(e).__name__}: {e}")
        pytest.skip(f"Flake8 not available or could not be run: {e}")
