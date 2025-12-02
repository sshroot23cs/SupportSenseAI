# File-by-File Guide

This guide explains the purpose and key functions of each file in the project.

## 📋 File Organization

### Application Core (7 Python Files)
These files contain the main application logic.

### Documentation (5 Markdown Files)
These files explain how to use and understand the system.

### Configuration (2 Files)
Setup and dependency management.

---

## 🔧 APPLICATION CORE FILES

### 1. `config.py` - Configuration Hub
**Purpose**: Central configuration for the entire system

**What it contains**:
- Ollama connection settings (URL, model, timeout)
- RAG parameters (chunk size, top results, confidence threshold)
- Knowledge base categories and keywords
- Response templates for different scenarios
- Escalation keywords that trigger human handoff
- File paths for data and logs

**When to modify**:
- Changing which Ollama model to use
- Adjusting confidence threshold
- Adding new knowledge base categories
- Customizing response messages

**Example usage**:
```python
from config import OLLAMA_MODEL, CONFIDENCE_THRESHOLD
# Use these settings throughout the app
```

---

### 2. `data_loader.py` - Knowledge Base Manager
**Purpose**: Load, search, and manage SquareTrade knowledge base

**Key Classes**:
- `KnowledgeBase`: Main class for KB management

**Key Methods**:
- `search(query)`: Find relevant documents
- `get_by_category(category)`: Get docs by topic
- `add_document(doc)`: Add new document
- `save_to_file()`: Persist to JSON

**What it does**:
1. Loads documents from `data/knowledge_base.json`
2. Provides keyword-based search (retrieval)
3. Organizes docs by category (plans, claims, support)
4. Calculates relevance scores
5. Saves new documents to file

**When to use**:
- Getting relevant docs for a query: `kb.search("claim")`
- Adding SquareTrade content: `kb.add_document({...})`
- Retrieving FAQs: `kb.get_by_category("plans")`

**Example output**:
```python
results = kb.search("file a claim")
# Returns: [
#   {"id": "claim_001", "title": "How to file a claim", "relevance_score": 8},
#   {"id": "claim_002", "title": "Claim processing time", "relevance_score": 6}
# ]
```

---

### 3. `llm_client.py` - Ollama Interface
**Purpose**: Communicate with Ollama LLM server

**Key Classes**:
- `OllamaClient`: Interface to Ollama REST API

**Key Methods**:
- `generate(prompt)`: Get LLM response
- `is_available()`: Check server running
- `validate_model_available()`: Check model installed
- `get_embeddings(text)`: Get text embeddings (future)

**What it does**:
1. Connects to Ollama at localhost:11434
2. Sends prompts and gets responses
3. Handles errors (timeouts, connection issues)
4. Validates model availability
5. Supports streaming responses

**Configuration options**:
- `temperature`: 0-2, higher = more creative
- `top_p`: nucleus sampling, 0-1
- `num_ctx`: context window size

**Example usage**:
```python
llm = OllamaClient()
response = llm.generate("What is a warranty?", temperature=0.3)
# Returns: "A warranty is a promise that covers..."
```

---

### 4. `rag_engine.py` - Retrieval-Augmented Generation
**Purpose**: Combine KB retrieval with LLM generation

**Key Classes**:
- `RAGEngine`: Main RAG orchestrator

**Key Methods**:
- `process_query(query)`: Main entry point
- `_detect_category(query)`: Identify query type
- `_generate_answer(query, docs)`: LLM generation
- `_build_context(docs)`: Format docs as context
- `_create_prompt(query, context)`: Engineer prompt

**The RAG Pipeline**:
1. Detect query category (plans/claims/support)
2. Retrieve relevant docs from KB
3. Calculate confidence score
4. If high confidence:
   - Build context from docs
   - Create LLM prompt
   - Generate answer
5. If low confidence:
   - Mark for escalation
   - Return generic message

**Confidence Calculation**:
```
confidence = (sum of relevance_scores) / (count * 10)
# Normalized to 0-1 range
# If >= CONFIDENCE_THRESHOLD (0.5), generate answer
# Otherwise, escalate to human
```

