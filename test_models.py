#!/usr/bin/env python
"""
Check available models and test with different ones
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from llm_client import OllamaClient
import requests

def check_models():
    try:
        resp = requests.get('http://localhost:11434/api/tags', timeout=5)
        models = resp.json().get('models', [])
        print("Available models:")
        for m in models:
            print(f"  - {m['name']}")
        return [m['name'] for m in models]
    except Exception as e:
        print(f"Error: {e}")
        return []

def test_with_model(model_name):
    from rag_engine import RAGEngine
    from data_loader import KnowledgeBase
    
    print(f"\n{'='*70}")
    print(f"Testing with model: {model_name}")
    print('='*70)
    
    kb = KnowledgeBase()
    llm = OllamaClient(model=model_name)
    rag = RAGEngine(kb=kb, llm_client=llm)
    
    query = "Details about coverage, pricing, and plan features"
    response, metadata = rag.process_query(query)
    
    print(f"Retrieved {len(metadata['retrieved_docs'])} docs")
    print(f"\nResponse preview:")
    print(response[:200] + ("..." if len(response) > 200 else ""))
    
    has_info = "pricing" in response.lower() or "coverage" in response.lower() or "features" in response.lower()
    print(f"\nHas useful info: {has_info}")

if __name__ == "__main__":
    models = check_models()
    
    for model in models[:2]:  # Test first 2 models
        try:
            test_with_model(model)
        except Exception as e:
            print(f"Error testing {model}: {e}")
