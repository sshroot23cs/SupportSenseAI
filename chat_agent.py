"""
Main chat agent orchestrator
"""

import logging
from typing import Dict, Any, Tuple
from datetime import datetime
from data_loader import KnowledgeBase
from llm_client import OllamaClient
from rag_engine import RAGEngine
from escalation_handler import EscalationHandler
from config import LOG_LEVEL, LOG_FILE

# Configure logging
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class SquareTradeAgent:
    """Main SquareTrade chat agent"""
    
    def __init__(self):
        """Initialize the chat agent with all components"""
        logger.info("Initializing SquareTrade Chat Agent...")
        
        # Initialize components
        self.kb = KnowledgeBase()
        self.llm = OllamaClient()
        self.rag = RAGEngine(kb=self.kb, llm_client=self.llm)
        self.escalation = EscalationHandler()
        
        # Verify LLM is available (non-blocking, with warnings only)
        try:
            if not self.llm.is_available():
                logger.warning("Ollama server may not be available (non-blocking)")
        except Exception as e:
            logger.warning(f"Could not verify Ollama availability: {e}")
        
        # Check if model is available (non-blocking, with warnings only)
        try:
            if not self.llm.validate_model_available():
                logger.warning(f"Model may not be available (non-blocking)")
        except Exception as e:
            logger.warning(f"Could not validate model: {e}")
        
        logger.info("SquareTrade Chat Agent initialized successfully")
    
    def process_message(
        self,
        user_message: str,
        user_id: str = "anonymous",
        session_id: str = None
    ) -> Dict[str, Any]:
        """
        Process user message and generate response
        
        Args:
            user_message: User's input message
            user_id: Unique user identifier
            session_id: Chat session ID for tracking
            
        Returns:
            Response dict with message, metadata, and actions
        """
        if not user_message or not user_message.strip():
            return {
                "response": "Please enter a question to get started.",
                "success": False,
                "escalated": False
            }
        
        logger.info(f"Processing message from user {user_id}: {user_message[:50]}...")
        
        # Step 1: Check if escalation is needed upfront
        if self.escalation.should_escalate(user_message):
            logger.info("Query escalated due to user request")
            ticket = self.escalation.create_escalation(
                user_query=user_message,
                reason="User requested human support",
                user_id=user_id,
                metadata={"session_id": session_id}
            )
            return {
                "response": self.escalation.get_escalation_response(ticket['id']),
                "success": True,
                "escalated": True,
                "escalation_id": ticket['id'],
                "priority": ticket['priority'],
                "metadata": {
                    "intent": "intent_escalation",
                    "intent_confidence": 1.0,
                    "user_query": user_message,
                    "retrieved_docs": [],
                    "escalation_reason": "User requested human support"
                }
            }
        
        # Step 2: Process query with RAG engine
        try:
            answer, metadata = self.rag.process_query(user_message)
            
            # Step 3: Check if answer requires escalation
            if metadata.get("escalated"):
                logger.info(f"Answer escalated: {metadata.get('reason')}")
                ticket = self.escalation.create_escalation(
                    user_query=user_message,
                    reason=metadata.get('reason', 'Unable to provide confident answer'),
                    user_id=user_id,
                    metadata={
                        "session_id": session_id,
                        "confidence": metadata.get('confidence'),
                        "category": metadata.get('category')
                    }
                )
                
                return {
                    "response": answer,
                    "success": True,
                    "escalated": True,
                    "escalation_id": ticket['id'],
                    "priority": ticket['priority'],
                    "metadata": metadata
                }
            
            # Step 4: Return confident answer with sources
            # Format sources as HTML links
            sources_html = ""
            retrieved_docs = metadata.get('retrieved_docs', [])
            if retrieved_docs:
                sources_html = "<br><br><strong>Sources:</strong><br>"
                for i, doc in enumerate(retrieved_docs, 1):
                    doc_title = doc.get('title', 'Unknown Source')
                    doc_id = doc.get('id', f'doc_{i}')
                    sources_html += f"<a href='#{doc_id}'>{i}. {doc_title}</a><br>"
            
            response_with_sources = answer + sources_html if sources_html else answer
            
            return {
                "response": response_with_sources,
                "success": True,
                "escalated": False,
                "confidence": metadata.get('confidence'),
                "category": metadata.get('category'),
                "sources": len(retrieved_docs),
                "metadata": metadata
            }
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            
            # Create escalation for errors
            ticket = self.escalation.create_escalation(
                user_query=user_message,
                reason=f"System error: {str(e)}",
                user_id=user_id,
                metadata={"session_id": session_id}
            )
            
            return {
                "response": "I encountered an error processing your request. Our support team has been notified.",
                "success": False,
                "escalated": True,
                "escalation_id": ticket['id'],
                "error": str(e)
            }
    
    def get_faq(self, category: str = None) -> Dict[str, Any]:
        """
        Get FAQ content
        
        Args:
            category: Category to filter FAQs
            
        Returns:
            FAQ data
        """
        faqs = self.rag.get_faq_answers(category=category)
        return {
            "faqs": faqs,
            "total": len(faqs),
            "category": category
        }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get agent system status"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "llm_available": self.llm.is_available(),
            "llm_model": self.llm.model,
            "knowledge_base_documents": len(self.kb.documents),
            "pending_escalations": len(self.escalation.get_pending_escalations())
        }
    
    def test_connectivity(self) -> Dict[str, Any]:
        """Test all system components"""
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "components": {}
        }
        
        # Test LLM
        try:
            is_available = self.llm.is_available()
            results["components"]["llm"] = {
                "status": "available" if is_available else "unavailable",
                "model": self.llm.model if is_available else "N/A"
            }
        except Exception as e:
            results["components"]["llm"] = {"status": "error", "error": str(e)}
        
        # Test Knowledge Base
        try:
            kb_count = len(self.kb.documents)
            results["components"]["knowledge_base"] = {
                "status": "loaded",
                "document_count": kb_count
            }
        except Exception as e:
            results["components"]["knowledge_base"] = {"status": "error", "error": str(e)}
        
        # Test Escalation System
        try:
            pending = len(self.escalation.get_pending_escalations())
            results["components"]["escalation"] = {
                "status": "operational",
                "pending_tickets": pending
            }
        except Exception as e:
            results["components"]["escalation"] = {"status": "error", "error": str(e)}
        
        return results


# Singleton instance
_agent_instance = None


def get_agent() -> SquareTradeAgent:
    """Get or create agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = SquareTradeAgent()
    return _agent_instance
