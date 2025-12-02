# SquareTrade Chat Agent

An intelligent customer support chatbot for SquareTrade that uses Python, Ollama LLM, and Retrieval-Augmented Generation (RAG) to provide instant assistance with protection plans, claims, and support topics.

## Project Structure

```
SupportSenseAI/
├── config.py                    # Configuration and constants
├── data_loader.py              # Knowledge base management
├── llm_client.py               # Ollama LLM interface
├── rag_engine.py               # Retrieval-Augmented Generation logic
├── escalation_handler.py        # Human agent escalation system
├── chat_agent.py               # Main agent orchestrator
├── web_widget.py               # Flask REST API and chat widget UI
├── setup.py                    # Installation and setup script
├── requirements.txt            # Python dependencies
├── data/                       # Knowledge base and escalation records
├── logs/                       # Application logs
└── README.md                   # This file
```

## System Architecture

### Component Overview

1. **config.py** - Centralized configuration for all components including Ollama settings, RAG parameters, and response templates

2. **data_loader.py** - `KnowledgeBase` class that:
   - Loads SquareTrade content from JSON files
   - Provides keyword-based search functionality
   - Supports categorization (plans, claims, support)
   - Can be extended with semantic search

3. **llm_client.py** - `OllamaClient` class for:
   - Connecting to Ollama REST API
   - Generating text with configurable parameters
   - Handling streaming and non-streaming responses
   - Error handling and retries

4. **rag_engine.py** - `RAGEngine` orchestrates:
   - Query categorization
   - Document retrieval from knowledge base
   - Confidence calculation
   - Answer generation with context
   - Fallback to escalation on low confidence

5. **escalation_handler.py** - `EscalationHandler` manages:
   - Escalation ticket creation
   - Priority calculation based on urgency
   - Escalation tracking and persistence
   - Human agent handoff

6. **chat_agent.py** - `SquareTradeAgent` main orchestrator:
   - Initializes all components
   - Processes user messages end-to-end
   - Coordinates between RAG and escalation
   - Provides FAQ and status endpoints

7. **web_widget.py** - Flask API providing:
   - `/chat` endpoint for message processing
   - `/faq` endpoint for FAQ retrieval
   - `/widget` endpoint serving embedded chat UI
   - Admin endpoints for escalation management
   - Session management and history tracking

## Prerequisites

- **Python 3.8+**
- **Ollama 0.13.0** (local LLM engine)
- **pip** (Python package manager)

## Installation & Setup

### Step 1: Install Ollama

#### macOS
```bash
brew install ollama
brew services start ollama
```

#### Windows
1. Download from https://ollama.ai
2. Install and run the application
3. Verify it's running at http://localhost:11434

#### Linux
```bash
curl https://ollama.ai/install.sh | sh
systemctl start ollama
```

### Step 2: Pull a Language Model

```bash
# Pull Mistral (recommended for this project)
ollama pull mistral

# Or pull another model
ollama pull llama2
ollama pull neural-chat
```

Verify model is available:
```bash
curl http://localhost:11434/api/tags
```

### Step 3: Clone and Setup Project

```bash
cd SupportSenseAI

# Install Python dependencies
pip install -r requirements.txt

# Run setup script
python setup.py
```

### Step 4: Verify Installation

```bash
python setup.py
```

Expected output:
```
✓ Directories created
✓ Configuration file
✓ Ollama server running
✓ All imports successful
```

## Running the Agent

### Start the Web API Server

```bash
python web_widget.py
```

Expected output:
```
 * Running on http://0.0.0.0:5000
 * Press CTRL+C to quit
```

### Access the Chat Widget

- **Web UI**: http://localhost:5000/widget
- **API Health**: http://localhost:5000/health
- **Test Components**: http://localhost:5000/test

## API Endpoints

### Chat Endpoint
**POST** `/chat`

Request:
```json
{
  "message": "What protection plans do you offer?",
  "user_id": "user_123",
  "session_id": "session_456"
}
```

Response:
```json
{
  "session_id": "session_456",
  "response": "SquareTrade offers comprehensive protection plans...",
  "success": true,
  "escalated": false,
  "confidence": 0.85,
  "category": "protection_plans",
  "sources": 3
}
```

### FAQ Endpoint
**GET** `/faq?category=plans`

Response:
```json
{
  "faqs": [
    {
      "question": "What protection plans does SquareTrade offer?",
      "answer": "SquareTrade offers comprehensive protection plans...",
      "category": "protection_plans"
    }
  ],
  "total": 5,
  "category": "plans"
}
```

### Health Check
**GET** `/health`

### Test Components
**GET** `/test`

## Configuration

Edit `config.py` to customize:

