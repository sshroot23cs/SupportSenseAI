#!/usr/bin/env python
"""
Test script to diagnose RAG retrieval issue
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from data_loader import KnowledgeBase
from config import TOP_K_RESULTS, CONFIDENCE_THRESHOLD

def test_search():
    kb = KnowledgeBase()
    query = "Details about coverage, pricing, and plan features"

    print("=" * 70)
    print("RAG SEARCH DIAGNOSTICS")
    print("=" * 70)
    print(f"\nQuery: {query}")
    print(f"TOP_K_RESULTS: {TOP_K_RESULTS}")
    print(f"CONFIDENCE_THRESHOLD: {CONFIDENCE_THRESHOLD}")
    print(f"\nTotal documents in KB: {len(kb.documents)}\n")

    # Show all documents and their keywords
    print("Available documents:")
    print("-" * 70)
    for doc in kb.documents:
        print(f"ID: {doc['id']}")
        print(f"Title: {doc['title']}")
        print(f"Category: {doc['category']}")
        print(f"Keywords: {doc.get('keywords', [])}")
        print()

    # Test search
    print("\n" + "=" * 70)
    print("SEARCH RESULTS")
    print("=" * 70)
    results = kb.search(query, top_k=TOP_K_RESULTS)
    print(f"\nRetrieved {len(results)} documents:\n")
    
    if not results:
        print("⚠ NO DOCUMENTS RETRIEVED!")
        print("\nDEBUG INFO:")
        print(f"Query terms: {query.lower().split()}")
        print("\nChecking individual keywords...")
        
        query_terms = query.lower().split()
        for doc in kb.documents:
            score = 0
            matching_terms = []
            content_lower = (doc.get('content', '') + ' ' + doc.get('title', '')).lower()
            keywords = doc.get('keywords', [])
            
            for term in query_terms:
                if term in content_lower:
                    score += 2
                    matching_terms.append(f"{term}(content)")
                if term in [k.lower() for k in keywords]:
                    score += 3
                    matching_terms.append(f"{term}(keyword)")
            
            print(f"\n{doc['id']}: score={score}")
            if matching_terms:
                print(f"  Matches: {', '.join(matching_terms)}")
    else:
        for i, doc in enumerate(results, 1):
            print(f"{i}. {doc['title']}")
            print(f"   ID: {doc['id']}")
            print(f"   Category: {doc['category']}")
            print(f"   Relevance Score: {doc['relevance_score']}")
            print(f"   Keywords: {doc.get('keywords', [])}")
            print()

if __name__ == "__main__":
    test_search()
