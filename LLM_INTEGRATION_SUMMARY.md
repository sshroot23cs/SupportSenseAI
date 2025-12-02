# LLM Client Integration Summary

## Overview

The SupportSenseAI project now supports multiple LLM providers through a factory pattern design:

- **Ollama** - Local language models (default)
- **OpenAI** - OpenAI API (gpt-3.5-turbo, gpt-4, etc.)
- **Azure OpenAI** - Azure-hosted OpenAI models

## Key Changes

### 1. New Classes

#### `OpenAIClient`
Unified client for both OpenAI and Azure OpenAI:
```python
from llm_client import OpenAIClient

# OpenAI
client = OpenAIClient(provider="openai", model="gpt-3.5-turbo")

# Azure OpenAI
client = OpenAIClient(provider="azure", model="gpt-35-turbo")
```

#### `LLMClientFactory`
Factory for creating provider-agnostic clients:
```python
from llm_client import LLMClientFactory

# Uses provider from LLM_PROVIDER env var
client = LLMClientFactory.create_client()

# Override provider
client = LLMClientFactory.create_client(provider="openai")
```

### 2. Updated Configuration (`config.py`)

New settings:
```python
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # Provider selection
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
AZURE_OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL", "gpt-35-turbo")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
```

### 3. Updated Environment Variables (`.env`)

```env
# Provider selection
LLM_PROVIDER=ollama  # or 'openai' or 'azure'

# OpenAI settings
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo

# Azure OpenAI settings
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_MODEL=gpt-35-turbo
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### 4. Updated Agent (`chat_agent.py`)

Now uses factory:
```python
from llm_client import LLMClientFactory

class SquareTradeAgent:
    def __init__(self):
        self.llm = LLMClientFactory.create_client()  # Provider-agnostic
```

### 5. Updated Requirements

Added `openai==1.3.0` package for OpenAI/Azure support.

## Usage Examples

### Using Ollama (Default)

```python
from llm_client import LLMClientFactory

client = LLMClientFactory.create_client()  # Uses Ollama
response = client.generate("What is SquareTrade?")
```

### Using OpenAI

1. Set `.env`:
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

2. Use client:
```python
from llm_client import LLMClientFactory

client = LLMClientFactory.create_client()  # Uses OpenAI
response = client.generate("What is SquareTrade?")
```

### Using Azure OpenAI

1. Set `.env`:
```env
LLM_PROVIDER=azure
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
```

2. Use client:
```python
from llm_client import LLMClientFactory

client = LLMClientFactory.create_client()  # Uses Azure OpenAI
response = client.generate("What is SquareTrade?")
```

## Backward Compatibility

Existing code using `OllamaClient` directly continues to work:

```python
from llm_client import OllamaClient

client = OllamaClient()  # Still works as before
response = client.generate("Your prompt")
```

## Testing

Run the configuration verification script:

```bash
python test_llm_config.py
```

Output shows:
- ✓ Provider type and model
- ✓ Service availability
- ✓ Test generation (if service available)

## Files Modified

| File | Changes |
|------|---------|
| `llm_client.py` | Added OpenAIClient, LLMClientFactory; refactored imports |
| `config.py` | Added LLM_PROVIDER and OpenAI/Azure settings |
| `chat_agent.py` | Updated to use LLMClientFactory |
| `.env` | Added OpenAI and Azure configuration |
| `.env.example` | Complete configuration template |
| `requirements.txt` | Added openai package |

## Files Created

| File | Purpose |
|------|---------|
| `OPENAI_INTEGRATION.md` | Comprehensive OpenAI/Azure setup guide |
| `test_llm_config.py` | Configuration verification script |

## Common Workflows

### Switch from Ollama to OpenAI

1. Get API key from https://platform.openai.com/api-keys
2. Update `.env`:
   ```env
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-...
   ```
3. Restart your application - no code changes needed!

### Switch from OpenAI to Azure

1. Deploy model in Azure OpenAI
2. Update `.env`:
   ```env
   LLM_PROVIDER=azure
   AZURE_OPENAI_API_KEY=...
   AZURE_OPENAI_ENDPOINT=https://...
   ```
3. Restart application - no code changes needed!

### Use Different Models at Runtime

```python
from llm_client import LLMClientFactory

# Use gpt-4 instead of default
client = LLMClientFactory.create_client(
    provider="openai",
    model="gpt-4"
)
```

## API Feature Comparison

| Feature | Ollama | OpenAI | Azure OpenAI |
|---------|--------|--------|--------------|
| Text Generation | ✓ | ✓ | ✓ |
| Streaming | ✓ | ✓ | ✓ |
| Embeddings | ✓ | ✓ | ✓ |
| No API key needed | ✓ | ✗ | ✗ |
| Local execution | ✓ | ✗ | ✗ |
| Cloud-hosted | ✗ | ✓ | ✓ |

## Troubleshooting

**Issue:** "openai package not installed"
```bash
pip install openai==1.3.0
```

**Issue:** OpenAI API key not working
- Verify key is valid at https://platform.openai.com/api-keys
- Check `.env` has correct key
- Ensure `LLM_PROVIDER=openai`

**Issue:** Azure endpoint not found
- Verify endpoint format: `https://your-resource.openai.azure.com/`
- Check deployment name matches `AZURE_OPENAI_MODEL`
- Ensure `LLM_PROVIDER=azure`

**Issue:** "Model not found"
- Verify model name for your provider
- OpenAI: gpt-3.5-turbo, gpt-4, etc.
- Azure: deployment name (e.g., gpt-35-turbo)
- Ollama: mistral, llama2, etc.

## Next Steps

1. Test with `python test_llm_config.py`
2. Review [OPENAI_INTEGRATION.md](./OPENAI_INTEGRATION.md) for detailed setup
3. Customize system prompt and generation parameters as needed
4. Deploy to your preferred environment

## Branch Information

This integration is on the `open_ai_llm` branch. To use:

```bash
git checkout open_ai_llm
pip install -r requirements.txt
python test_llm_config.py
```

To merge to main (after testing):

```bash
git checkout main
git merge open_ai_llm
```

## Related Documentation

- [OPENAI_INTEGRATION.md](./OPENAI_INTEGRATION.md) - Detailed setup guide
- [config.py](./config.py) - Configuration reference
- [llm_client.py](./llm_client.py) - Implementation details
- [test_llm_config.py](./test_llm_config.py) - Testing script
