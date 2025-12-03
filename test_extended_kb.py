#!/usr/bin/env python3
"""
Test script to verify the extended knowledge base works correctly
Tests queries related to new content from help center, all plans, support portal, and blog
"""

import logging
from pathlib import Path
from data_loader import KnowledgeBase
from rag_engine import RAGEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_extended_knowledge_base():
    """Test queries related to new knowledge base documents"""
    
    logger.info("=" * 70)
    logger.info("Testing Extended Knowledge Base (New Pages Integration)")
    logger.info("=" * 70)
    
    # Initialize knowledge base and RAG engine
    kb = KnowledgeBase()
    rag = RAGEngine(kb)
    
    # Verify all documents loaded
    logger.info(f"\nTotal documents in knowledge base: {len(kb.documents)}")
    for doc in kb.documents:
        logger.info(f"  - {doc['id']}: {doc['title']}")
    
    # Test queries related to new content
    test_queries = [
        # Help center queries
        "How do I use the help center to file a claim?",
        "What resources are available on the get-help page?",
        "Can you guide me through the claim process?",
        
        # Phone and family plans
        "Do you offer family plans for phones?",
        "Tell me about phone protection plan options",
        "What are the available phone plans?",
        
        # All plans (appliances, furniture)
        "Do you have protection for appliances like fridges and washers?",
        "Can I protect my furniture with SquareTrade?",
        "What coverage is available for TVs and major appliances?",
        
        # Support portal
        "Where can I find FAQs and knowledge articles?",
        "Do you offer support in Spanish?",
        "How do I access the support portal?",
        
        # Blog content
        "What helpful tips does the SquareTrade blog offer?",
        "Where can I find maintenance guides and how-to articles?",
        "Do you publish device durability testing results?",
        
        # Plan management
        "Is plan registration required?",
        "Can I cancel my plan anytime?",
        "How do I manage my account?",
        
        # Features and benefits
        "What additional benefits come with my plan?",
        "Do you offer data recovery assistance?",
        "Is theft protection available?"
    ]
    
    logger.info("\n" + "=" * 70)
    logger.info("Testing Query Processing and Retrieval")
    logger.info("=" * 70)
    
    for i, query in enumerate(test_queries, 1):
        logger.info(f"\n[Query {i}/{len(test_queries)}]")
        logger.info(f"Question: {query}")
        
        try:
            # Process query through RAG engine
            result = rag.process_query(query)
            
            logger.info(f"Detected Intent: {result['intent']} (confidence: {result['confidence']:.2f})")
            logger.info(f"Category: {result['category']}")
            logger.info(f"Retrieved Documents: {len(result['documents'])} documents")
            
            for j, doc in enumerate(result['documents'], 1):
                score = doc.get('relevance_score', 0)
                logger.info(f"  {j}. {doc['title']} (score: {score})")
            
            logger.info(f"Response Generated: {result['answer'][:100]}...")
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
    
    # Test search functionality directly
    logger.info("\n" + "=" * 70)
    logger.info("Direct Search Functionality Test")
    logger.info("=" * 70)
    
    search_tests = [
        "phone family plans",
        "appliance furniture coverage",
        "support portal FAQ Spanish",
        "blog maintenance tips",
        "plan registration cancellation",
        "help center claim filing",
        "features benefits data recovery"
    ]
    
    for search_query in search_tests:
        logger.info(f"\nSearch: '{search_query}'")
        results = kb.search(search_query, top_k=3)
        
        logger.info(f"Found {len(results)} results:")
        for result in results:
            score = result.get('relevance_score', 0)
            logger.info(f"  - {result['title']} (score: {score})")
    
    # Document category summary
    logger.info("\n" + "=" * 70)
    logger.info("Knowledge Base Summary by Category")
    logger.info("=" * 70)
    
    categories = {}
    for doc in kb.documents:
        cat = doc.get('category', 'uncategorized')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(doc['id'])
    
    for cat, doc_ids in sorted(categories.items()):
        logger.info(f"{cat}: {len(doc_ids)} documents - {', '.join(doc_ids)}")
    
    logger.info("\n" + "=" * 70)
    logger.info("Extended Knowledge Base Test Complete")
    logger.info("=" * 70)

if __name__ == "__main__":
    test_extended_knowledge_base()
