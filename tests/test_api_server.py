#!/usr/bin/env python
"""
Comprehensive API Server Test for SupportSenseAI
Tests all endpoints and agent functionality through HTTP
"""

import requests
import json
import time
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

BASE_URL = "http://localhost:5000"
MAX_RETRIES = 10
RETRY_DELAY = 1

def wait_for_server(timeout=30):
    """Wait for server to become available"""
    print("Waiting for Flask server to start...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("✓ Server is ready!")
                return True
        except Exception:
            pass
        
        time.sleep(1)
    
    print("✗ Server failed to start within timeout")
    return False

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def format_response(text, max_len=200):
    if isinstance(text, dict):
        text = str(text)
    if len(text) > max_len:
        return text[:max_len] + "..."
    return text

def test_health_endpoint():
    """Test /health endpoint"""
    print_section("TEST 1: HEALTH ENDPOINT")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health check passed")
            print(f"  Status: {data.get('status', 'unknown')}")
            print(f"  LLM Available: {data.get('llm_available', 'unknown')}")
            return True
        else:
            print(f"✗ Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_chat_endpoint():
    """Test /chat endpoint with various queries"""
    print_section("TEST 2: CHAT ENDPOINT - BASIC MESSAGES")
    
    test_cases = [
        ("Hi there!", "Welcome"),
        ("What plans do you offer?", "Plan Inquiry"),
        ("How do I file a claim?", "Claim Filing"),
        ("Can I talk to support?", "Escalation"),
    ]
    
    passed = 0
    for message, description in test_cases:
        print(f"\n[{description}] Sending: \"{message}\"")
        
        try:
            response = requests.post(
                f"{BASE_URL}/chat",
                json={"message": message},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                intent = data.get("metadata", {}).get("intent", "unknown")
                confidence = data.get("metadata", {}).get("intent_confidence", 0)
                escalated = data.get("escalated", False)
                answer = data.get("response", "")
                
                print(f"  Status: OK")
                print(f"  Intent: {intent} ({confidence:.2f})")
                print(f"  Escalated: {escalated}")
                print(f"  Response: {format_response(answer, 150)}")
                
                passed += 1
                print(f"  ✓ PASSED")
            else:
                print(f"  ✗ Status {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print(f"\nTotal: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)

def test_faq_endpoint():
    """Test /faq endpoint"""
    print_section("TEST 3: FAQ ENDPOINT")
    
    categories = [None, "protection_plans", "support"]
    passed = 0
    
    for category in categories:
        cat_name = category or "all"
        print(f"\n[Category: {cat_name}]")
        
        try:
            url = f"{BASE_URL}/faq"
            params = {"category": category} if category else {}
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                faqs = data.get("faqs", [])
                
                print(f"  Status: OK")
                print(f"  FAQs Found: {len(faqs)}")
                
                if faqs:
                    print(f"  Sample: {format_response(faqs[0].get('question', ''), 100)}")
                
                passed += 1
                print(f"  ✓ PASSED")
            else:
                print(f"  ✗ Status {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print(f"\nTotal: {passed}/{len(categories)} passed")
    return passed == len(categories)

def test_escalations_endpoint():
    """Test /escalations endpoint"""
    print_section("TEST 4: ESCALATIONS ENDPOINT")
    
    try:
        response = requests.get(f"{BASE_URL}/escalations", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            escalations = data.get("escalations", [])
            
            print(f"Status: OK")
            print(f"Escalations Found: {len(escalations)}")
            
            if escalations:
                latest = escalations[0]
                print(f"Latest Escalation: {latest.get('id', 'unknown')}")
                print(f"Status: {latest.get('status', 'unknown')}")
                print(f"Priority: {latest.get('priority', 'unknown')}")
            
            print(f"✓ PASSED")
            return True
        else:
            print(f"✗ Status {response.status_code}: {response.text[:100]}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_multi_turn_conversation():
    """Test multi-turn conversation capability"""
    print_section("TEST 5: MULTI-TURN CONVERSATION")
    
    user_id = "test_user_001"
    session_id = "session_001"
    
    messages = [
        "Hi, I need help",
        "What are your protection plans?",
        "Can I talk to someone about my claim?",
    ]
    
    passed = 0
    for i, message in enumerate(messages, 1):
        print(f"\n[Turn {i}] Sending: \"{message}\"")
        
        try:
            response = requests.post(
                f"{BASE_URL}/chat",
                json={
                    "message": message,
                    "user_id": user_id,
                    "session_id": session_id
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                intent = data.get("metadata", {}).get("intent", "unknown")
                answer = data.get("response", "")
                
                print(f"  Intent: {intent}")
                print(f"  Response: {format_response(answer, 100)}")
                print(f"  ✓ PASSED")
                
                passed += 1
            else:
                print(f"  ✗ Status {response.status_code}")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print(f"\nTotal: {passed}/{len(messages)} passed")
    return passed == len(messages)

def test_edge_cases():
    """Test edge cases and error handling"""
    print_section("TEST 6: EDGE CASES & ERROR HANDLING")
    
    edge_cases = [
        ({"message": ""}, "Empty message"),
        ({"message": "   "}, "Whitespace only"),
        ({"message": "x" * 1000}, "Very long message"),
    ]
    
    passed = 0
    for payload, description in edge_cases:
        print(f"\n[{description}]")
        
        try:
            response = requests.post(
                f"{BASE_URL}/chat",
                json=payload,
                timeout=10
            )
            
            # Should either return valid response or error status
            if response.status_code in [200, 400]:
                print(f"  Status: {response.status_code}")
                data = response.json()
                print(f"  Response: {format_response(data.get('response', 'N/A'), 100)}")
                print(f"  ✓ PASSED (Handled gracefully)")
                passed += 1
            else:
                print(f"  ✗ Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print(f"\nTotal: {passed}/{len(edge_cases)} passed")
    return passed == len(edge_cases)

def test_widget_endpoint():
    """Test /widget endpoint"""
    print_section("TEST 7: WIDGET ENDPOINT")
    
    try:
        response = requests.get(f"{BASE_URL}/widget", timeout=5)
        
        if response.status_code == 200:
            content = response.text
            print(f"Status: OK")
            print(f"HTML Size: {len(content)} bytes")
            
            if "<!DOCTYPE html>" in content or "<html" in content.lower():
                print(f"HTML Structure: Valid")
                print(f"✓ PASSED")
                return True
            else:
                print(f"⚠ May not be valid HTML")
                return False
        else:
            print(f"✗ Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("="*70)
    print("SUPPORTENSEAI - API SERVER TEST SUITE")
    print("="*70)
    
    # Wait for server
    if not wait_for_server():
        print("\n✗ Server did not start. Exiting.")
        sys.exit(1)
    
    # Run tests
    results = {}
    
    results["Health"] = test_health_endpoint()
    time.sleep(1)
    
    results["Chat"] = test_chat_endpoint()
    time.sleep(1)
    
    results["FAQ"] = test_faq_endpoint()
    time.sleep(1)
    
    results["Escalations"] = test_escalations_endpoint()
    time.sleep(1)
    
    results["MultiTurn"] = test_multi_turn_conversation()
    time.sleep(1)
    
    results["EdgeCases"] = test_edge_cases()
    time.sleep(1)
    
    results["Widget"] = test_widget_endpoint()
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "OK" if result else "FAILED"
        symbol = "OK" if result else "FAILED"
        print(f"  [{symbol}] {test_name}")
    
    print(f"\nTotal: {passed}/{total} test suites passed")
    
    if passed == total:
        print("\n✓ ALL API TESTS PASSED - SYSTEM READY FOR DEPLOYMENT")
    else:
        print(f"\n⚠ {total - passed} test suite(s) failed")
    
    print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
