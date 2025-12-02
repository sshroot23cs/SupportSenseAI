"""
LLM client for interacting with language models (Ollama or OpenAI)
"""

import logging
import requests
import json
import os
from typing import Optional, Dict, Any
from config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT, LLM_PROVIDER

try:
    from openai import AzureOpenAI, OpenAI
except ImportError:
    AzureOpenAI = None
    OpenAI = None

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Client for communicating with OpenAI or Azure OpenAI models"""
    
    def __init__(self, provider: str = "openai", model: str = "gpt-3.5-turbo"):
        """
        Initialize OpenAI client
        
        Args:
            provider: 'openai' or 'azure'
            model: Model name to use
        """
        self.provider = provider
        self.model = model
        
        if provider == "azure":
            self._init_azure_client()
        else:
            self._init_openai_client()
    
    def _init_azure_client(self):
        """Initialize Azure OpenAI client"""
        if AzureOpenAI is None:
            raise ImportError("openai package not installed. Install with: pip install openai")
        
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        
        if not api_key or not endpoint:
            raise ValueError("AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT must be set")
        
        self.client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )
        logger.info(f"Azure OpenAI client initialized with model: {self.model}")
    
    def _init_openai_client(self):
        """Initialize OpenAI client"""
        if OpenAI is None:
            raise ImportError("openai package not installed. Install with: pip install openai")
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY must be set")
        
        self.client = OpenAI(api_key=api_key)
        logger.info(f"OpenAI client initialized with model: {self.model}")
    
    def is_available(self) -> bool:
        """Check if OpenAI service is available"""
        try:
            response = self.client.models.list() if hasattr(self.client, 'models') else True
            return True
        except Exception as e:
            logger.error(f"OpenAI service not available: {e}")
            return False
    
    def generate(
        self,
        prompt: str,
        stream: bool = False,
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: int = 2048
    ) -> str:
        """
        Generate text using OpenAI
        
        Args:
            prompt: Input prompt
            stream: Whether to stream response
            temperature: Sampling temperature (0-2)
            top_p: Nucleus sampling parameter
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated text response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful SquareTrade support assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                stream=stream
            )
            
            if stream:
                return self._handle_streaming_response(response)
            else:
                return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"Error calling OpenAI: {e}")
            return "An error occurred while processing your request."
    
    def _handle_streaming_response(self, response) -> str:
        """Handle streaming response from OpenAI"""
        result = ""
        try:
            for chunk in response:
                if chunk.choices[0].delta.content:
                    result += chunk.choices[0].delta.content
            return result.strip()
        except Exception as e:
            logger.error(f"Error handling streaming response: {e}")
            return result.strip() if result else "Error processing response."
    
    def get_embeddings(self, text: str) -> Optional[list]:
        """
        Get embeddings for text using OpenAI
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector or None if failed
        """
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error getting embeddings: {e}")
            return None
    
    def validate_model_available(self) -> bool:
        """Validate that the model is accessible"""
        try:
            logger.info(f"Model '{self.model}' is available")
            return True
        except Exception as e:
            logger.error(f"Error validating model: {e}")
            return False


class LLMClientFactory:
    """Factory for creating LLM clients based on provider"""
    
    @staticmethod
    def create_client(provider: Optional[str] = None, model: Optional[str] = None):
        """
        Create appropriate LLM client based on provider
        
        Args:
            provider: 'ollama', 'openai', or 'azure'. Defaults to LLM_PROVIDER config
            model: Model name. Defaults to configured model for that provider
            
        Returns:
            Configured LLM client instance
        """
        provider = provider or LLM_PROVIDER
        
        if provider == "openai":
            model = model or os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
            return OpenAIClient(provider="openai", model=model)
        elif provider == "azure":
            model = model or os.getenv("AZURE_OPENAI_MODEL", "gpt-35-turbo")
            return OpenAIClient(provider="azure", model=model)
        else:
            model = model or OLLAMA_MODEL
            return OllamaClient(base_url=OLLAMA_BASE_URL, model=model)


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


def get_llm_client():
    """Get default LLM client based on configuration"""
    return LLMClientFactory.create_client()
