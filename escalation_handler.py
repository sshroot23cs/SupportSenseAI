"""
Escalation handler for routing to human agents
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from config import ESCALATION_DB_PATH, ESCALATION_KEYWORDS

logger = logging.getLogger(__name__)


class EscalationHandler:
    """Manages escalations to human support agents"""
    
    def __init__(self, db_path: Path = None):
        """
        Initialize escalation handler
        
        Args:
            db_path: Path to escalations database
        """
        self.db_path = db_path or ESCALATION_DB_PATH
        self.escalations: List[Dict[str, Any]] = []
        self._load_escalations()
    
    def _load_escalations(self):
        """Load existing escalations from file"""
        try:
            if self.db_path.exists():
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    self.escalations = json.load(f)
                logger.info(f"Loaded {len(self.escalations)} escalations")
            else:
                self.escalations = []
        except Exception as e:
            logger.error(f"Error loading escalations: {e}")
            self.escalations = []
    
    def should_escalate(self, user_query: str, confidence: float = 0.0, reason: str = None) -> bool:
        """
        Determine if query should be escalated
        
        Args:
            user_query: User's query
            confidence: Confidence score from RAG engine
            reason: Reason for potential escalation
            
        Returns:
            True if should escalate, False otherwise
        """
        # Check for explicit escalation requests
        query_lower = user_query.lower()
        for keyword in ESCALATION_KEYWORDS:
            if keyword in query_lower:
                logger.info(f"Escalation keyword detected: {keyword}")
                return True
        
        # Check confidence threshold
        if confidence < 0.5 and reason:
            logger.info(f"Low confidence escalation: {reason}")
            return True
        
        return False
    
    def create_escalation(
        self,
        user_query: str,
        reason: str,
        user_id: str = "anonymous",
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create an escalation ticket
        
        Args:
            user_query: Original user query
            reason: Reason for escalation
            user_id: User identifier
            metadata: Additional metadata
            
        Returns:
            Escalation ticket dict
        """
        escalation_id = f"ESC_{len(self.escalations) + 1:05d}"
        
        ticket = {
            "id": escalation_id,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "user_query": user_query,
            "reason": reason,
            "status": "pending",
            "assigned_to": None,
            "priority": self._calculate_priority(user_query),
            "metadata": metadata or {}
        }
        
        self.escalations.append(ticket)
        self._save_escalations()
        
        logger.info(f"Created escalation ticket: {escalation_id}")
        return ticket
    
    def _calculate_priority(self, query: str) -> str:
        """
        Calculate priority level for escalation
        
        Args:
            query: User query
            
        Returns:
            Priority level: 'low', 'medium', 'high'
        """
        query_lower = query.lower()
        
        # High priority keywords
        high_priority_words = ["urgent", "broken", "defective", "not working", "immediate", "critical"]
        if any(word in query_lower for word in high_priority_words):
            return "high"
        
        # Medium priority keywords
        medium_priority_words = ["claim", "refund", "warranty"]
        if any(word in query_lower for word in medium_priority_words):
            return "medium"
        
        return "low"
    
    def _save_escalations(self):
        """Save escalations to file"""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.escalations, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(self.escalations)} escalations")
        except Exception as e:
            logger.error(f"Error saving escalations: {e}")
    
    def get_escalation_response(self, escalation_id: str = None) -> str:
        """
        Get response template for escalation
        
        Args:
            escalation_id: ID of escalation ticket
            
        Returns:
            Escalation response message
        """
        if escalation_id:
            return f"Thank you for contacting us. Your support ticket is {escalation_id}. A human agent will assist you shortly."
        return "Connecting you with a human agent now. Your request is important to us."
    
    def get_pending_escalations(self) -> List[Dict[str, Any]]:
        """Get all pending escalation tickets"""
        return [e for e in self.escalations if e.get('status') == 'pending']
    
    def resolve_escalation(self, escalation_id: str, resolution: str = None) -> bool:
        """
        Mark escalation as resolved
        
        Args:
            escalation_id: ID of escalation ticket
            resolution: Resolution details
            
        Returns:
            True if successful, False otherwise
        """
        for ticket in self.escalations:
            if ticket['id'] == escalation_id:
                ticket['status'] = 'resolved'
                ticket['resolved_at'] = datetime.utcnow().isoformat()
                if resolution:
                    ticket['resolution'] = resolution
                self._save_escalations()
                logger.info(f"Resolved escalation: {escalation_id}")
                return True
        
        logger.warning(f"Escalation not found: {escalation_id}")
        return False
