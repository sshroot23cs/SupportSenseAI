#!/usr/bin/env python3
"""
Test blog queries with better context
"""

from rag_engine import RAGEngine
from data_loader import KnowledgeBase
from llm_client import OllamaClient

# Initialize
kb = KnowledgeBase()
llm = OllamaClient()
rag = RAGEngine(kb, llm)

# Test queries
test_queries = [
    "how-to",
    "Do you have how-to guides?",
    "Show me blog tips",
    "I want to read maintenance guides",
    "Can I learn how to maintain my device?",
]

print(f"\n{'='*80}")
print(f"Testing Blog/How-To Intent Detection")
print(f"{'='*80}\n")

for test_query in test_queries:
    print(f"Query: '{test_query}'")
    
    response, metadata = rag.process_query(test_query)
    
    print(f"  Intent: {metadata['intent']} (confidence: {metadata['intent_confidence']:.3f})")
    print(f"  Category: {metadata['category']}")
    print(f"  Final Confidence: {metadata['confidence']:.3f}")
    print(f"  Escalated: {metadata['escalated']}")
    
    if metadata['retrieved_docs']:
        docs = metadata['retrieved_docs']
        print(f"  Retrieved: {docs[0].get('title', 'Unknown')} (score: {docs[0].get('relevance_score', 0):.2f})")
    
    # Truncate response for display
    resp_truncated = response[:100].replace('\n', ' ') + "..." if len(response) > 100 else response
    print(f"  Response: {resp_truncated}")
    print()
