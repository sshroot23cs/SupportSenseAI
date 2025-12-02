#!/usr/bin/env python3
"""
Unit tests for SquareTrade Chat Agent
Tests the agent directly without server
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from chat_agent import SquareTradeAgent


def test_agent():
    """Test agent directly"""
    print("\n" + "="*60)
    print("Direct Chat Agent Testing (No Server)")
    print("="*60 + "\n")
    
    # Initialize agent
    print("▶ Initializing agent...")
    try:
        agent = SquareTradeAgent()
        print("✓ Agent initialized successfully\n")
    except Exception as e:
        print(f"✗ Failed to initialize agent: {e}\n")
        return False
    
    # Test cases
    tests = [
        ("Welcome", "Hi"),
        ("Welcome variant", "Hello there"),
        ("Plan inquiry", "What plans do you offer?"),
        ("Pricing", "How much do your plans cost?"),
        ("File claim", "How do I file a claim?"),
        ("Claims support", "I need help with my claim"),
        ("Contact", "How do I contact support?"),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, message in tests:
        print(f"▶ Testing: {test_name}")
        print(f"  Message: '{message}'")
        
        try:
            result = agent.process_message(
                user_message=message,
                user_id="test_user",
                session_id="test_session"
            )
            
            intent = result['metadata']['intent']
            confidence = result['metadata']['intent_confidence']
            response = result['response']
            
            print(f"  Intent: {intent} ({confidence:.2f})")
            print(f"  Response: {response[:75]}...")
            print(f"✓ Test passed\n")
            passed += 1
            
        except Exception as e:
            print(f"✗ Test failed: {e}\n")
            failed += 1
    
    # Summary
    print("="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0


if __name__ == '__main__':
    success = test_agent()
    sys.exit(0 if success else 1)
