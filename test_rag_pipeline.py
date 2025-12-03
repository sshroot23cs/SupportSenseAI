#!/usr/bin/env python
"""
Test the full RAG pipeline to see where the issue is
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from rag_engine import RAGEngine
from data_loader import KnowledgeBase
from llm_client import OllamaClient
from config import TOP_K_RESULTS, CONFIDENCE_THRESHOLD

def test_rag_pipeline():
    print("=" * 70)
    print("FULL RAG PIPELINE TEST")
    print("=" * 70)
    
    kb = KnowledgeBase()
    llm = OllamaClient()
    rag = RAGEngine(kb=kb, llm_client=llm)
    
    query = "Details about coverage, pricing, and plan features"
    print(f"\nQuery: {query}\n")
    
    # Step 1: Search
    print("Step 1: Knowledge Base Search")
    print("-" * 70)
    docs = kb.search(query, top_k=TOP_K_RESULTS)
    print(f"Retrieved {len(docs)} documents:")
    for i, doc in enumerate(docs, 1):
        print(f"  {i}. {doc['title']} (score: {doc['relevance_score']})")
    
    # Step 2: Calculate confidence
    print(f"\nStep 2: Calculate Confidence")
    print("-" * 70)
    avg_relevance = sum(doc.get('relevance_score', 0) for doc in docs) / len(docs) if docs else 0
    confidence = min(avg_relevance / 10, 1.0)
    print(f"Average relevance score: {avg_relevance}")
    print(f"Calculated confidence: {confidence:.2f}")
    print(f"Confidence threshold: {CONFIDENCE_THRESHOLD}")
    print(f"Will generate answer: {confidence >= CONFIDENCE_THRESHOLD}")
    
    # Step 3: Full pipeline
    print(f"\nStep 3: Full RAG Process")
    print("-" * 70)
    response, metadata = rag.process_query(query)
    print(f"Intent: {metadata['intent']} (confidence: {metadata['intent_confidence']:.2f})")
    print(f"Category: {metadata['category']}")
    print(f"Confidence: {metadata['confidence']:.2f}")
    print(f"Escalated: {metadata['escalated']}")
    if metadata['reason']:
        print(f"Reason: {metadata['reason']}")
    print(f"\nResponse:\n{response}\n")
    
    # Step 4: Show why specific docs weren't returned
    print(f"\nStep 4: Why weren't other relevant docs retrieved?")
    print("-" * 70)
    all_results = kb.search(query, top_k=len(kb.documents))
    missing_docs = all_results[len(docs):]
    print(f"Retrieved: {len(docs)}, Total matches: {len(all_results)}, Missing: {len(missing_docs)}")
    if missing_docs:
        print("\nDocuments that matched but weren't in top 3:")
        for doc in missing_docs:
            print(f"  - {doc['title']} (score: {doc['relevance_score']})")

if __name__ == "__main__":
    test_rag_pipeline()
