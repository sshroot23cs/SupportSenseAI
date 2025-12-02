#!/usr/bin/env python
"""
Quick test script to verify OpenAI/Azure OpenAI integration
Run this to test your LLM configuration before using the full agent
"""

import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
from config import LLM_PROVIDER

# Load environment variables
load_dotenv()

print("=" * 70)
print("LLM PROVIDER CONFIGURATION TEST")
print("=" * 70)

print(f"\nConfigured Provider: {LLM_PROVIDER}")
print(f"Environment LLM_PROVIDER: {os.getenv('LLM_PROVIDER', 'not set')}")

try:
    from llm_client import LLMClientFactory
    
    print("\n✓ Successfully imported LLMClientFactory")
    
    # Try to create client
    print("\nAttempting to create LLM client...")
    client = LLMClientFactory.create_client()
    
    print(f"✓ Successfully created {client.__class__.__name__} instance")
    if hasattr(client, 'provider'):
        print(f"  Provider: {client.provider}")
    if hasattr(client, 'model'):
        print(f"  Model: {client.model}")
    
    # Check availability
    print("\nChecking service availability...")
    is_available = client.is_available()
    status = "✓ Available" if is_available else "✗ Not available"
    print(f"  {status}")
    
    # Test generation if available
    if is_available:
        print("\nGenerating test response...")
        try:
            # Use appropriate parameters based on client type
            if client.__class__.__name__ == "OllamaClient":
                response = client.generate(
                    "What is SquareTrade?",
                    temperature=0.5,
                    num_ctx=500
                )
            else:
                response = client.generate(
                    "What is SquareTrade?",
                    temperature=0.5,
                    max_tokens=100
                )
            print(f"✓ Response: {response[:150]}...")
        except Exception as e:
            print(f"⚠ Generation failed: {e}")
    else:
        print("\n⚠ Service not available, skipping generation test")
    
    print("\n" + "=" * 70)
    print("Configuration test completed successfully!")
    print("=" * 70)
    
except ImportError as e:
    print(f"\n✗ Import Error: {e}")
    print("\nMake sure to install required packages:")
    print("  pip install -r requirements.txt")
    print("  pip install openai")
    sys.exit(1)

except ValueError as e:
    print(f"\n✗ Configuration Error: {e}")
    print("\nCheck your .env file configuration:")
    print(f"  - LLM_PROVIDER is set to: {LLM_PROVIDER}")
    
    if LLM_PROVIDER == "openai":
        print("  - For OpenAI, ensure OPENAI_API_KEY is set")
        print("  - Refer to OPENAI_INTEGRATION.md for setup instructions")
    elif LLM_PROVIDER == "azure":
        print("  - For Azure, ensure AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT are set")
        print("  - Refer to OPENAI_INTEGRATION.md for setup instructions")
    elif LLM_PROVIDER == "ollama":
        print("  - For Ollama, ensure it's running at OLLAMA_BASE_URL")
    
    sys.exit(1)

except Exception as e:
    print(f"\n✗ Unexpected Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
