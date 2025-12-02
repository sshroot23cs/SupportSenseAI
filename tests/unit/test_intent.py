#!/usr/bin/env python3
"""Test intent detection"""
import sys
from pathlib import Path

# Add parent directory to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from rag_engine import RAGEngine


def test_intent_detection():
    """Test intent detection"""
    print("\n" + "="*60)
    print("Testing Intent Detection")
    print("="*60 + "\n")
    
    rag = RAGEngine()

    print(f"Loaded intents: {list(rag.intents.keys())}")
    print(f"Number of intents: {len(rag.intents)}\n")

    # Test welcome intent
    test_queries = [
        "Hi",
        "Hello",
        "What can you do?",
        "Help",
        "What are your capabilities?"
    ]

    passed = 0
    failed = 0
    
    for query in test_queries:
        try:
            intent, score = rag._detect_intent(query)
            print(f"▶ Query: '{query}'")
            print(f"  Intent: {intent}")
            print(f"  Score: {score:.2f}")
            
            # Get full response
            response, metadata = rag.process_query(query)
            print(f"  Response: {response[:100]}...")
            print(f"  Intent in metadata: {metadata['intent']}")
            print(f"  Confidence: {metadata['intent_confidence']:.2f}")
            print(f"✓ Test passed\n")
            passed += 1
        except Exception as e:
            print(f"✗ Test failed: {e}\n")
            failed += 1

    print("="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0


if __name__ == '__main__':
    success = test_intent_detection()
    sys.exit(0 if success else 1)
