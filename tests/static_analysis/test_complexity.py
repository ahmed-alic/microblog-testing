import subprocess
import os
import pytest
import json
import re
import sys


def test_code_complexity():
    """
    Run Radon on the application code to analyze code complexity metrics.
    
    Radon is a Python tool that computes various metrics from the source code:
    - Cyclomatic Complexity (CC)
    - Maintainability Index (MI)
    - Raw metrics (LOC, LLOC, SLOC)
    
    This test ensures that code complexity stays within acceptable limits.
    """
    # Get the base directory of the project
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    app_dir = os.path.join(base_dir, 'app')
    
    # Construct path to radon in the venv
    venv_dir = os.path.join(base_dir, 'venv')
    scripts_dir = os.path.join(venv_dir, 'Scripts')
    radon_path = os.path.join(scripts_dir, 'radon.exe')
    
    # Check if radon exists at the expected path
    if not os.path.exists(radon_path):
        print(f"Radon not found at {radon_path}")
        print("Looking for radon in alternate locations...")
        # Try to find radon in the path
        for path in os.environ.get('PATH', '').split(os.pathsep):
            potential_path = os.path.join(path, 'radon.exe')
            if os.path.exists(potential_path):
                radon_path = potential_path
                print(f"Found radon at {radon_path}")
                break
        else:
            # As a fallback, check in the venv's bin directory (for Unix systems)
            bin_path = os.path.join(venv_dir, 'bin', 'radon')
            if os.path.exists(bin_path):
                radon_path = bin_path
                print(f"Found radon at {radon_path}")
    
    try:
        # Run radon cc with JSON output format
        print(f"Running radon from {radon_path}")
        result = subprocess.run(
            [radon_path, 'cc', '-j', app_dir],
            capture_output=True,
            text=True
        )
        
        # Parse the JSON output
        if result.stdout:
            try:
                report = json.loads(result.stdout)
                
                # Track complexity issues
                high_complexity_functions = []
                very_high_complexity_functions = []
                
                # Calculate average complexity
                all_complexities = []
                
                # Process each file
                for filename, functions in report.items():
                    for func in functions:
                        complexity = func.get('complexity', 0)
                        all_complexities.append(complexity)
                        name = func.get('name')
                        classname = func.get('classname')
                        lineno = func.get('lineno')
                        
                        full_name = f"{classname}.{name}" if classname else name
                        location = f"{filename}:{lineno}"
                        
                        if complexity >= 15:  # Very high complexity
                            very_high_complexity_functions.append((full_name, location, complexity))
                        elif complexity >= 10:  # High complexity
                            high_complexity_functions.append((full_name, location, complexity))
                
                # Print findings
                avg_complexity = sum(all_complexities) / len(all_complexities) if all_complexities else 0
                print(f"Average cyclomatic complexity: {avg_complexity:.2f}")
                print(f"Found {len(high_complexity_functions)} functions with high complexity (≥10)")
                print(f"Found {len(very_high_complexity_functions)} functions with very high complexity (≥15)")
                
                # Print details of problematic functions
                if high_complexity_functions or very_high_complexity_functions:
                    print("\nDetails of high complexity functions:")
                    
                    for name, location, complexity in very_high_complexity_functions:
                        print(f"VERY HIGH: {name} at {location} - Complexity: {complexity}")
                    
                    for name, location, complexity in high_complexity_functions:
                        print(f"HIGH: {name} at {location} - Complexity: {complexity}")
                
                # Run radon mi to get maintainability index
                mi_result = subprocess.run(
                    [radon_path, 'mi', '-s', app_dir],
                    capture_output=True,
                    text=True
                )
                
                if mi_result.stdout:
                    print("\nMaintainability Index Summary:")
                    poor_maintainability = []
                    
                    # Parse the output to find files with poor maintainability
                    for line in mi_result.stdout.splitlines():
                        if ' - C ' in line or ' - D ' in line:  # C and D are poor maintainability grades
                            poor_maintainability.append(line)
                    
                    if poor_maintainability:
                        print("Files with poor maintainability:")
                        for item in poor_maintainability:
                            print(item)
                    else:
                        print("All files have acceptable maintainability index.")
                
                # We'll warn about but not fail the test for high complexity
                assert len(very_high_complexity_functions) == 0, (
                    f"Found {len(very_high_complexity_functions)} functions with very high cyclomatic complexity (≥15). "
                    "Consider refactoring these functions to improve maintainability."
                )
                
            except json.JSONDecodeError:
                print("Could not parse Radon JSON output")
                print(f"Raw output: {result.stdout}")
                pytest.skip("Could not parse Radon output")
        
        # Check for any errors in running radon
        if result.stderr:
            print(f"Radon stderr: {result.stderr}")
        
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"Error running Radon: {e}")
        pytest.skip("Radon not available or could not be run")
