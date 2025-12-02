"""
Configuration and constants for SquareTrade Chat Agent
"""

import os
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent

# Ollama Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "auto")  # Will auto-detect available model
OLLAMA_TIMEOUT = 300  # seconds

# RAG Configuration
CHUNK_SIZE = 500  # Character size for knowledge base chunks
CHUNK_OVERLAP = 50  # Overlap between chunks
TOP_K_RESULTS = 3  # Number of relevant documents to retrieve

# Knowledge Base Categories
KB_CATEGORIES = {
    "protection_plans": {
        "description": "Information about SquareTrade protection plans",
        "keywords": ["plan", "coverage", "protection", "warranty"]
    },
    "claims": {
        "description": "Filing and tracking claims",
        "keywords": ["claim", "file", "coverage", "damage", "incident"]
    },
    "support": {
        "description": "General support topics",
        "keywords": ["help", "support", "faq", "guide", "how"]
    }
}

# Intent Thresholds
CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence for answering
ESCALATION_KEYWORDS = ["agent", "human", "support", "manager", "representative"]

# Response Templates
RESPONSE_TEMPLATES = {
    "answer": "Based on our knowledge base: {answer}",
    "uncertain": "I'm not entirely certain about that. Let me escalate this to our support team.",
    "out_of_scope": "I can only help with questions about SquareTrade plans, claims, and coverage. Your question seems outside my scope.",
    "escalation": "I'm connecting you with a human agent who can better assist you."
}

# Database for escalations (can be replaced with real DB)
ESCALATION_DB_PATH = PROJECT_ROOT / "data" / "escalations.json"
KNOWLEDGE_BASE_PATH = PROJECT_ROOT / "data" / "knowledge_base.json"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = PROJECT_ROOT / "logs" / "agent.log"
