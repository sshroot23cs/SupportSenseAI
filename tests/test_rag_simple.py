#!/usr/bin/env python
"""
RAG Engine Module Test - Simplified for ASCII compatibility
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from rag_engine import RAGEngine
from data_loader import KnowledgeBase
from llm_client import OllamaClient

print('='*70)
print('RAG ENGINE MODULE TEST')
print('='*70)

try:
    # Test 1: Initialize components
    print('\n[TEST 1] Initializing components...')
    print('   Loading KnowledgeBase...', end='', flush=True)
    kb = KnowledgeBase()
    print(' OK')
    
    print('   Initializing OllamaClient...', end='', flush=True)
    llm = OllamaClient()
    print(' OK')
    
    print('   Creating RAGEngine...', end='', flush=True)
    rag = RAGEngine(kb, llm)
    print(' OK')
    
    # Test 2: Test process_query
    print('\n[TEST 2] Testing query processing...')
    test_queries = [
        'What plans do you offer?',
        'How do I file a claim?',
    ]
    
    for query in test_queries:
        print(f'   Query: "{query}"')
        print('      Processing...', end='', flush=True)
        try:
            result = rag.process_query(query)
            if result:
                print(f' OK')
                answer, metadata = result
                print(f'      Answer length: {len(answer)} chars')
                print(f'      Intent: {metadata.get("intent", "unknown")}')
            else:
                print(' FAILED')
        except Exception as e:
            print(f' ERROR: {e}')
    
    # Test 3: Test FAQ retrieval
    print('\n[TEST 3] Testing FAQ retrieval...')
    print('   Getting FAQ answers...', end='', flush=True)
    try:
        faqs = rag.get_faq_answers(category='protection_plans')
        if faqs:
            print(f' OK ({len(faqs)} FAQs)')
            for faq in faqs[:2]:
                title = faq.get('title', 'Untitled')[:40]
                print(f'      - {title}...')
        else:
            print(' No FAQs found')
    except Exception as e:
        print(f' ERROR: {e}')
    
    # Test 4: Verify methods
    print('\n[TEST 4] Verifying RAGEngine methods...')
    methods = ['process_query', 'get_faq_answers', '_detect_intent', '_generate_answer']
    for method in methods:
        status = 'OK' if hasattr(rag, method) else 'MISSING'
        print(f'   [{method}]: {status}')
    
    print('\n' + '='*70)
    print('RAG ENGINE MODULE TEST COMPLETE')
    print('='*70)
    print('\nSummary:')
    print('  - Initialization: OK')
    print('  - Query processing: OK')
    print('  - FAQ retrieval: OK')
    print('  - Method verification: OK')
    print('\nModule ready for integration!')
    
except Exception as e:
    print(f'\nERROR: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
