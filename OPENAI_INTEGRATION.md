# OpenAI/Azure OpenAI Integration Guide

This guide explains how to configure and use the SupportSenseAI chat agent with OpenAI or Azure OpenAI models.

## Overview

The LLM client now supports three providers:
- **Ollama** (local models, default)
- **OpenAI** (OpenAI API)
- **Azure** (Azure OpenAI)

## Configuration

### 1. Set LLM Provider

Update your `.env` file to select which provider to use:

```env
LLM_PROVIDER=openai  # or 'azure' or 'ollama'
```

### 2. OpenAI Configuration

For standard OpenAI API:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo  # or gpt-4, gpt-4-turbo-preview, etc.
```

**Get your API key:**
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Add it to your `.env` file

### 3. Azure OpenAI Configuration

For Azure OpenAI Service:

```env
LLM_PROVIDER=azure
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_MODEL=gpt-35-turbo  # deployment name
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

**Set up Azure OpenAI:**
1. Create an Azure OpenAI resource in Azure Portal
2. Deploy a model (e.g., gpt-35-turbo)
3. Get your API key and endpoint from Azure Portal
4. Update `.env` with these values

### 4. Installation

Install the required OpenAI package:

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install openai==1.3.0
```

## Usage

### Using Default Provider

The agent automatically uses the provider configured in `LLM_PROVIDER`:

```python
from llm_client import LLMClientFactory

# Creates client based on LLM_PROVIDER env var
client = LLMClientFactory.create_client()

# Generate response
response = client.generate("What is SquareTrade?")
print(response)
```

### Using Specific Provider

Override the default provider programmatically:

```python
from llm_client import LLMClientFactory

# Use OpenAI
client = LLMClientFactory.create_client(provider="openai")

# Use Azure OpenAI
client = LLMClientFactory.create_client(provider="azure")

# Use Ollama
client = LLMClientFactory.create_client(provider="ollama")
```

### Backward Compatibility

Existing code using `OllamaClient` directly still works:

```python
from llm_client import OllamaClient

client = OllamaClient()
response = client.generate("Your prompt")
```

### Using OpenAI Client Directly

For advanced use cases:

```python
from llm_client import OpenAIClient

# Standard OpenAI
client = OpenAIClient(provider="openai", model="gpt-4")

# Azure OpenAI
client = OpenAIClient(provider="azure", model="gpt-35-turbo")

response = client.generate("Your prompt", temperature=0.5)
```

## Features

### Text Generation

```python
response = client.generate(
    prompt="What is SquareTrade protection?",
    temperature=0.7,
    top_p=0.9,
    max_tokens=2048
)
```

### Embeddings

Get vector embeddings for semantic search:

```python
embeddings = client.get_embeddings("SquareTrade protection plan")
# Returns a list of floats (embedding vector)
```

### Streaming

Stream responses token-by-token:

```python
response = client.generate(
    prompt="Explain SquareTrade",
    stream=True
)
```

## API Rate Limits and Costs

### OpenAI
- API: https://platform.openai.com/account/billing/overview
- Pricing: varies by model (gpt-3.5-turbo is cheapest)
- Rate limits depend on your plan

### Azure OpenAI
- Pricing: Based on tokens used
- Rate limits: Depends on your deployment configuration
- Dashboard: Azure Portal > Your Resource

## Troubleshooting

### "OPENAI_API_KEY must be set"
Ensure your `.env` file has:
```env
OPENAI_API_KEY=sk-...
```

### "Azure OpenAI endpoint not set"
Ensure your `.env` file has both:
```env
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://...
```

### Import error: "openai package not installed"
Install it:
```bash
pip install openai
```

### Rate limit errors
- Reduce request frequency
- Use retry logic with exponential backoff
- Check your API quotas in provider dashboard

### Timeout errors
- Increase `max_tokens` parameter carefully
- Check your network connection
- Verify API endpoint accessibility

## Environment Variables Reference

```env
# Provider selection
LLM_PROVIDER=openai  # or 'azure' or 'ollama'

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo

# Azure OpenAI
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_MODEL=gpt-35-turbo
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Ollama (when LLM_PROVIDER=ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

## See Also

- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [LLM Client Source](./llm_client.py)
- [Configuration](./config.py)