**Example flow**:
```python
rag = RAGEngine()
answer, metadata = rag.process_query("How do I file a claim?")
# Returns:
# answer: "To file a claim: 1) Log in to your account..."
# metadata: {
#   "category": "claims",
#   "confidence": 0.85,
#   "retrieved_docs": 3,
#   "escalated": false
# }
```

---

### 5. `escalation_handler.py` - Human Handoff Manager
**Purpose**: Create and manage escalation tickets for human support

**Key Classes**:
- `EscalationHandler`: Escalation management

**Key Methods**:
- `should_escalate(query)`: Check if escalation needed
- `create_escalation(query, reason)`: Create ticket
- `_calculate_priority(query)`: Set priority level
- `resolve_escalation(id, resolution)`: Mark as resolved
- `get_pending_escalations()`: List open tickets

**Escalation Triggers**:
1. User explicitly requests agent/human/manager
2. Low confidence score from RAG engine
3. System errors

**Priority Levels**:
- **High**: "urgent", "broken", "defective", "immediate"
- **Medium**: "claim", "refund", "warranty"
- **Low**: All others

**Ticket Structure**:
```json
{
  "id": "ESC_00001",
  "timestamp": "2024-01-15T10:30:00",
  "user_id": "user_123",
  "user_query": "Why isn't my claim approved?",
  "reason": "Low confidence",
  "status": "pending",
  "priority": "high"
}
```

**Usage**:
```python
escalation = EscalationHandler()

# Check if escalation needed
if escalation.should_escalate("I need to talk to someone"):
    ticket = escalation.create_escalation(
        user_query="I need to talk to someone",
        reason="User requested human support",
        user_id="user_123"
    )
    print(ticket['id'])  # ESC_00001
```

---

### 6. `chat_agent.py` - Main Orchestrator
**Purpose**: Coordinate all components and handle message processing

**Key Classes**:
- `SquareTradeAgent`: Main agent orchestrator
- Uses singleton pattern (one instance for app)

**Key Methods**:
- `process_message(user_message)`: Main entry point
- `get_faq(category)`: Retrieve FAQs
- `get_agent_status()`: System health
- `test_connectivity()`: Validate all components

**Processing Pipeline**:
1. Initialize all components (KB, LLM, RAG, Escalation)
2. Check if Ollama server is running
3. Validate model is available
4. On incoming message:
   - Check escalation triggers
   - Process through RAG
   - Decide answer or escalate
   - Return response + metadata

**Response Format**:
```python
{
  "response": "SquareTrade offers...",
  "success": true,
  "escalated": false,
  "confidence": 0.85,
  "category": "plans",
  "sources": 3
}
```

**Usage**:
```python
agent = SquareTradeAgent()

# Process a message
result = agent.process_message(
    user_message="What plans do you have?",
    user_id="user_123",
    session_id="session_456"
)

# Check system status
status = agent.get_agent_status()
# Returns: llm_available, knowledge_base_documents, pending_escalations
```

---

### 7. `web_widget.py` - REST API & Chat UI
**Purpose**: Flask server providing REST API and embedded chat widget

**Endpoints**:
- **POST** `/chat` - Process user message
- **GET** `/faq` - Get FAQ content
- **GET** `/escalations` - List escalations (admin)
- **PUT** `/escalations/<id>` - Resolve escalation (admin)
- **GET** `/health` - System health
- **GET** `/test` - Test components
- **GET** `/widget` - Serve chat UI

**Key Features**:
1. **Chat Endpoint** (`/chat`):
   - Accepts JSON with user message
   - Routes to chat_agent
   - Returns response + metadata
   - Tracks sessions

2. **Widget Endpoint** (`/widget`):
   - Serves HTML/CSS/JavaScript
   - Real-time chat interface
   - Session persistence in localStorage
   - Shows confidence scores
   - Displays escalation notices

3. **Session Management**:
   - Stores in-memory (upgrade to Redis for production)
   - Tracks user messages and responses
   - Maps session_id to user_id

**Request Example** (POST /chat):
```json
{
  "message": "How do I file a claim?",
  "user_id": "user_123",
  "session_id": "session_456"
}
```

