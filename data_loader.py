"""
Knowledge base loader and manager for SquareTrade content
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from config import KNOWLEDGE_BASE_PATH, KB_CATEGORIES

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """Manages SquareTrade knowledge base"""
    
    def __init__(self, kb_path: Path = None):
        """
        Initialize knowledge base
        
        Args:
            kb_path: Path to knowledge base JSON file
        """
        self.kb_path = kb_path or KNOWLEDGE_BASE_PATH
        self.documents: List[Dict[str, Any]] = []
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        """Load knowledge base from JSON file"""
        try:
            if self.kb_path.exists():
                with open(self.kb_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Extract documents array from JSON structure
                    if isinstance(data, dict) and 'documents' in data:
                        self.documents = data['documents']
                    else:
                        self.documents = data if isinstance(data, list) else []
                logger.info(f"Loaded {len(self.documents)} documents from knowledge base")
            else:
                logger.warning(f"Knowledge base not found at {self.kb_path}")
                self.documents = self._load_sample_knowledge_base()
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
            self.documents = self._load_sample_knowledge_base()
    
    def _load_sample_knowledge_base(self) -> List[Dict[str, Any]]:
        """
        Load sample knowledge base (placeholder for actual SquareTrade content)
        In production, this would fetch from SquareTrade official resources
        """
        return [
            {
                "id": "plan_001",
                "category": "protection_plans",
                "title": "What protection plans does SquareTrade offer?",
                "content": "SquareTrade offers comprehensive protection plans for electronics including smartphones, tablets, laptops, and appliances. Plans cover accidental damage, hardware failure, and more depending on the product.",
                "keywords": ["plans", "coverage", "protection"]
            },
            {
                "id": "claim_001",
                "category": "claims",
                "title": "How to file a claim",
                "content": "To file a claim: 1) Log in to your SquareTrade account, 2) Click 'File a Claim', 3) Provide details about the issue, 4) Submit photos if required, 5) Wait for claim approval.",
                "keywords": ["claim", "file", "process"]
            },
            {
                "id": "support_001",
                "category": "support",
                "title": "What is covered under SquareTrade plans?",
                "content": "Coverage typically includes accidental damage from falls, liquid damage, hardware failure, and malfunction. Specific coverage depends on the plan selected and product type.",
                "keywords": ["coverage", "what's covered", "included"]
            },
            {
                "id": "claim_002",
                "category": "claims",
                "title": "How long does claim processing take?",
                "content": "Most claims are processed within 5-10 business days. You can track your claim status in the SquareTrade app or website using your claim number.",
                "keywords": ["claim", "processing", "time", "status"]
            },
            {
                "id": "plan_002",
                "category": "protection_plans",
                "title": "Plan pricing and options",
                "content": "SquareTrade plans start from $99 annually for basic coverage and go up to $299+ for premium plans with extended coverage. Prices vary by product type and coverage level.",
                "keywords": ["price", "cost", "plan", "affordable"]
            }
        ]
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search knowledge base for relevant documents
        Uses keyword matching and relevance scoring
        
        Args:
            query: Search query from user
            top_k: Number of top results to return
            
        Returns:
            List of relevant documents with relevance scores
        """
        results = []
        query_terms = query.lower().split()
        query_terms = [t for t in query_terms if len(t) > 2]  # Filter out short words
        
        for doc in self.documents:
            # Simple keyword matching (in production, use semantic search)
            content_lower = (doc.get('content', '') + ' ' + doc.get('title', '')).lower()
            keywords = doc.get('keywords', [])
            
            # Calculate relevance score
            score = 0
            matched_keywords = []
            
            for term in query_terms:
                # Check content match (lower weight)
                if term in content_lower:
                    score += 1
                
                # Check keyword match (higher weight)
                for keyword in keywords:
                    keyword_lower = keyword.lower()
                    if term in keyword_lower or keyword_lower in term:
                        score += 5
                        matched_keywords.append(keyword)
                        break
            
            # Bonus: Document has multiple matching keywords
            unique_matched = set(matched_keywords)
            if len(unique_matched) >= 2:
                score += 3
            
            if score > 0:
                results.append({
                    **doc,
                    'relevance_score': score
                })
        
        # Sort by relevance and return top_k
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:top_k]
    
    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all documents in a specific category"""
        return [doc for doc in self.documents if doc.get('category') == category]
    
    def add_document(self, doc: Dict[str, Any]) -> None:
        """Add a new document to the knowledge base"""
        if 'id' not in doc:
            doc['id'] = f"doc_{len(self.documents) + 1}"
        self.documents.append(doc)
        logger.info(f"Added document: {doc.get('id')}")
    
    def save_to_file(self) -> None:
        """Save knowledge base to JSON file"""
        try:
            self.kb_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.kb_path, 'w', encoding='utf-8') as f:
                json.dump(self.documents, f, indent=2, ensure_ascii=False)
            logger.info(f"Knowledge base saved to {self.kb_path}")
        except Exception as e:
            logger.error(f"Error saving knowledge base: {e}")