```python
# Ollama settings
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "mistral"  # Can change to llama2, neural-chat, etc.

# RAG settings
TOP_K_RESULTS = 3  # Number of documents to retrieve
CONFIDENCE_THRESHOLD = 0.5  # Min confidence for answering

# Response behavior
ESCALATION_KEYWORDS = ["agent", "human", "support"]
```

Or use environment variables:
```bash
export OLLAMA_MODEL=llama2
export OLLAMA_BASE_URL=http://localhost:11434
export LOG_LEVEL=DEBUG
python web_widget.py
```

## Knowledge Base Management

### Adding Custom Content

Edit `data_loader.py` to load from your sources:

```python
def _load_sample_knowledge_base(self):
    # Replace with your SquareTrade content
    return [
        {
            "id": "plan_001",
            "category": "protection_plans",
            "title": "Your Question?",
            "content": "Your answer here...",
            "keywords": ["relevant", "keywords"]
        }
    ]
```

### Persist Knowledge Base

```python
from data_loader import KnowledgeBase

kb = KnowledgeBase()
kb.add_document({
    "id": "custom_001",
    "category": "claims",
    "title": "How to file a claim?",
    "content": "Step by step guide...",
    "keywords": ["claim", "file"]
})
kb.save_to_file()  # Save to data/knowledge_base.json
```

## Escalation Management

### View Pending Escalations

```bash
curl http://localhost:5000/escalations
```

### Resolve an Escalation

```bash
curl -X PUT http://localhost:5000/escalations/ESC_00001 \
  -H "Content-Type: application/json" \
  -d '{"resolution": "Issue resolved by agent"}'
```

## Logging

Logs are stored in `logs/agent.log`:

```bash
tail -f logs/agent.log
```

Adjust log level in `config.py`:
```python
LOG_LEVEL = "DEBUG"  # or INFO, WARNING, ERROR
```

## Query Flow Diagram

```
User Query
    ↓
Check Escalation Keywords → YES → Create Escalation Ticket
    ↓ NO
Detect Category (plans/claims/support)
    ↓
Retrieve Top-K Relevant Docs from KB
    ↓
Calculate Confidence Score
    ↓
Confidence >= Threshold? → NO → Create Escalation Ticket
    ↓ YES
Generate Answer with LLM (using retrieved docs as context)
    ↓
Return Confident Answer with Metadata
```

## Response Quality Tips

1. **Knowledge Base Quality**: Keep SquareTrade content current and comprehensive
2. **Temperature Setting**: Lower (0.3) = more factual, Higher (0.7) = more creative
3. **Context Quality**: More relevant docs = better answers
4. **Monitoring**: Review logs and escalations to improve responses

## Troubleshooting

### Ollama Server Not Found
```
Error: Cannot connect to Ollama server at localhost:11434
```
**Solution**: Make sure Ollama is running
```bash
# macOS
brew services start ollama

# Linux
systemctl start ollama

# Windows - run Ollama application
```

### Model Not Found
```
Error: Model 'mistral' not found
```
**Solution**: Pull the model first
```bash
ollama pull mistral
```

### Low Confidence Responses
- Add more documents to knowledge base
- Improve document relevance
- Check `TOP_K_RESULTS` setting
- Review `CONFIDENCE_THRESHOLD`

### Slow Response Times
- Reduce `CHUNK_SIZE` and `num_ctx`
- Use faster model (neural-chat is faster than mistral)
- Optimize knowledge base search

## Performance Considerations

- **Model Selection**: Neural-Chat (fastest) < Mistral (balanced) < Llama2 (best quality)
- **Response Time**: ~2-5 seconds typical with Mistral on CPU
- **GPU Support**: Ollama auto-detects GPU; much faster with NVIDIA/Apple Silicon
- **Scaling**: For production, use session persistence and vector database

## Future Enhancements

1. **Semantic Search**: Replace keyword search with embeddings
2. **Vector Database**: Use Pinecone or Weaviate for efficient retrieval
3. **Multi-turn Context**: Maintain conversation history for context
4. **Analytics**: Track common questions and escalation patterns
5. **Integration**: Connect to SquareTrade APIs for real-time data
6. **Feedback Loop**: Learn from human agent resolutions
7. **Multi-language**: Support Spanish, French, etc.

## Compliance Notes

✓ No personal data storage (escalations don't include PII)
✓ Only answers about SquareTrade topics (in-scope enforcement)
✓ Escalation available for unmatched intents
✓ Audit trail of conversations in logs

## Support

For issues or questions:
1. Check `logs/agent.log` for errors
2. Review Configuration section above
3. Run `/test` endpoint to validate components
4. Check Ollama status: `curl http://localhost:11434/api/tags`

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
