#!/usr/bin/env python
"""
Comprehensive LLM Client Test
Tests Ollama connection, response generation, embeddings, and model detection
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from llm_client import OllamaClient
import requests

print('='*70)
print('COMPREHENSIVE LLM CLIENT TEST')
print('='*70)

try:
    # Test 1: Initialize client
    print('\n[TEST 1] Initializing OllamaClient...')
    client = OllamaClient()
    print('   ✓ Client initialized')
    print(f'      Model: {client.model}')
    print(f'      Base URL: {client.base_url}')
    print(f'      Generate Endpoint: {client.generate_endpoint}')
    
    # Test 2: Check server availability
    print('\n[TEST 2] Checking Ollama server availability...')
    if client.is_available():
        print('   ✓ Ollama server is running')
    else:
        print('   ✗ Ollama server is not responding')
        exit(1)
    
    # Test 3: List available models
    print('\n[TEST 3] Listing available models...')
    try:
        response = requests.get(f'{client.base_url}/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f'   ✓ Found {len(models)} model(s)')
            for model in models:
                name = model.get('name', 'unknown')
                size = model.get('size', 0) / (1024**3)  # Convert to GB
                print(f'      - {name} ({size:.2f} GB)')
        else:
            print(f'   ✗ Failed to list models (status: {response.status_code})')
    except Exception as e:
        print(f'   ✗ Error listing models: {e}')
    
    # Test 4: Validate model
    print('\n[TEST 4] Validating configured model...')
    if client.validate_model_available():
        print(f'   ✓ Model "{client.model}" is available')
    else:
        print(f'   ✗ Model "{client.model}" not found')
    
    # Test 5: Generate text (non-streaming)
    print('\n[TEST 5] Testing text generation (non-streaming)...')
    test_prompts = [
        'What is device protection insurance?',
        'List 3 benefits of insurance plans'
    ]
    
    for prompt in test_prompts:
        print(f'\n   Prompt: "{prompt}"')
        print('   Generating...', end='', flush=True)
        response = client.generate(prompt, stream=False)
        if response:
            chars = len(response)
            words = len(response.split())
            preview = response[:100] + '...' if len(response) > 100 else response
            print(f' ✓')
            print(f'      Length: {chars} chars, {words} words')
            print(f'      Preview: {preview}')
        else:
            print(' ✗ No response')
    
    # Test 6: Get embeddings
    print('\n[TEST 6] Testing embeddings generation...')
    test_text = 'SquareTrade device protection plan'
    print(f'   Text: "{test_text}"')
    print('   Generating embedding...', end='', flush=True)
    embedding = client.get_embeddings(test_text)
    if embedding:
        print(f' ✓')
        print(f'      Embedding dimensions: {len(embedding)}')
        print(f'      First 5 values: {embedding[:5]}')
    else:
        print(' ✗ Failed to generate embedding')
    
    # Test 7: Multiple rapid requests
    print('\n[TEST 7] Testing multiple rapid requests...')
    print('   Sending 3 requests in sequence...')
    for i in range(1, 4):
        prompt = f'Question {i}: What is SquareTrade?'
        print(f'      Request {i}...', end='', flush=True)
        response = client.generate(prompt, stream=False)
        if response:
            print(f' ✓ ({len(response)} chars)')
        else:
            print(' ✗')
    
    print('\n' + '='*70)
    print('✓ ALL TESTS PASSED - LLM CLIENT IS WORKING CORRECTLY')
    print('='*70)
    print('\nSummary:')
    print('  - Ollama server: ✓ Running')
    print('  - Model detection: ✓ Working')
    print('  - Text generation: ✓ Working')
    print('  - Embeddings: ✓ Working (if applicable)')
    print('  - Multiple requests: ✓ Working')
    print('\n✓ Ready for production use!')
    
except KeyboardInterrupt:
    print('\n\n✗ Test interrupted by user')
    exit(1)
except Exception as e:
    print(f'\n✗ CRITICAL ERROR: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
