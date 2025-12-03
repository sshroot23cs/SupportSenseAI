#!/usr/bin/env python3
"""
Debug specific cleaning question
"""

from rag_engine import RAGEngine
from data_loader import KnowledgeBase
from llm_client import OllamaClient

# Initialize
kb = KnowledgeBase()
llm = OllamaClient()
rag = RAGEngine(kb, llm)

# Test query
test_query = "How do I clean my laptop safely?"

print(f"\nQuery: {test_query}")

# Get docs
docs = kb.search(test_query, top_k=3)
print(f"Retrieved {len(docs)} documents:")
for i, doc in enumerate(docs, 1):
    print(f"{i}. {doc['title']} (score: {doc['relevance_score']:.2f})")

# Check if content has cleaning info
first_doc = docs[0]['content']
print(f"\n'cleaning' in doc: {'cleaning' in first_doc.lower()}")
print(f"'microfiber' in doc: {'microfiber' in first_doc.lower()}")
print(f"'clean' in doc: {'clean' in first_doc.lower()}")

# Show snippet
idx = first_doc.lower().find('clean')
if idx >= 0:
    print(f"\nSnippet: ...{first_doc[max(0, idx-50):idx+150]}...")

# Process
response, metadata = rag.process_query(test_query)
print(f"\nResponse: {response[:300]}")
