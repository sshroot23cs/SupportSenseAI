#!/usr/bin/env python3
"""
Debug script to see what context is being passed to LLM
"""

import logging
from data_loader import KnowledgeBase
from rag_engine import RAGEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

kb = KnowledgeBase()
rag = RAGEngine(kb)

query = "Do you offer family plans"

# Get search results
docs = kb.search(query, top_k=3)

logger.info("=" * 80)
logger.info(f"Query: {query}")
logger.info("=" * 80)

logger.info("\nRetrieved Documents:")
for i, doc in enumerate(docs, 1):
    logger.info(f"\n[{i}] {doc['title']} (score: {doc.get('relevance_score', 0)})")
    logger.info(f"Content: {doc['content'][:200]}...")

# Build context like RAG engine does
context = rag._build_context(docs)

logger.info("\n" + "=" * 80)
logger.info("FULL CONTEXT BEING SENT TO LLM:")
logger.info("=" * 80)
logger.info(context)

# Build prompt like RAG engine does
prompt = rag._create_prompt(query, context)

logger.info("\n" + "=" * 80)
logger.info("FULL PROMPT BEING SENT TO LLM:")
logger.info("=" * 80)
logger.info(prompt)

logger.info("\n" + "=" * 80)
logger.info("Generating answer...")
logger.info("=" * 80)

answer = rag.llm.generate(prompt=prompt, stream=False, temperature=0.3, top_p=0.9)

logger.info(f"\nLLM ANSWER:\n{answer}")
