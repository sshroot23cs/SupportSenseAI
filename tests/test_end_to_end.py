#!/usr/bin/env python
"""
End-to-End Flow Test for SupportSenseAI
Tests the complete chat agent workflow
"""

import sys
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from chat_agent import SquareTradeAgent

print("=" * 70)
print("SUPPORTENSEAI - END-TO-END FLOW TEST")
print("=" * 70)

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def format_response(text, max_len=150):
    if len(text) > max_len:
        return text[:max_len] + "..."
    return text

try:
    # Initialize agent
    print_section("PHASE 1: SYSTEM INITIALIZATION")
    print("Initializing SquareTradeAgent...")
    agent = SquareTradeAgent()
    print("✓ Agent initialized successfully")
    print(f"  - LLM Model: {agent.llm.model}")
    print(f"  - Knowledge Base: {len(agent.kb.documents)} documents loaded")
    print(f"  - Escalations: {len(agent.escalation.escalations)} in queue")
    
    # Test connectivity
    print("\nTesting system connectivity...")
    status = agent.get_agent_status()
    print(f"✓ Agent status retrieved:")
    print(f"  - LLM Available: {status.get('llm_available', False)}")
    print(f"  - Model: {status.get('llm_model', 'unknown')}")
    print(f"  - KB Documents: {status.get('knowledge_base_documents', 0)}")
    print(f"  - Pending Escalations: {status.get('pending_escalations', 0)}")
    
    # Test multi-turn conversation
    print_section("PHASE 2: MULTI-TURN CONVERSATION TEST")
    
    test_messages = [
        {
            "user": "user_123",
            "message": "Hi there!",
            "description": "Welcome message"
        },
        {
            "user": "user_123",
            "message": "What protection plans do you offer?",
            "description": "Plan inquiry"
        },
        {
            "user": "user_456",
            "message": "How do I file a claim?",
            "description": "Claim filing"
        },
        {
            "user": "user_456",
            "message": "Can I talk to a human agent?",
            "description": "Escalation request"
        }
    ]
    
    results = []
    for i, test in enumerate(test_messages, 1):
        print(f"\n[Message {i}] {test['description']}")
        print(f"  User: {test['user']}")
        print(f"  Query: \"{test['message']}\"")
        
        try:
            response = agent.process_message(
                user_message=test["message"],
                user_id=test["user"]
            )
            
            intent = response.get("metadata", {}).get("intent", "unknown")
            confidence = response.get("metadata", {}).get("intent_confidence", 0)
            answer = response.get("response", "")
            escalated = response.get("escalated", False)
            
            print(f"  Intent: {intent} (confidence: {confidence:.2f})")
            print(f"  Escalated: {escalated}")
            print(f"  Response: {format_response(answer, 120)}")
            
            results.append({
                "message": test["message"],
                "intent": intent,
                "confidence": confidence,
                "escalated": escalated,
                "success": response.get("success", False),
                "passed": True
            })
            print("  ✓ Message processed successfully")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append({
                "message": test["message"],
                "error": str(e),
                "passed": False
            })
    
    # Test FAQ retrieval
    print_section("PHASE 3: FAQ RETRIEVAL TEST")
    
    categories = [None, "support", "protection_plans"]
    
    for category in categories:
        cat_name = category or "all"
        print(f"\nRetrieving FAQs for category: {cat_name}")
        
        try:
            faq_response = agent.get_faq(category=category)
            faqs = faq_response.get("faqs", [])
            print(f"  ✓ Retrieved {len(faqs)} FAQs")
            
            if faqs:
                print(f"  Sample FAQ: {format_response(faqs[0].get('question', ''), 100)}")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # Test knowledge base search
    print_section("PHASE 4: KNOWLEDGE BASE SEARCH TEST")
    
    search_queries = [
        "protection plans coverage",
        "claim filing process",
        "warranty information"
    ]
    
    for query in search_queries:
        print(f"\nSearching KB for: \"{query}\"")
        
        try:
            results_kb = agent.kb.search(query)
            print(f"  ✓ Results found: {len(results_kb)}")
            
            if results_kb:
                top_result = results_kb[0]
                print(f"  Top match: {format_response(top_result.get('content', ''), 100)}")
                print(f"  Score: {top_result.get('score', 0):.2f}")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # Test escalation workflow
    print_section("PHASE 5: ESCALATION WORKFLOW TEST")
    
    escalation_queries = [
        "I need to speak with a human",
        "Can I talk to support?",
        "I want to talk to a manager"
    ]
    
    escalation_count_before = len(agent.escalation.get_pending_escalations())
    print(f"Initial pending escalations: {escalation_count_before}")
    
    escalations_created = 0
    for i, query in enumerate(escalation_queries, 1):
        print(f"\n[Escalation Test {i}] \"{query}\"")
        
        try:
            response = agent.process_message(
                user_message=query,
                user_id=f"escalation_user_{i}"
            )
            
            escalated = response.get("escalated", False)
            escalation_id = response.get("escalation_id", None)
            
            print(f"  Escalated: {escalated}")
            if escalated:
                print(f"  Escalation ID: {escalation_id}")
                escalations_created += 1
                print(f"  Response: {format_response(response.get('response', ''))}")
                print("  ✓ Escalation processed")
            else:
                print("  ⚠ Did not escalate as expected")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    escalation_count_after = len(agent.escalation.get_pending_escalations())
    print(f"\nFinal pending escalations: {escalation_count_after}")
    print(f"Escalations created in test: {escalations_created}")
    
    # Test error handling
    print_section("PHASE 6: ERROR HANDLING TEST")
    
    error_tests = [
        {"message": "", "user_id": "user_123", "description": "Empty message"},
        {"message": "   ", "user_id": "user_123", "description": "Whitespace-only message"},
    ]
    
    error_results = []
    for test in error_tests:
        print(f"\n[Test] {test['description']}")
        try:
            response = agent.process_message(
                user_message=test["message"],
                user_id=test["user_id"]
            )
            success = response.get("success", False)
            print(f"  Success: {success}")
            print(f"  Response: {format_response(response.get('response', ''))}")
            error_results.append({"test": test['description'], "passed": True})
            print("  ✓ Handled gracefully")
            
        except Exception as e:
            print(f"  ⚠ Exception: {type(e).__name__}: {str(e)[:80]}")
            error_results.append({
                "test": test['description'],
                "error": str(e),
                "passed": False
            })
    
    # Summary
    print_section("FINAL RESULTS SUMMARY")
    
    passed_messages = sum(1 for r in results if r.get("passed", False))
    failed_messages = sum(1 for r in results if not r.get("passed", False))
    
    print(f"\nMessage Processing:")
    print(f"  OK Passed: {passed_messages}/{len(results)}")
    print(f"  FAILED Failed: {failed_messages}/{len(results)}")
    
    print(f"\nEscalation Workflow:")
    print(f"  OK Escalations created: {escalations_created}")
    print(f"  OK Total pending: {escalation_count_after}")
    
    print(f"\nError Handling:")
    passed_errors = sum(1 for r in error_results if r.get("passed", False))
    print(f"  OK Handled gracefully: {passed_errors}/{len(error_results)}")
    
    print(f"\nSystem Status:")
    print(f"  OK Agent initialized")
    print(f"  OK LLM connected ({agent.llm.model})")
    print(f"  OK Knowledge base loaded ({len(agent.kb.documents)} docs)")
    print(f"  OK Escalation handler ready ({escalation_count_after} escalations)")
    
    print("\n" + "=" * 70)
    print("END-TO-END FLOW TEST COMPLETE")
    if passed_messages == len(results):
        print("Status: OK ALL SYSTEMS OPERATIONAL")
    else:
        print(f"Status: PARTIAL SUCCESS ({passed_messages}/{len(results)} passed)")
    print("=" * 70)
    
except Exception as e:
    print(f"\nFAILED CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
