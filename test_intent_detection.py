#!/usr/bin/env python3
"""
Test script to verify updated intent detection works with extended knowledge base
"""

import logging
from data_loader import KnowledgeBase
from rag_engine import RAGEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_intent_detection():
    """Test intent detection with various queries"""
    
    logger.info("=" * 70)
    logger.info("Testing Updated Intent Detection")
    logger.info("=" * 70)
    
    # Initialize
    kb = KnowledgeBase()
    rag = RAGEngine(kb)
    
    # Test queries focusing on family plans and new content
    test_queries = [
        # Original issue
        "Do you offer family plans",
        "Do you offer family plans for phones?",
        "Tell me about family plans",
        "What family plans are available?",
        
        # Other new intents
        "How do I access the help center?",
        "Where can I find FAQs and support?",
        "Tell me about your blog",
        "Can I cancel my plan?",
        "How do I register my plan?",
        "What are the plan features?",
        "Do you have appliance protection?",
        "Can I get furniture coverage?",
        
        # Original intents (should still work)
        "How do I file a claim?",
        "What's the status of my claim?",
        "I need device replacement",
        "How much does it cost?",
        "Tell me about your pricing",
        "How do I activate a plan?",
        "Contact support",
        "Hi there, what can you help with?"
    ]
    
    logger.info("\nTesting Intent Detection:\n")
    
    results = []
    for query in test_queries:
        intent, confidence = rag._detect_intent(query)
        results.append({
            'query': query,
            'intent': intent,
            'confidence': confidence
        })
        
        # Color code results
        if confidence >= 0.5:
            status = "✅ STRONG"
        elif confidence >= 0.3:
            status = "⚠️  MODERATE"
        else:
            status = "❌ WEAK"
        
        logger.info(f"{status} | {query}")
        logger.info(f"         → Intent: {intent} (confidence: {confidence:.2f})")
        logger.info("")
    
    # Summary
    strong_detections = sum(1 for r in results if r['confidence'] >= 0.5)
    moderate_detections = sum(1 for r in results if 0.3 <= r['confidence'] < 0.5)
    weak_detections = sum(1 for r in results if r['confidence'] < 0.3)
    
    logger.info("=" * 70)
    logger.info("Intent Detection Summary")
    logger.info("=" * 70)
    logger.info(f"Strong detections (≥0.5):   {strong_detections}/{len(results)}")
    logger.info(f"Moderate detections (0.3-0.5): {moderate_detections}/{len(results)}")
    logger.info(f"Weak detections (<0.3):    {weak_detections}/{len(results)}")
    
    # Test the specific problematic query with full pipeline
    logger.info("\n" + "=" * 70)
    logger.info("Full Pipeline Test: 'Do you offer family plans'")
    logger.info("=" * 70)
    
    problematic_query = "Do you offer family plans"
    response, metadata = rag.process_query(problematic_query)
    
    logger.info(f"Query: {problematic_query}")
    logger.info(f"Intent: {metadata['intent']}")
    logger.info(f"Intent Confidence: {metadata['intent_confidence']:.2f}")
    logger.info(f"Category: {metadata['category']}")
    logger.info(f"Documents Retrieved: {len(metadata['retrieved_docs'])}")
    
    for i, doc in enumerate(metadata['retrieved_docs'], 1):
        logger.info(f"  {i}. {doc['title']} (score: {doc.get('relevance_score', 0)})")
    
    logger.info(f"Answer: {response[:150]}...")
    
    logger.info("\n" + "=" * 70)
    logger.info("Intent Detection Test Complete")
    logger.info("=" * 70)

if __name__ == "__main__":
    test_intent_detection()
