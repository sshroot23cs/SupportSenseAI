#!/usr/bin/env python3
"""
Debug script to capture exact LLM prompt and doc content
"""

from rag_engine import RAGEngine
from data_loader import KnowledgeBase
from llm_client import OllamaClient

# Initialize
kb = KnowledgeBase()
llm = OllamaClient()
rag = RAGEngine(kb, llm)

# Test query
test_query = "How do I extend my smartphone battery life?"

print(f"\n{'='*80}")
print(f"Debugging: {test_query}")
print(f"{'='*80}\n")

# Get intent
intent, intent_score = rag._detect_intent(test_query)
print(f"Intent: {intent} ({intent_score:.3f})")

# Get category
category = rag._detect_category(test_query)
print(f"Category: {category}")

# Get documents
docs = kb.search(test_query, top_k=3)
print(f"\nRetrieved {len(docs)} documents:")
for i, doc in enumerate(docs, 1):
    print(f"\n{i}. {doc['title']} (score: {doc['relevance_score']:.2f})")
    print(f"   Content: {doc['content'][:200]}...")

# Check if "battery" is in the first doc
if docs:
    first_doc = docs[0]['content']
    print(f"\n'battery' in doc content: {'battery' in first_doc.lower()}")
    print(f"'extend' in doc content: {'extend' in first_doc.lower()}")
    print(f"'battery life' in doc content: {'battery life' in first_doc.lower()}")
