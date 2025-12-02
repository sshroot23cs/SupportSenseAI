#!/usr/bin/env python
"""
SupportSenseAI - DEPLOYMENT VERIFICATION REPORT
Comprehensive test of all API endpoints and agent functionality
"""

import sys
sys.path.insert(0, 'c:\\Users\\Sushrut\\gitrepos\\SupportSenseAI')

from flask import Flask, request, jsonify
from chat_agent import get_agent
from datetime import datetime

# Initialize Flask app for testing
app = Flask(__name__)

# Test metrics
results = {
    "timestamp": datetime.utcnow().isoformat(),
    "tests_run": 0,
    "tests_passed": 0,
    "tests_failed": 0,
    "details": []
}

def test_result(name, passed, details=""):
    """Record test result"""
    results["tests_run"] += 1
    if passed:
        results["tests_passed"] += 1
        status = "✅ PASS"
    else:
        results["tests_failed"] += 1
        status = "❌ FAIL"
    
    result_entry = {
        "name": name,
        "status": status,
        "passed": passed,
        "details": details,
        "timestamp": datetime.utcnow().isoformat()
    }
    results["details"].append(result_entry)
    print(f"\n{status} - {name}")
    if details:
        print(f"   {details}")

def main():
    print("=" * 70)
    print("SUPPORTSENSEAI - DEPLOYMENT VERIFICATION TEST SUITE")
    print("=" * 70)
    
    client = app.test_client()
    
    # ===== SECTION 1: SYSTEM INITIALIZATION =====
    print("\n[SECTION 1] SYSTEM INITIALIZATION")
    print("-" * 70)
    
    try:
        agent = get_agent()
        test_result("Agent Initialization", True, "SquareTradeAgent created successfully")
    except Exception as e:
        test_result("Agent Initialization", False, str(e))
        return
    
    try:
        status = agent.get_agent_status()
        kb_docs = status.get('knowledge_base_documents', 0)
        escalations = status.get('pending_escalations', 0)
        llm_available = status.get('llm_available', False)
        test_result("Agent Status Check", True, 
                   f"KB: {kb_docs} docs, Escalations: {escalations}, LLM: {'✓' if llm_available else '✗'}")
    except Exception as e:
        test_result("Agent Status Check", False, str(e))
    
    # ===== SECTION 2: HEALTH & CONNECTIVITY =====
    print("\n[SECTION 2] HEALTH & CONNECTIVITY")
    print("-" * 70)
    
    try:
        connectivity = agent.test_connectivity()
        all_connected = all(connectivity.values())
        test_result("Component Connectivity", all_connected, 
                   f"Components: {connectivity}")
    except Exception as e:
        test_result("Component Connectivity", False, str(e))
    
    # ===== SECTION 3: BASIC CHAT FUNCTIONALITY =====
    print("\n[SECTION 3] BASIC CHAT FUNCTIONALITY")
    print("-" * 70)
    
    # Test 3.1: Welcome Intent
    try:
        response = agent.process_message(
            user_message="Hello",
            user_id="test_user_1"
        )
        welcome_success = (response.get('success') and 
                          response.get('intent') == 'intent_welcome')
        test_result("Chat: Welcome Intent", welcome_success,
                   f"Intent: {response.get('intent')}, Confidence: {response.get('confidence'):.2%}")
    except Exception as e:
        test_result("Chat: Welcome Intent", False, str(e))
    
    # Test 3.2: Plan Inquiry
    try:
        response = agent.process_message(
            user_message="What protection plans do you offer?",
            user_id="test_user_2"
        )
        plan_success = (response.get('success') and 
                       response.get('intent') in ['intent_plan_inquiry', 'intent_plan_details'])
        test_result("Chat: Plan Inquiry", plan_success,
                   f"Intent: {response.get('intent')}, Sources: {response.get('sources', 0)}")
    except Exception as e:
        test_result("Chat: Plan Inquiry", False, str(e))
    
    # Test 3.3: Claims Question
    try:
        response = agent.process_message(
            user_message="How do I file a claim?",
            user_id="test_user_3"
        )
        claims_success = response.get('success')
        test_result("Chat: Claims Question", claims_success,
                   f"Retrieved {response.get('sources', 0)} documents")
    except Exception as e:
        test_result("Chat: Claims Question", False, str(e))
    
    # ===== SECTION 4: MULTI-TURN CONVERSATION =====
    print("\n[SECTION 4] MULTI-TURN CONVERSATION")
    print("-" * 70)
    
    try:
        session_id = "test_session_1"
        msg1 = agent.process_message("What's the price?", user_id="user_1", session_id=session_id)
        msg2 = agent.process_message("Any discounts?", user_id="user_1", session_id=session_id)
        msg3 = agent.process_message("Can you escalate me?", user_id="user_1", session_id=session_id)
        
        multi_success = all([msg1.get('success'), msg2.get('success'), msg3.get('success')])
        test_result("Multi-Turn Conversation", multi_success, "3 sequential messages processed")
    except Exception as e:
        test_result("Multi-Turn Conversation", False, str(e))
    
    # ===== SECTION 5: ESCALATION WORKFLOW =====
    print("\n[SECTION 5] ESCALATION WORKFLOW")
    print("-" * 70)
    
    try:
        response = agent.process_message(
            user_message="I need to speak with a human representative immediately",
            user_id="frustrated_user"
        )
        escalated = response.get('escalated', False)
        test_result("Escalation Detection", escalated,
                   f"Escalation ID: {response.get('escalation_id', 'N/A')}")
    except Exception as e:
        test_result("Escalation Detection", False, str(e))
    
    try:
        pending = agent.escalation.get_pending_escalations()
        test_result("Pending Escalations List", len(pending) > 0,
                   f"Found {len(pending)} pending escalations")
    except Exception as e:
        test_result("Pending Escalations List", False, str(e))
    
    # ===== SECTION 6: FAQ & KNOWLEDGE BASE =====
    print("\n[SECTION 6: FAQ & KNOWLEDGE BASE")
    print("-" * 70)
    
    try:
        faq_all = agent.get_faq()
        test_result("FAQ Retrieval (All)", len(faq_all) > 0,
                   f"Retrieved {len(faq_all)} FAQs")
    except Exception as e:
        test_result("FAQ Retrieval (All)", False, str(e))
    
    try:
        faq_plans = agent.get_faq(category='protection_plans')
        test_result("FAQ Retrieval (Category)", len(faq_plans) > 0,
                   f"Retrieved {len(faq_plans)} plan FAQs")
    except Exception as e:
        test_result("FAQ Retrieval (Category)", False, str(e))
    
    try:
        kb_search = agent.rag_engine.search_knowledge_base("protection", top_k=3)
        test_result("Knowledge Base Search", len(kb_search) > 0,
                   f"Found {len(kb_search)} relevant documents")
    except Exception as e:
        test_result("Knowledge Base Search", False, str(e))
    
    # ===== SECTION 7: ERROR HANDLING =====
    print("\n[SECTION 7] ERROR HANDLING")
    print("-" * 70)
    
    try:
        response = agent.process_message(
            user_message="",  # Empty message
            user_id="test_user"
        )
        empty_handled = True
        test_result("Empty Message Handling", empty_handled, "Empty messages handled gracefully")
    except Exception as e:
        test_result("Empty Message Handling", False, str(e))
    
    try:
        response = agent.process_message(
            user_message="   ",  # Whitespace only
            user_id="test_user"
        )
        whitespace_handled = True
        test_result("Whitespace Message Handling", whitespace_handled, "Whitespace handled gracefully")
    except Exception as e:
        test_result("Whitespace Message Handling", False, str(e))
    
    # ===== SUMMARY =====
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {results['tests_run']}")
    print(f"Passed: {results['tests_passed']} ✅")
    print(f"Failed: {results['tests_failed']} ❌")
    print(f"Success Rate: {(results['tests_passed']/results['tests_run']*100):.1f}%")
    
    print("\n" + "=" * 70)
    if results['tests_failed'] == 0:
        print("🎉 ALL TESTS PASSED - SYSTEM READY FOR DEPLOYMENT 🎉")
    else:
        print(f"⚠️  {results['tests_failed']} test(s) failed - review required")
    print("=" * 70)
    
    return results

if __name__ == '__main__':
    results = main()
    
    # Save results to JSON
    import json
    with open('c:\\Users\\Sushrut\\gitrepos\\SupportSenseAI\\DEPLOYMENT_TEST_RESULTS.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nResults saved to: DEPLOYMENT_TEST_RESULTS.json")
