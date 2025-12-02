"""
Ollama LLM client for interacting with local language model
"""

import logging
import requests
import json
from typing import Optional, Dict, Any
from config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for communicating with Ollama LLM"""
    
    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = OLLAMA_MODEL):
        """
        Initialize Ollama client
        
        Args:
            base_url: Ollama server URL
            model: Model name to use
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.generate_endpoint = f"{self.base_url}/api/chat"
        self.embedding_endpoint = f"{self.base_url}/api/embeddings"
        self._model_detected = False
    
    def is_available(self) -> bool:
        """Check if Ollama server is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama server not available: {e}")
            return False
    
    def _detect_model(self):
        """Auto-detect and use best available model"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                if models:
                    available_names = [m['name'] for m in models]
                    # Prefer gemma:2b if available, then gemma, then others
                    for preferred in ['gemma:2b', 'gemma', 'mistral', 'llama2', 'neural-chat']:
                        for available in available_names:
                            if preferred in available:
                                self.model = available
                                logger.info(f"Auto-detected model: {self.model}")
                                return
                    # Use first available model if no preference match
                    self.model = available_names[0]
                    logger.info(f"Using first available model: {self.model}")
        except Exception as e:
            logger.warning(f"Could not auto-detect model: {e}, using: {self.model}")
    
    def generate(
        self,
        prompt: str,
        stream: bool = False,
        temperature: float = 0.7,
        top_p: float = 0.9,
        num_ctx: int = 2048
    ) -> str:
        """
        Generate text using Ollama
        
        Args:
            prompt: Input prompt
            stream: Whether to stream response
            temperature: Sampling temperature (0-2, higher = more creative)
            top_p: Nucleus sampling parameter
            num_ctx: Context window size
            
        Returns:
            Generated text response
        """
        # Detect model on first use
        if not self._model_detected:
            self._detect_model()
            self._model_detected = True
            
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "stream": stream,
                "options": {
                    "temperature": temperature,
                    "top_p": top_p,
                    "num_ctx": num_ctx
                }
            }
            
            response = requests.post(
                self.generate_endpoint,
                json=payload,
                timeout=OLLAMA_TIMEOUT
            )
            response.raise_for_status()
            
            if stream:
                return self._handle_streaming_response(response)
            else:
                result = response.json()
                return result.get('message', {}).get('content', '').strip()
        
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            return "I'm experiencing delays. Please try again."
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama server")
            return "Service temporarily unavailable. Please try again."
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            return "An error occurred while processing your request."
    
    def _handle_streaming_response(self, response: requests.Response) -> str:
        """Handle streaming response from Ollama"""
        result = ""
        try:
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    result += data.get('response', '')
            return result.strip()
        except Exception as e:
            logger.error(f"Error handling streaming response: {e}")
            return result.strip() if result else "Error processing response."
    
    def get_embeddings(self, text: str) -> Optional[list]:
        """
        Get embeddings for text (for semantic search)
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector or None if failed
        """
        try:
            payload = {
                "model": self.model,
                "prompt": text
            }
            
            response = requests.post(
                self.embedding_endpoint,
                json=payload,
                timeout=OLLAMA_TIMEOUT
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get('embedding')
        
        except Exception as e:
            logger.error(f"Error getting embeddings: {e}")
            return None
    
    def validate_model_available(self) -> bool:
        """Check if specified model is available in Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m.get('name', '').split(':')[0] for m in models]
                if self.model in model_names:
                    logger.info(f"Model '{self.model}' is available")
                    return True
                else:
                    logger.warning(f"Model '{self.model}' not found. Available: {model_names}")
                    return False
        except Exception as e:
            logger.error(f"Error checking model availability: {e}")
            return False
