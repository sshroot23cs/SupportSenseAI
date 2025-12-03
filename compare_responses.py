#!/usr/bin/env python
"""
Compare responses from debug vs agent call
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from data_loader import KnowledgeBase
from rag_engine import RAGEngine
from llm_client import OllamaClient

def test_both_methods():
    kb = KnowledgeBase()
    llm = OllamaClient()
    rag = RAGEngine(kb=kb, llm_client=llm)
    
    query = "Details about coverage, pricing, and plan features"
    
    print("=" * 80)
    print("METHOD 1: Direct LLM call (like debug_prompt.py)")
    print("=" * 80)
    
    docs1 = kb.search(query, top_k=3)
    context1 = rag._build_context(docs1)
    prompt1 = rag._create_prompt(query, context1)
    response1 = llm.generate(prompt1, stream=False, temperature=0.3, top_p=0.9)
    
    print("Retrieved docs:")
    for doc in docs1:
        print(f"  - {doc['title']}")
    print(f"\nResponse:\n{response1}\n")
    
    print("=" * 80)
    print("METHOD 2: RAG Engine call (what user sees)")
    print("=" * 80)
    
    response2, metadata = rag.process_query(query)
    
    print("Retrieved docs:")
    for doc in metadata['retrieved_docs']:
        print(f"  - {doc['title']}")
    print(f"\nResponse:\n{response2}\n")
    
    print("=" * 80)
    print("COMPARISON")
    print("=" * 80)
    print(f"Responses match: {response1.strip() == response2.strip()}")
    print(f"Method 1 has useful info: {'pricing' in response1.lower() or 'coverage' in response1.lower()}")
    print(f"Method 2 has useful info: {'pricing' in response2.lower() or 'coverage' in response2.lower()}")

if __name__ == "__main__":
    test_both_methods()
