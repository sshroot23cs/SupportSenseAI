"""
RAG (Retrieval-Augmented Generation) Engine for intelligent responses
"""

import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
from data_loader import KnowledgeBase
from llm_client import OllamaClient
from config import TOP_K_RESULTS, CONFIDENCE_THRESHOLD, RESPONSE_TEMPLATES, KB_CATEGORIES, PROJECT_ROOT

logger = logging.getLogger(__name__)


class RAGEngine:
    """
    Retrieval-Augmented Generation engine
    Combines knowledge base retrieval with LLM generation
    """
    
    def __init__(self, kb: KnowledgeBase = None, llm_client: OllamaClient = None):
        """
        Initialize RAG engine
        
        Args:
            kb: KnowledgeBase instance
            llm_client: OllamaClient instance
        """
        self.kb = kb or KnowledgeBase()
        self.llm = llm_client or OllamaClient()
        self.intents = self._load_intents()
        self.dialogflows = self._load_dialogflows()
    
    def _load_intents(self) -> Dict[str, Dict]:
        """Load intent definitions from knowledge base"""
        try:
            kb_path = PROJECT_ROOT / "data" / "intent_knowledge_base.json"
            if kb_path.exists():
                with open(kb_path, 'r') as f:
                    data = json.load(f)
                    return data.get('intents', {})
        except Exception as e:
            logger.warning(f"Could not load intents: {e}")
        return {}
    
    def _load_dialogflows(self) -> Dict[str, Dict]:
        """Load dialog flow definitions"""
        try:
            df_path = PROJECT_ROOT / "data" / "dialogflows.json"
            if df_path.exists():
                with open(df_path, 'r') as f:
                    data = json.load(f)
                    return data.get('dialogflows', {})
        except Exception as e:
            logger.warning(f"Could not load dialogflows: {e}")
        return {}
    
    def _get_dialogflow_entry_message(self, intent: str) -> str:
        """Get entry message from dialog flow for intent"""
        try:
            if intent and intent in self.dialogflows:
                flow = self.dialogflows[intent]
                states = flow.get('states', [])
                if states:
                    return states[0].get('message', '')
        except Exception as e:
            logger.warning(f"Could not get dialogflow entry message: {e}")
        return None
    
    def _detect_intent(self, user_query: str) -> Tuple[str, float]:
        """
        Detect user intent from query
        Uses keyword matching with both exact and partial matching
        
        Args:
            user_query: User's question
            
        Returns:
            Tuple of (intent_name, confidence)
        """
        query_lower = user_query.lower()
        query_words = set(query_lower.split())
        
        best_intent = None
        best_score = 0.0
        
        for intent_name, intent_info in self.intents.items():
            keywords = intent_info.get('keywords', [])
            matched = 0
            
            for kw in keywords:
                kw_lower = kw.lower()
                # Exact phrase match
                if kw_lower in query_lower:
                    matched += 2
                # Partial word match (any word in keyword matches query)
                elif any(word in query_lower for word in kw_lower.split()):
                    matched += 1
            
            if matched > 0:
                score = matched / (len(keywords) * 2) if keywords else 0
                # Cap score at 1.0
                score = min(score, 1.0)
                if score > best_score:
                    best_score = score
                    best_intent = intent_name
        
        logger.info(f"Detected intent: {best_intent} (confidence: {best_score:.2f})")
        return best_intent, best_score
    
    def process_query(self, user_query: str) -> Tuple[str, Dict[str, Any]]:
        """
        Process user query and generate response
        
        Args:
            user_query: User's question
            
        Returns:
            Tuple of (response, metadata dict)
        """
        metadata = {
            "user_query": user_query,
            "category": None,
            "retrieved_docs": [],
            "confidence": 0.0,
            "escalated": False,
            "reason": None,
            "intent": None,
            "intent_confidence": 0.0
        }
        
        # Step 1: Detect user intent
        intent, intent_score = self._detect_intent(user_query)
        metadata["intent"] = intent
        metadata["intent_confidence"] = intent_score
        
        # Step 2: Detect query category
        category = self._detect_category(user_query)
        metadata["category"] = category
        
        # Step 2b: Handle welcome intent specially
        if intent and intent == "intent_welcome":
            intent_info = self.intents.get(intent, {})
            response = intent_info.get('response_template', 'Welcome to SquareTrade! How can I help you?')
            metadata["confidence"] = 1.0
            metadata["escalated"] = False
            logger.info("Welcome intent detected - returning capabilities")
            return response, metadata
        
        # Step 3: Retrieve relevant documents from knowledge base
        retrieved_docs = self.kb.search(user_query, top_k=TOP_K_RESULTS)
        metadata["retrieved_docs"] = retrieved_docs
        
        logger.info(f"Retrieved {len(retrieved_docs)} documents for query: {user_query[:50]}...")
        
        # Step 3: Check if we have enough relevant information
        if not retrieved_docs:
            response = RESPONSE_TEMPLATES["out_of_scope"]
            metadata["confidence"] = 0.0
            metadata["escalated"] = True
            metadata["reason"] = "No relevant documents found"
            logger.warning("No relevant documents found for query")
            return response, metadata
        
        # Step 4: Calculate confidence based on retrieved documents
        avg_relevance = sum(doc.get('relevance_score', 0) for doc in retrieved_docs) / len(retrieved_docs)
        confidence = min(avg_relevance / 10, 1.0)  # Normalize to 0-1
        metadata["confidence"] = confidence
        
        # Step 5: Generate response using LLM with context
        if confidence >= CONFIDENCE_THRESHOLD:
            response = self._generate_answer(user_query, retrieved_docs)
            logger.info(f"Generated answer with confidence: {confidence:.2f}")
        else:
            response = RESPONSE_TEMPLATES["uncertain"]
            metadata["escalated"] = True
            metadata["reason"] = f"Low confidence score: {confidence:.2f}"
            logger.warning(f"Low confidence ({confidence:.2f}), escalating")
        
        return response, metadata
    
    def _detect_category(self, query: str) -> str:
        """
        Detect the category of the query
        
        Args:
            query: User query
            
        Returns:
            Category name
        """
        query_lower = query.lower()
        
        for category, info in KB_CATEGORIES.items():
            for keyword in info["keywords"]:
                if keyword in query_lower:
                    return category
        
        return "support"  # default category
    
    def _generate_answer(self, user_query: str, context_docs: List[Dict[str, Any]]) -> str:
        """
        Generate answer using LLM with context from retrieved documents
        
        Args:
            user_query: Original user question
            context_docs: Retrieved context documents
            
        Returns:
            Generated answer
        """
        # Build context from retrieved documents
        context = self._build_context(context_docs)
        
        # Create prompt for LLM
        prompt = self._create_prompt(user_query, context)
        
        # Generate response from LLM
        response = self.llm.generate(
            prompt=prompt,
            stream=False,
            temperature=0.3,  # Lower temperature for factual answers
            top_p=0.9
        )
        
        return response
    
    def _build_context(self, docs: List[Dict[str, Any]]) -> str:
        """Build context string from documents"""
        context_parts = []
        for i, doc in enumerate(docs, 1):
            context_parts.append(f"Source {i}: {doc.get('title', 'Unknown')}")
            context_parts.append(doc.get('content', ''))
            context_parts.append("---")
        
        return "\n".join(context_parts)
    
    def _create_prompt(self, user_query: str, context: str) -> str:
        """
        Create a structured prompt for the LLM
        
        Args:
            user_query: User's question
            context: Retrieved context
            
        Returns:
            Formatted prompt
        """
        prompt = f"""You are a helpful SquareTrade customer support assistant. Your task is to answer the user's question using ONLY the information from the provided sources below.

IMPORTANT RULES:
1. Use ONLY information from the sources provided. Do NOT make up information.
2. If the user's question is answered in the sources, provide a clear and helpful answer.
3. If the answer is NOT in the sources, say "I don't have that information in our knowledge base."
4. Read all sources carefully before answering - the answer may be in any of the sources.

SOURCES:
{context}

USER QUESTION: {user_query}

ANSWER (use the information from sources above):"""
        
        return prompt
    
    def get_faq_answers(self, category: str = None) -> List[Dict[str, Any]]:
        """Get FAQ answers by category"""
        if category:
            docs = self.kb.get_by_category(category)
        else:
            docs = self.kb.documents
        
        return [
            {
                "question": doc.get('title'),
                "answer": doc.get('content'),
                "category": doc.get('category')
            }
            for doc in docs
        ]
