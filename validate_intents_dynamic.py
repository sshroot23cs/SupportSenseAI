#!/usr/bin/env python3
"""
Dynamic Intent and Document Validation Script with CSV Export
Tests all intents to ensure keywords match documents and LLM can answer questions
Exports results to CSV files for analysis
"""

import json
import sys
import io
import csv
from pathlib import Path
from datetime import datetime

# Handle Unicode encoding for Windows terminal
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from rag_engine import RAGEngine
from data_loader import KnowledgeBase
from llm_client import OllamaClient

# Initialize
kb = KnowledgeBase()
llm = OllamaClient()
rag = RAGEngine(kb, llm)

# Load intents
kb_path = Path("data/intent_knowledge_base.json")
with open(kb_path, 'r') as f:
    data = json.load(f)
    intents = data.get('intents', {})
    all_docs = {doc['id']: doc for doc in data.get('documents', [])}

print(f"\n{'='*100}")
print(f"DYNAMIC INTENT AND DOCUMENT VALIDATION")
print(f"{'='*100}\n")

# Summary stats
total_intents = len(intents)
total_docs = len(all_docs)
issues_found = []
successful_tests = []
validation_results = []

print(f"Testing {total_intents} intents across {total_docs} documents\n")
print(f"{'Intent':<30} {'Keywords':<15} {'Docs':<8} {'Status':<15} {'Issue'}")
print("-" * 100)

for intent_name, intent_info in intents.items():
    keywords = intent_info.get('keywords', [])
    documents = intent_info.get('documents', [])
    
    # Skip escalation intents (they have no documents)
    if intent_name.startswith('intent_escalation') and not documents:
        print(f"{intent_name:<30} {len(keywords):<15} {len(documents):<8} {'[SKIP]':<15} (No docs expected)")
        validation_results.append({
            'intent': intent_name,
            'keywords_count': len(keywords),
            'documents_count': len(documents),
            'status': 'SKIP',
            'issue': 'No docs expected',
            'test_keyword': '',
            'detected_intent': '',
            'match': '',
            'documents_retrieved': ''
        })
        continue
    
    # Test 1: Check if intent has documents
    if not documents:
        issue = "No documents mapped"
        issues_found.append((intent_name, issue))
        print(f"{intent_name:<30} {len(keywords):<15} {len(documents):<8} {'[FAIL]':<15} {issue}")
        validation_results.append({
            'intent': intent_name,
            'keywords_count': len(keywords),
            'documents_count': len(documents),
            'status': 'FAIL',
            'issue': issue,
            'test_keyword': '',
            'detected_intent': '',
            'match': 'No',
            'documents_retrieved': ''
        })
        continue
    
    # Test 2: Check if documents exist in knowledge base
    missing_docs = [doc_id for doc_id in documents if doc_id not in all_docs]
    if missing_docs:
        issue = f"Missing docs: {missing_docs}"
        issues_found.append((intent_name, issue))
        print(f"{intent_name:<30} {len(keywords):<15} {len(documents):<8} {'[FAIL]':<15} {issue}")
        validation_results.append({
            'intent': intent_name,
            'keywords_count': len(keywords),
            'documents_count': len(documents),
            'status': 'FAIL',
            'issue': issue,
            'test_keyword': '',
            'detected_intent': '',
            'match': 'No',
            'documents_retrieved': ''
        })
        continue
    
    # Test 3: Test keyword matching with sample query
    status = "[FAIL]"
    issue = "Unknown error"
    intent_detected = ""
    retrieved_ids_str = ""
    
    if keywords:
        sample_keyword = keywords[0]
        intent_detected, confidence = rag._detect_intent(sample_keyword)
        
        if intent_detected == intent_name:
            # Test 4: Check if documents are retrieved for this keyword
            retrieved_docs = kb.search(sample_keyword, top_k=3)
            if retrieved_docs:
                # Check if any of the mapped documents are in the retrieved results
                retrieved_ids = [doc['id'] for doc in retrieved_docs]
                retrieved_ids_str = ', '.join(retrieved_ids)
                mapped_in_results = any(doc_id in retrieved_ids for doc_id in documents)
                
                if mapped_in_results:
                    status = "[PASS]"
                    issue = "OK"
                    successful_tests.append((intent_name, sample_keyword))
                else:
                    issue = f"Mapped docs not in search results. Got: {retrieved_ids[:2]}"
                    issues_found.append((intent_name, issue))
                    status = "[WARN]"
            else:
                issue = "No documents retrieved for keyword"
                issues_found.append((intent_name, issue))
                status = "[FAIL]"
        else:
            issue = f"Keyword matched '{intent_detected}' not '{intent_name}'"
            issues_found.append((intent_name, issue))
            status = "[WARN]"
            # Still get retrieved docs for CSV
            retrieved_docs = kb.search(sample_keyword, top_k=3)
            retrieved_ids_str = ', '.join([doc['id'] for doc in retrieved_docs]) if retrieved_docs else 'N/A'
    else:
        issue = "No keywords defined"
        issues_found.append((intent_name, issue))
        status = "[WARN]"
    
    validation_results.append({
        'intent': intent_name,
        'keywords_count': len(keywords),
        'documents_count': len(documents),
        'status': status.replace('[', '').replace(']', ''),
        'issue': issue,
        'test_keyword': keywords[0] if keywords else 'N/A',
        'detected_intent': intent_detected if keywords else 'N/A',
        'match': 'Yes' if keywords and intent_detected == intent_name else 'No',
        'documents_retrieved': retrieved_ids_str
    })
    
    print(f"{intent_name:<30} {len(keywords):<15} {len(documents):<8} {status:<15} {issue}")

