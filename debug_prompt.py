#!/usr/bin/env python
"""
Debug script to see exactly what prompt is being sent to LLM
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from data_loader import KnowledgeBase
from rag_engine import RAGEngine
from llm_client import OllamaClient
from config import TOP_K_RESULTS

def debug_prompt():
    kb = KnowledgeBase()
    llm = OllamaClient()
    rag = RAGEngine(kb=kb, llm_client=llm)
    
    query = "Details about coverage, pricing, and plan features"
    
    # Get docs
    docs = kb.search(query, top_k=TOP_K_RESULTS)
    context = rag._build_context(docs)
    prompt = rag._create_prompt(query, context)
    
    print("=" * 70)
    print("FULL PROMPT BEING SENT TO LLM")
    print("=" * 70)
    print(prompt)
    print("\n" + "=" * 70)
    print("SENDING TO LLM...")
    print("=" * 70)
    
    response = llm.generate(prompt, stream=False, temperature=0.3, top_p=0.9)
    print(f"\nLLM Response:\n{response}")

if __name__ == "__main__":
    debug_prompt()