**Response Example**:
```json
{
  "session_id": "session_456",
  "response": "To file a claim: 1) Log in...",
  "success": true,
  "escalated": false,
  "confidence": 0.85
}
```

**Running the server**:
```bash
python web_widget.py
# Starts at http://localhost:5000
```

---

## 📚 DOCUMENTATION FILES

### `README.md` - Complete Documentation
Comprehensive guide covering:
- Project overview
- Installation for all platforms
- Running the agent
- API reference
- Configuration options
- Troubleshooting
- Performance tips

### `QUICKSTART.md` - Fast Setup
5-minute setup guide with:
- Prerequisites check
- Ollama installation
- Project setup
- Starting the server
- First test

### `ARCHITECTURE.md` - Technical Details
Deep dive including:
- System architecture diagrams
- Data flow visualization
- Component interactions
- Error handling strategy
- Development workflow

### `PROJECT_SUMMARY.md` - Overview
Project summary with:
- File descriptions
- Feature list
- Quick start
- API endpoints
- Next steps

### `Scope_Definition.md` - Project Scope
Original scope document (unchanged):
- Objectives
- In-scope features
- Out-of-scope items

---

## ⚙️ CONFIGURATION FILES

### `requirements.txt` - Python Dependencies
```
Flask==2.3.3          # Web framework
Flask-CORS==4.0.0     # Cross-origin requests
requests==2.31.0      # HTTP client
python-dotenv==1.0.0  # Environment variables
```

### `.gitignore` - Git Configuration
Ignores:
- Python cache and packages
- Virtual environment
- IDE settings
- Logs and data files
- OS-specific files

---

## 🛠️ SETUP & TESTING FILES

### `setup.py` - Installation Script
**Purpose**: Validate and initialize the project

**Functions**:
1. Create necessary directories (data, logs)
2. Create `.env` file with defaults
3. Check Ollama is running
4. Validate Python imports
5. Display setup summary

**Run it**:
```bash
python setup.py
```

**Output**:
```
✓ Directories created
✓ Configuration file
✓ Ollama server running
✓ All imports successful
Setup complete!
```

### `test_agent.py` - Test Suite
**Purpose**: Comprehensive testing of all components

**Tests**:
1. `test_knowledge_base()` - KB loading and search
2. `test_ollama_client()` - LLM connectivity
3. `test_rag_engine()` - RAG pipeline
4. `test_escalation_handler()` - Escalation logic
5. `test_chat_agent()` - End-to-end agent

**Run it**:
```bash
python test_agent.py
```

**Output**:
```
✓ PASS: Knowledge Base
✓ PASS: Ollama Client
✓ PASS: RAG Engine
✓ PASS: Escalation Handler
✓ PASS: Chat Agent

Total: 5/5 passed
```

---

## 🎯 How These Files Work Together

```
1. User visits website → Loads /widget endpoint (web_widget.py)
2. User types message → POST /chat (web_widget.py)
3. Routed to process_message() (chat_agent.py)
4. Check escalation keywords (escalation_handler.py)
5. Detect category (rag_engine.py)
6. Search KB (data_loader.py)
7. Generate prompt (rag_engine.py)
8. Call LLM (llm_client.py)
9. Create escalation if needed (escalation_handler.py)
10. Return response with metadata (web_widget.py)
11. Display in widget (HTML/JavaScript)
```

---

## 📝 Modification Guide

**Want to change something?**

| Goal | File | What to Change |
|------|------|---|
| Change LLM model | config.py | `OLLAMA_MODEL` |
| Add KB document | data_loader.py | `_load_sample_knowledge_base()` |
| Adjust confidence | config.py | `CONFIDENCE_THRESHOLD` |
| Add API endpoint | web_widget.py | Add new `@app.route()` |
| Add escalation trigger | config.py | `ESCALATION_KEYWORDS` |
| Change response text | config.py | `RESPONSE_TEMPLATES` |
| Add test | test_agent.py | Add `test_*()` function |
| Change port | web_widget.py | `app.run(..., port=5001)` |

---

This guide helps you understand what each file does and how to navigate the codebase!
