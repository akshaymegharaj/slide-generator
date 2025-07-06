"""
Simple test runner to verify test structure
"""
import pytest
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_tests():
    """Run all tests"""
    # Run tests with verbose output
    pytest.main(["-v", "tests/"])

if __name__ == "__main__":
    run_tests() 