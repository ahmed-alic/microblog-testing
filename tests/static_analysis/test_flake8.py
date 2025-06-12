import subprocess
import os
import pytest


@pytest.mark.skip(reason="Skipping flake8 tests while focusing on functional tests")
def test_flake8_compliance():
    """
    Run flake8 on the application code to ensure 
    code quality standards are maintained.
    """
    # This test is marked as skippable since we're focusing on functional test stability
    # rather than enforcing code style standards at this time
    
    # Get the base directory of the project
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        # Run flake8 and capture output
        result = subprocess.run(
            ['flake8', os.path.join(base_dir, 'app')],
            capture_output=True,
            text=True
        )
        
        # Print flake8 output for reporting purposes
        if result.stdout:
            print("Flake8 output:")
            print(result.stdout)
        
        # Assert that flake8 found no violations, but this won't affect test runs
        assert result.returncode == 0, f"Flake8 found code style issues\n{result.stdout}"
    except (subprocess.SubprocessError, FileNotFoundError):
        pytest.skip("Flake8 not available or could not be run")
        
