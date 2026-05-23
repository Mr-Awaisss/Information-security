#!/usr/bin/env python3
"""Run all security tests and generate a report."""
import subprocess
import sys
import os
from datetime import datetime

def main():
    print("=" * 70)
    print("SECURITY TEST SUITE - Secure Password Hashing & Authentication")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Change to project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    # Run pytest with verbose output
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 'tests/', '-v', '--tb=short'],
        capture_output=False
    )
    
    print("\n" + "=" * 70)
    if result.returncode == 0:
        print("ALL TESTS PASSED (SUCCESS)")
    else:
        print("SOME TESTS FAILED (FAILURE)")
    print("=" * 70)
    
    return result.returncode

if __name__ == '__main__':
    sys.exit(main())
