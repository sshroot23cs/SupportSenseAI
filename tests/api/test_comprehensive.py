#!/usr/bin/env python3
"""
Comprehensive test suite for SquareTrade Chat Agent API
Tests all intent flows and API functionality
"""

import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import requests
except ImportError:
    print("Error: requests library not found. Install with: pip install requests")
    sys.exit(1)

BASE_URL = "http://localhost:5000"
TIMEOUT = 30


# ANSI colors
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(msg: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{msg:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def print_test(msg: str):
    print(f"{Colors.OKBLUE}▶ {msg}{Colors.ENDC}")


def print_pass(msg: str):
    print(f"{Colors.OKGREEN}✓ {msg}{Colors.ENDC}")


def print_fail(msg: str):
    print(f"{Colors.FAIL}✗ {msg}{Colors.ENDC}")


def print_info(msg: str):
    print(f"{Colors.OKCYAN}ℹ {msg}{Colors.ENDC}")


def test_health() -> bool:
    """Test health endpoint"""
    print_test("Testing /health endpoint")
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            print_pass(f"Health check passed: {data.get('status', 'unknown')}")
            return True
        else:
            print_fail(f"Health check failed: {resp.status_code}")
            return False
    except Exception as e:
        print_fail(f"Health check error: {e}")
        return False


def test_chat_endpoint(message: str, expected_intent: str = None) -> Tuple[bool, Dict]:
    """Test chat endpoint with a message"""
    try:
        resp = requests.post(
            f"{BASE_URL}/chat",
            json={"message": message},
            timeout=TIMEOUT
        )
        
        if resp.status_code != 200:
            print_fail(f"Chat request failed: {resp.status_code}")
            return False, {}
        
        data = resp.json()
        intent = data.get('metadata', {}).get('intent', 'unknown')
        confidence = data.get('metadata', {}).get('intent_confidence', 0)
        
        # Check if intent matches expected
        if expected_intent and intent != expected_intent:
            print_fail(f"Intent mismatch: got '{intent}', expected '{expected_intent}'")
            return False, data
        
        print_pass(f"Message: '{message}'")
        print_info(f"Intent: {intent} (confidence: {confidence:.2f})")
        print_info(f"Response: {data.get('response', '')[:100]}...")
        
        return True, data
        
    except Exception as e:
        print_fail(f"Chat request error: {e}")
        return False, {}


def test_intent_plan_inquiry() -> bool:
    """Test plan inquiry intent"""
    print_test("Testing Plan Inquiry Intent")
    success, data = test_chat_endpoint(
        "What plans do you offer?",
        expected_intent="intent_plan_inquiry"
    )
    return success


def test_intent_file_claim() -> bool:
    """Test file claim intent"""
    print_test("Testing File Claim Intent")
    success, data = test_chat_endpoint(
        "How do I file a claim?",
        expected_intent="intent_file_claim"
    )
    return success


def test_intent_pricing() -> bool:
    """Test pricing intent"""
    print_test("Testing Pricing Intent")
    success, data = test_chat_endpoint(
        "How much does it cost?",
        expected_intent="intent_pricing"
    )
    return success


def test_intent_welcome() -> bool:
    """Test welcome intent"""
    print_test("Testing Welcome Intent")
    success, data = test_chat_endpoint(
        "Hi",
        expected_intent="intent_welcome"
    )
    
    if success:
        response = data.get('response', '')
        if "protection plans" in response.lower():
            print_pass("Welcome response contains capabilities information")
            return True
        else:
            print_fail("Welcome response missing capabilities information")
            return False
    
    return success


def test_intent_contact_support() -> bool:
    """Test contact support intent"""
    print_test("Testing Contact Support Intent")
    success, data = test_chat_endpoint(
        "How do I contact support?",
        expected_intent="intent_contact_support"
    )
    return success


def test_intent_claim_status() -> bool:
    """Test claim status intent"""
    print_test("Testing Claim Status Intent")
    success, data = test_chat_endpoint(
        "Where is my claim?",
        expected_intent="intent_claim_status"
    )
    return success


def test_intent_device_replacement() -> bool:
    """Test device replacement intent"""
    print_test("Testing Device Replacement Intent")
    success, data = test_chat_endpoint(
        "Can I get a replacement device?",
        expected_intent="intent_device_replacement"
    )
    return success


def test_metadata_structure() -> bool:
    """Test response metadata structure"""
    print_test("Testing Response Metadata Structure")
    
    try:
        resp = requests.post(
            f"{BASE_URL}/chat",
            json={"message": "Hello"},
            timeout=TIMEOUT
        )
        
        if resp.status_code != 200:
            print_fail("Failed to get response")
            return False
        
        data = resp.json()
        
        # Check required fields
        required_fields = ['response', 'metadata']
        for field in required_fields:
            if field not in data:
                print_fail(f"Missing field: {field}")
                return False
        
        # Check metadata structure
        metadata = data['metadata']
        metadata_fields = ['intent', 'intent_confidence', 'user_query', 'retrieved_docs']
        for field in metadata_fields:
            if field not in metadata:
                print_fail(f"Missing metadata field: {field}")
                return False
        
        print_pass("Response structure is correct")
        print_info(f"Response fields: {', '.join(data.keys())}")
        print_info(f"Metadata fields: {', '.join(metadata.keys())}")
        
        return True
        
    except Exception as e:
        print_fail(f"Error testing metadata: {e}")
        return False


def test_session_management() -> bool:
    """Test session management across multiple requests"""
    print_test("Testing Session Management")
    
    try:
        session_id = "test-session-123"
        
        # First message
        resp1 = requests.post(
            f"{BASE_URL}/chat",
            json={
                "message": "Hi",
                "session_id": session_id,
                "user_id": "test-user"
            },
            timeout=TIMEOUT
        )
        
        if resp1.status_code != 200:
            print_fail("First message failed")
            return False
        
        # Second message in same session
        resp2 = requests.post(
            f"{BASE_URL}/chat",
            json={
                "message": "What plans do you offer?",
                "session_id": session_id,
                "user_id": "test-user"
            },
            timeout=TIMEOUT
        )
        
        if resp2.status_code != 200:
            print_fail("Second message failed")
            return False
        
        print_pass("Session management working correctly")
        print_info(f"Session ID: {session_id}")
        print_info(f"Both requests processed successfully")
        
        return True
        
    except Exception as e:
        print_fail(f"Session management error: {e}")
        return False


def test_knowledge_base_retrieval() -> bool:
    """Test knowledge base document retrieval"""
    print_test("Testing Knowledge Base Retrieval")
    
    try:
        resp = requests.post(
            f"{BASE_URL}/chat",
            json={"message": "What's covered in protection plans?"},
            timeout=TIMEOUT
        )
        
        if resp.status_code != 200:
            print_fail("Request failed")
            return False
        
        data = resp.json()
        retrieved_docs = data.get('metadata', {}).get('retrieved_docs', [])
        
        if len(retrieved_docs) > 0:
            print_pass(f"Knowledge base retrieval working: {len(retrieved_docs)} documents retrieved")
            for i, doc in enumerate(retrieved_docs[:2], 1):
                title = doc.get('title', 'Unknown')
                print_info(f"  Doc {i}: {title}")
            return True
        else:
            print_fail("No documents retrieved from knowledge base")
            return False
        
    except Exception as e:
        print_fail(f"Knowledge base retrieval error: {e}")
        return False


def main():
    """Run all tests"""
    print_header("SquareTrade Chat Agent - API Test Suite")
    
    # Wait for server to be ready
    print_info("Waiting for server to be ready...")
    max_retries = 5
    for i in range(max_retries):
        try:
            requests.get(f"{BASE_URL}/health", timeout=5)
            print_pass("Server is ready!")
            break
        except:
            if i < max_retries - 1:
                print_info(f"Retry {i+1}/{max_retries}...")
                time.sleep(1)
            else:
                print_fail("Server is not responding")
                sys.exit(1)
    
    # Run tests
    tests = [
        ("Health Check", test_health),
        ("Response Metadata Structure", test_metadata_structure),
        ("Welcome Intent", test_intent_welcome),
        ("Plan Inquiry Intent", test_intent_plan_inquiry),
        ("File Claim Intent", test_intent_file_claim),
        ("Pricing Intent", test_intent_pricing),
        ("Contact Support Intent", test_intent_contact_support),
        ("Claim Status Intent", test_intent_claim_status),
        ("Device Replacement Intent", test_intent_device_replacement),
        ("Knowledge Base Retrieval", test_knowledge_base_retrieval),
        ("Session Management", test_session_management),
    ]
    
    results = []
    for test_name, test_func in tests:
        print_header(test_name)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_fail(f"Test crashed: {e}")
            results.append((test_name, False))
        print()
    
    # Summary
    print_header("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.OKGREEN}PASS{Colors.ENDC}" if result else f"{Colors.FAIL}FAIL{Colors.ENDC}"
        print(f"  {status} - {test_name}")
    
    print()
    percentage = (passed / total * 100) if total > 0 else 0
    if passed == total:
        print_pass(f"All tests passed! ({passed}/{total} - 100%)")
        sys.exit(0)
    else:
        print_fail(f"Some tests failed: {passed}/{total} passed ({percentage:.1f}%)")
        sys.exit(1)


if __name__ == '__main__':
    main()
