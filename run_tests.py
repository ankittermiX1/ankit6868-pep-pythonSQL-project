#!/usr/bin/env python3
import subprocess
import sys
import os

def run_tests():
    # Set up the environment
    env = os.environ.copy()
    env['PYTHONPATH'] = os.path.join(os.getcwd(), 'src')
    
    try:
        # Run the test file
        result = subprocess.run([
            sys.executable, 'src/test/lab_test.py'
        ], env=env, cwd=os.getcwd())
        
        if result.returncode == 0:
            print("\n✅ ALL TESTS COMPLETED!")
        else:
            print(f"\n❌ Tests failed with return code: {result.returncode}")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)