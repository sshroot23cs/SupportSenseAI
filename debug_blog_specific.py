#!/usr/bin/env python3
"""
Test specific blog how-to queries
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
    "How do I extend my smartphone battery life?",
    "How do I clean my laptop safely?",
    "What maintenance tips do you have for electronics?",
    "How do I transfer data to a new laptop?",
]

print(f"\n{'='*80}")
print(f"Testing Specific Blog How-To Queries")
print(f"{'='*80}\n")

for test_query in test_queries:
    print(f"Query: '{test_query}'")
    
    response, metadata = rag.process_query(test_query)
    
    print(f"  Intent: {metadata['intent']} (confidence: {metadata['intent_confidence']:.3f})")
    print(f"  Final Confidence: {metadata['confidence']:.3f}")
    print(f"  Escalated: {metadata['escalated']}")
    
    if metadata['retrieved_docs']:
        docs = metadata['retrieved_docs']
        print(f"  Retrieved: {docs[0].get('title', 'Unknown')}")
    
    print(f"  Response: {response[:200]}")
    print()
