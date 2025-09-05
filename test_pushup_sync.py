#!/usr/bin/env python3
"""
Test script for pushup sync functionality.
This script tests the pushup extraction logic without requiring actual Strava API calls.
"""

import sys
import os
import re

# Add the run_page directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'run_page'))

# Import our pushup sync module
from pushup_sync import extract_pushup_count

def test_pushup_extraction():
    """Test the pushup extraction logic with various sample activity names."""
    
    test_cases = [
        # (activity_name, expected_count)
        ("100 pushups morning workout", 100),
        ("Push-ups: 50 reps", 50),
        ("Morning training - 75 push ups", 75),
        ("Workout with 200 pushups and other exercises", 200),
        ("25 俯卧撑 晨练", 25),  # Chinese
        ("俯卧撑: 80次", 80),   # Chinese with count
        ("Daily pushup challenge - 150", 150),
        ("Upper body workout", 0),  # No pushup count
        ("Running 5km", 0),  # Not pushup related
        ("50 PUSHUPS + cardio", 50),
        ("Pushup test: 90", 90),
    ]
    
    print("Testing pushup extraction logic:")
    print("-" * 50)
    
    all_passed = True
    for i, (activity_name, expected) in enumerate(test_cases, 1):
        # Create a mock activity object
        class MockActivity:
            def __init__(self, name):
                self.name = name
                self.description = ""
        
        activity = MockActivity(activity_name)
        actual = extract_pushup_count(activity)
        
        status = "✅ PASS" if actual == expected else "❌ FAIL"
        print(f"Test {i:2d}: {status} | '{activity_name}' → {actual} (expected {expected})")
        
        if actual != expected:
            all_passed = False
    
    print("-" * 50)
    if all_passed:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed. Check the extraction logic.")
    
    return all_passed

def test_regex_patterns():
    """Test individual regex patterns used for pushup extraction."""
    
    patterns = [
        r'(\d+)\s*push[\s-]*ups?',
        r'push[\s-]*ups?\s*[:\-]?\s*(\d+)',
        r'(\d+)\s*俯卧撑',
        r'俯卧撑\s*[:\-]?\s*(\d+)',
        r'pushup[s]?\s*[:\-]?\s*(\d+)',
        r'(\d+)\s*pushup[s]?',
    ]
    
    test_strings = [
        "100 pushups",
        "push-ups: 50",
        "75 push ups",
        "pushup 25",
        "俯卧撑 80",
        "200 俯卧撑",
    ]
    
    print("\nTesting regex patterns:")
    print("-" * 30)
    
    for pattern in patterns:
        print(f"Pattern: {pattern}")
        for test_str in test_strings:
            matches = re.findall(pattern, test_str.lower(), re.IGNORECASE)
            if matches:
                print(f"  '{test_str}' → {matches[0]}")
        print()

if __name__ == "__main__":
    print("Pushup Sync Test Suite")
    print("=" * 50)
    
    # Test the extraction logic
    success = test_pushup_extraction()
    
    # Test regex patterns
    test_regex_patterns()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)