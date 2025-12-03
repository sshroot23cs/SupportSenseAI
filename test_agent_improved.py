#!/usr/bin/env python
"""
Quick test of the agent with improved search
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from rag_engine import RAGEngine
from data_loader import KnowledgeBase
from llm_client import OllamaClient

kb = KnowledgeBase()
llm = OllamaClient()
rag = RAGEngine(kb=kb, llm_client=llm)

query = "Details about coverage, pricing, and plan features"
response, metadata = rag.process_query(query)

print("Query:", query)
print()
print("=" * 70)
print("AGENT RESPONSE:")
print("=" * 70)
print(response)
print()
print("=" * 70)
print("METADATA:")
print("=" * 70)
print("Retrieved docs:", len(metadata['retrieved_docs']))
for doc in metadata['retrieved_docs']:
    print(f"  - {doc['title']} (score: {doc['relevance_score']})")
print(f"\nConfidence: {metadata['confidence']:.2f}")
print(f"Escalated: {metadata['escalated']}")
