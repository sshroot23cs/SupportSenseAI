#!/usr/bin/env python3
"""
Test full query processing for 'how-to'
"""

from rag_engine import RAGEngine
from data_loader import KnowledgeBase
from llm_client import OllamaClient
from config import CONFIDENCE_THRESHOLD

# Initialize
kb = KnowledgeBase()
llm = OllamaClient()
rag = RAGEngine(kb, llm)

# Test query
test_query = "how-to"

print(f"\n{'='*60}")
print(f"Testing query: '{test_query}'")
print(f"Confidence Threshold: {CONFIDENCE_THRESHOLD}")
print(f"{'='*60}\n")

# Process
response, metadata = rag.process_query(test_query)

print(f"Intent: {metadata['intent']}")
print(f"Intent Confidence: {metadata['intent_confidence']:.3f}")
print(f"Category: {metadata['category']}")
print(f"Retrieved Documents: {len(metadata['retrieved_docs'])}")
for doc in metadata['retrieved_docs']:
    print(f"  - {doc.get('title', 'Unknown')}: {doc.get('relevance_score', 0):.2f}")
print(f"\nFinal Confidence: {metadata['confidence']:.3f}")
print(f"Escalated: {metadata['escalated']}")
print(f"Reason: {metadata['reason']}")
print(f"\nResponse:\n{response}")
