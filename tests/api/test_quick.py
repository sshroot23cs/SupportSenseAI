#!/usr/bin/env python3
"""
Quick API test for SquareTrade Chat Agent
Tests basic endpoint functionality
"""
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests library not found. Install with: pip install requests")
    sys.exit(1)

BASE_URL = "http://localhost:5000"
TIMEOUT = 10


def test_quick():
    """Run quick API tests"""
    # Wait for server
    time.sleep(2)
    
    tests = [
        ("Welcome", "Hi"),
        ("Plan inquiry", "What plans do you offer?"),
        ("Pricing", "How much does it cost?"),
        ("Claim", "How do I file a claim?"),
    ]

    print("\n" + "="*60)
    print("Testing Chat Agent API - Quick Test".center(60))
    print("="*60 + "\n")

    passed = 0
    failed = 0
    
    for test_name, message in tests:
        try:
            resp = requests.post(
                f'{BASE_URL}/chat',
                json={'message': message},
                timeout=TIMEOUT
            )
            if resp.status_code == 200:
                data = resp.json()
                intent = data['metadata']['intent']
                confidence = data['metadata']['intent_confidence']
                print(f"✓ {test_name}")
                print(f"  Message: '{message}'")
                print(f"  Intent: {intent} ({confidence:.2f})")
                print(f"  Response: {data['response'][:80]}...")
                print()
                passed += 1
            else:
                print(f"✗ {test_name}: HTTP {resp.status_code}\n")
                failed += 1
        except Exception as e:
            print(f"✗ {test_name}: {e}\n")
            failed += 1

    print("="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0


if __name__ == '__main__':
    success = test_quick()
    sys.exit(0 if success else 1)
