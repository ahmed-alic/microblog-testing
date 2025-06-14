#!/usr/bin/env python
"""
Regression Test Runner for Microblog Flask Application

This script runs the consolidated regression test suite and generates a report.
By default, it runs all tests marked with @pytest.mark.regression, but can
be configured to run only the core regression tests in test_core_regression.py.
"""
import os
import sys
import subprocess
import datetime
import argparse

def run_regression_tests(core_only=False, use_venv=True):
    """Run the regression test suite and print results"""
    print("=" * 80)
    print("MICROBLOG FLASK APPLICATION - REGRESSION TEST SUITE")
    print(f"Test Run: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Determine the Python executable to use
    python_exe = os.path.join("venv", "Scripts", "python") if use_venv else "python"
    
    # Define the command to run regression tests
    cmd = [python_exe, "-m", "pytest"]
    
    # Run either just the core regression tests or all regression-marked tests
    if core_only:
        cmd.append("tests/regression/test_core_regression.py")
    else:
        cmd.extend(["-m", "regression"])
    
    # Add verbosity and coverage options
    cmd.extend(["-v", "--cov=app", "--cov-report=term"])
    
    # Run the command and capture output
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Print the output
    print("\nTest Output:\n")
    print(result.stdout)
    
    if result.stderr:
        print("\nErrors:\n")
        print(result.stderr)
    
    # Determine if all tests passed
    success = result.returncode == 0
    
    print("\n" + "=" * 80)
    if success:
        print("[PASS] ALL REGRESSION TESTS PASSED")
    else:
        print("[FAIL] REGRESSION TESTS FAILED")
    print("=" * 80)
    
    # Generate report file
    report_dir = "test_reports"
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    test_type = "core" if core_only else "all"
    report_file = os.path.join(report_dir, f"regression_report_{test_type}_{timestamp}.txt")
    
    with open(report_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write(f"MICROBLOG FLASK APPLICATION - REGRESSION TEST REPORT\n")
        f.write(f"Test Run: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        f.write(result.stdout)
        if result.stderr:
            f.write("\nErrors:\n\n")
            f.write(result.stderr)
        f.write("\n" + "=" * 80 + "\n")
        if success:
            f.write("[PASS] ALL REGRESSION TESTS PASSED\n")
        else:
            f.write("[FAIL] REGRESSION TESTS FAILED\n")
        f.write("=" * 80 + "\n")
    
    print(f"\nDetailed test report saved to: {report_file}")
    return success

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run regression tests for Microblog Flask application")
    parser.add_argument("--core-only", action="store_true", help="Run only the core regression tests")
    parser.add_argument("--no-venv", action="store_true", help="Use system Python instead of virtual environment")
    args = parser.parse_args()
    
    # Run the tests with the specified options
    success = run_regression_tests(core_only=args.core_only, use_venv=not args.no_venv)
    sys.exit(0 if success else 1)