print(f"\n{'='*100}")
print(f"SUMMARY")
print(f"{'='*100}")
print(f"PASS tests: {len(successful_tests)}/{total_intents}")
print(f"Issues found: {len(issues_found)}")

if issues_found:
    print(f"\n{'ISSUES REQUIRING ATTENTION':-^100}")
    for intent_name, issue in issues_found:
        print(f"  * {intent_name}: {issue}")

print(f"\n{'='*100}\n")

# Interactive testing section
print(f"INTERACTIVE LLM RESPONSE TESTING")
print(f"{'='*100}\n")

# Create test queries for each intent
test_queries = {
    "intent_plan_inquiry": "What plans do you offer?",
    "intent_plan_details": "What is covered in your plans?",
    "intent_help_resources": "Where can I find help?",
    "intent_blog_content": "Do you have any how-to guides?",
    "intent_pricing": "How much do plans cost?",
    "intent_file_claim": "How do I file a claim?",
    "intent_claim_status": "What's the status of my claim?",
    "intent_device_replacement": "Can I get a replacement device?",
    "intent_contact_support": "How can I contact support?",
    "intent_activation": "How do I activate a plan?",
    "intent_registration": "How do I register my plan?",
    "intent_plan_cancellation": "How do I cancel my plan?",
    "intent_faq": "What are common questions?",
    "intent_welcome": "What can you help me with?",
}

print(f"{'Query':<45} {'Intent':<30} {'Confidence':<12} {'Response Status'}")
print("-" * 100)

llm_results = []

for intent_name, query in test_queries.items():
    # Skip escalation intents for this test
    if intent_name.startswith('intent_escalation'):
        continue
    
    response, metadata = rag.process_query(query)
    
    detected_intent = metadata['intent']
    confidence = metadata['intent_confidence']
    escalated = metadata['escalated']
    
    # Determine response status
    if escalated:
        response_status = "[ESCALATED]"
    elif len(response) > 20 and "cannot" not in response.lower() and "not" not in response.lower():
        response_status = "[ANSWERED]"
    else:
        response_status = "[UNCLEAR]"
    
    match = "Yes" if detected_intent == intent_name else "No"
    
    print(f"{query:<45} {detected_intent:<30} {confidence:<12.3f} {response_status}")
    
    if detected_intent != intent_name:
        print(f"  ! Expected '{intent_name}' but got '{detected_intent}'")
    
    if escalated:
        print(f"  Reason: {metadata.get('reason', 'Unknown')}")
    
    # Collect for CSV
    llm_results.append({
        'query': query,
        'expected_intent': intent_name,
        'detected_intent': detected_intent,
        'intent_confidence': f"{confidence:.3f}",
        'intent_match': match,
        'response_status': response_status.replace('[', '').replace(']', ''),
        'escalated': 'Yes' if escalated else 'No',
        'response_length': len(response),
        'response_preview': response[:100]
    })

print(f"\n{'='*100}")
print(f"EXPORTING RESULTS TO CSV")
print(f"{'='*100}\n")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Export validation results
validation_csv = f"validation_results_{timestamp}.csv"
with open(validation_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'intent', 'keywords_count', 'documents_count', 'status', 'issue',
        'test_keyword', 'detected_intent', 'match', 'documents_retrieved'
    ])
    writer.writeheader()
    writer.writerows(validation_results)

print(f"[SAVED] Validation results: {validation_csv}")

# Export LLM response results
llm_csv = f"llm_response_results_{timestamp}.csv"
with open(llm_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'query', 'expected_intent', 'detected_intent', 'intent_confidence',
        'intent_match', 'response_status', 'escalated', 'response_length', 'response_preview'
    ])
    writer.writeheader()
    writer.writerows(llm_results)

print(f"[SAVED] LLM response results: {llm_csv}")

# Export summary statistics
summary_csv = f"validation_summary_{timestamp}.csv"
summary_stats = [
    {'metric': 'Total Intents Tested', 'value': total_intents},
    {'metric': 'Total Documents', 'value': total_docs},
    {'metric': 'Successful Tests', 'value': len(successful_tests)},
    {'metric': 'Issues Found', 'value': len(issues_found)},
    {'metric': 'Pass Rate', 'value': f"{(len(successful_tests)/total_intents)*100:.1f}%"},
    {'metric': 'LLM Tests Performed', 'value': len(llm_results)},
    {'metric': 'Correct Intent Matches', 'value': sum(1 for r in llm_results if r['intent_match'] == 'Yes')},
    {'metric': 'Intent Match Rate', 'value': f"{(sum(1 for r in llm_results if r['intent_match'] == 'Yes')/len(llm_results))*100:.1f}%" if llm_results else "0%"},
]

with open(summary_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['metric', 'value'])
    writer.writeheader()
    writer.writerows(summary_stats)

print(f"[SAVED] Summary statistics: {summary_csv}")

print(f"\nAll results exported successfully!")
print(f"{'='*100}\n")
