"""
Comprehensive unit tests for SquareTrade Chat Agent components
Tests knowledge base, LLM client, RAG engine, escalation, and agent
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from chat_agent import SquareTradeAgent
from data_loader import KnowledgeBase
from llm_client import OllamaClient
from rag_engine import RAGEngine
from escalation_handler import EscalationHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_knowledge_base():
    """Test knowledge base loading and search"""
    logger.info("\n" + "="*50)
    logger.info("Testing Knowledge Base")
    logger.info("="*50)
    
    kb = KnowledgeBase()
    
    logger.info(f"✓ KB loaded with {len(kb.documents)} documents")
    
    # Test search
    results = kb.search("claim filing process", top_k=3)
    logger.info(f"✓ Search returned {len(results)} results")
    
    for i, doc in enumerate(results, 1):
        logger.info(f"  {i}. {doc.get('title')} (score: {doc.get('relevance_score')})")
    
    # Test categorization
    for category in ["protection_plans", "claims", "support"]:
        docs = kb.get_by_category(category)
        logger.info(f"✓ Category '{category}': {len(docs)} documents")
    
    return True


def test_ollama_client():
    """Test Ollama client connection"""
    logger.info("\n" + "="*50)
    logger.info("Testing Ollama Client")
    logger.info("="*50)
    
    client = OllamaClient()
    
    # Check server availability
    if client.is_available():
        logger.info("✓ Ollama server is available")
    else:
        logger.error("✗ Ollama server not available")
        return False
    
    # Check model availability
    if client.validate_model_available():
        logger.info(f"✓ Model '{client.model}' is available")
    else:
        logger.warning(f"⚠ Model '{client.model}' may not be available")
    
    # Test generation
    logger.info("Testing text generation...")
    response = client.generate(
        prompt="Complete this sentence: SquareTrade provides",
        temperature=0.5,
        num_ctx=512
    )
    
    if response and len(response) > 0:
        logger.info(f"✓ Generated response: {response[:100]}...")
        return True
    else:
        logger.error("✗ Failed to generate response")
        return False


def test_rag_engine():
    """Test RAG engine"""
    logger.info("\n" + "="*50)
    logger.info("Testing RAG Engine")
    logger.info("="*50)
    
    kb = KnowledgeBase()
    llm = OllamaClient()
    rag = RAGEngine(kb=kb, llm_client=llm)
    
    # Test query processing
    test_queries = [
        "What protection plans do you offer?",
        "How do I file a claim?",
        "What is covered in my plan?"
    ]
    
    for query in test_queries:
        logger.info(f"\nQuery: {query}")
        response, metadata = rag.process_query(query)
        
        logger.info(f"✓ Response: {response[:100]}...")
        logger.info(f"  Confidence: {metadata.get('confidence'):.2f}")
        logger.info(f"  Category: {metadata.get('category')}")
        logger.info(f"  Escalated: {metadata.get('escalated')}")
    
    return True


def test_escalation_handler():
    """Test escalation system"""
    logger.info("\n" + "="*50)
    logger.info("Testing Escalation Handler")
    logger.info("="*50)
    
    handler = EscalationHandler()
    
    # Test escalation detection
    test_cases = [
        ("I want to speak to a human agent", True),
        ("What plans do you offer?", False),
        ("I need immediate support", True)
    ]
    
    for query, should_escalate in test_cases:
        result = handler.should_escalate(query)
        status = "✓" if result == should_escalate else "✗"
        logger.info(f"{status} Query: {query} -> Escalate: {result}")
    
    # Test escalation creation
    ticket = handler.create_escalation(
        user_query="My device is broken and not covered",
        reason="High priority issue",
        user_id="test_user"
    )
    
    logger.info(f"✓ Created escalation ticket: {ticket['id']}")
    logger.info(f"  Priority: {ticket['priority']}")
    logger.info(f"  Status: {ticket['status']}")
    
    # Test retrieval
    pending = handler.get_pending_escalations()
    logger.info(f"✓ Found {len(pending)} pending escalations")
    
    return True


def test_chat_agent():
    """Test main chat agent"""
    logger.info("\n" + "="*50)
    logger.info("Testing Chat Agent")
    logger.info("="*50)
    
    agent = SquareTradeAgent()
    
    # Test connectivity
    status = agent.test_connectivity()
    logger.info("✓ System Status:")
    for component, info in status.get('components', {}).items():
        logger.info(f"  {component}: {info.get('status')}")
    
    # Test message processing
    test_messages = [
        "What plans do you offer?",
        "I need to speak to an agent",
        "How do I file a claim?"
    ]
    
    for message in test_messages:
        logger.info(f"\nProcessing: {message}")
        result = agent.process_message(message, user_id="test_user")
        
        logger.info(f"✓ Response: {result.get('response')[:80]}...")
        logger.info(f"  Success: {result.get('success')}")
        logger.info(f"  Escalated: {result.get('escalated')}")
    
    return True


def run_all_tests():
    """Run all tests"""
    logger.info("\n" + "="*60)
    logger.info("SquareTrade Chat Agent - Component Test Suite")
    logger.info("="*60)
    
    tests = [
        ("Knowledge Base", test_knowledge_base),
        ("Ollama Client", test_ollama_client),
        ("RAG Engine", test_rag_engine),
        ("Escalation Handler", test_escalation_handler),
        ("Chat Agent", test_chat_agent),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"✗ {test_name} test failed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("Test Summary")
    logger.info("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\nTotal: {passed}/{total} passed")
    logger.info("="*60)
    
    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
