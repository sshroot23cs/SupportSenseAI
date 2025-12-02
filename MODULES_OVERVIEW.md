# SupportSenseAI - Module Architecture & Testing Plan

## Core Modules Overview

Your project has **5 core modules** that work together, plus supporting files:

### 1. **config.py** - Configuration Module
**Purpose:** Central configuration for all settings
- Ollama connection settings (URL, model, timeout)
- Database/file paths (knowledge base, logs, escalations)
- Environment variables setup

**Key Exports:**
```python
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "auto"
KNOWLEDGE_BASE_PATH = Path(__file__).parent / "data" / "knowledge_base.json"
```

**Status:** ✅ Core dependency (used by all modules)

---

### 2. **llm_client.py** - Language Model Client
**Purpose:** Interface to Ollama for text generation and embeddings

**Class:** `OllamaClient`

**Key Methods:**
- `__init__(base_url, model)` - Initialize connection
- `is_available()` - Check if Ollama is running
- `generate(prompt, stream, temperature, top_p, num_ctx)` - Generate text
- `get_embeddings(text)` - Get semantic embeddings
- `validate_model_available()` - Check model exists
- `_detect_model()` - Auto-select best available model
- `_handle_streaming_response(response)` - Process streaming

**Dependencies:** requests library

**Status:** ✅ TESTED - Full functionality confirmed

---

### 3. **data_loader.py** - Knowledge Base Manager
**Purpose:** Load and manage the knowledge base JSON files

**Class:** `KnowledgeBase`

**Key Methods:**
- `__init__(knowledge_base_path, intent_path, escalation_path, dialogflow_path)` - Load all data
- `get_answer(query)` - Find relevant answer
- `search(query, top_k)` - Semantic search
- `get_all_intents()` - List all intents
- `get_intent_confidence(intent_name)` - Get intent weight
- `get_escalation_keywords()` - Get escalation triggers
- `get_dialogflow(intent_name)` - Get dialog flow

**Data Files:**
- `data/knowledge_base.json` - Q&A pairs and content
- `data/intent_knowledge_base.json` - Intent definitions
- `data/escalations.json` - Escalation rules
- `data/dialogflows.json` - Dialog flows (currently viewing)

**Status:** ⏳ Needs testing

---

### 4. **rag_engine.py** - Retrieval Augmented Generation
**Purpose:** Combine knowledge base with LLM for better responses

**Class:** `RAGEngine`

**Key Methods:**
- `__init__(knowledge_base, llm_client)` - Initialize
- `generate_answer(query, max_tokens, temperature)` - Generate augmented response
- `search_context(query, top_k)` - Find relevant docs
- `evaluate_relevance(retrieved_docs, query)` - Score relevance

**Features:**
- Retrieves relevant documents from knowledge base
- Uses LLM to generate contextual responses
- Combines both for better accuracy

**Status:** ⏳ Needs testing

---

### 5. **escalation_handler.py** - Escalation Manager
**Purpose:** Handle conversation escalations to human support

**Class:** `EscalationHandler`

**Key Methods:**
- `__init__(escalation_data_path)` - Initialize
- `should_escalate(message)` - Check if escalation needed
- `create_escalation(user_id, reason, priority)` - Create ticket
- `get_escalation(escalation_id)` - Get ticket info
- `resolve_escalation(escalation_id, resolution)` - Close ticket
- `get_all_escalations(status)` - List escalations

**Escalation Triggers:**
- Urgent keywords (help, urgent, emergency)
- Multiple failed attempts
- Specific request to speak with human
- Issue classification as complex

**Status:** ⏳ Needs testing

---

### 6. **chat_agent.py** - Main Chat Agent
**Purpose:** Orchestrate all modules for conversational AI

**Class:** `SquareTradeAgent`

**Key Methods:**
- `__init__()` - Initialize all components
- `process_message(message, user_id, session_id)` - Main chat handler
- `detect_intent(message)` - Identify user intent
- `generate_response(message, intent)` - Create response
- `should_escalate(message)` - Check escalation
- `get_agent_status()` - System health check
- `test_connectivity()` - Component verification

**Helper Function:**
- `get_agent()` - Global agent instance

**Status:** ✅ Partially tested (direct tests passing)

---

### 7. **web_widget.py** - Flask API Server
**Purpose:** HTTP REST API for chat interface

**Flask Routes:**
- `GET /health` - Server status
- `GET /test` - Component connectivity test
- `POST /chat` - Main chat endpoint
- `GET /faq` - FAQ retrieval
- `GET /escalations` - List escalations
- `POST /escalations/<id>/resolve` - Resolve escalation
- `GET /sessions` - Session management
- `GET /widget` - Chat widget HTML
- `GET /` - Main page

**Features:**
- CORS enabled for widget embedding
- Session management
- User tracking
- JSON responses

**Status:** ⏳ Partially working (needs debugging)

---

## Supporting Files

### Configuration & Setup
- **config.py** - Central config (already described)
- **setup.py** - Installation script
- **run_server.py** - Server manager with PID tracking

### Data Files
- **data/knowledge_base.json** - Q&A database
- **data/intent_knowledge_base.json** - Intent definitions
- **data/escalations.json** - Escalation rules
- **data/dialogflows.json** - Dialog flows

### Tests
- **tests/unit/test_agent.py** - Direct agent tests (7 tests)
- **tests/unit/test_intent.py** - Intent detection
- **tests/unit/test_components.py** - Component integration (5 tests)
- **tests/api/test_quick.py** - Quick API tests (4 tests)
- **tests/api/test_comprehensive.py** - Full API tests (11 tests)
- **test_llm_client.py** - LLM client validation (7 tests)

---

## Module Dependency Graph

```
config.py
  ↓
┌─────────────────────────────────────┐
│                                     │
llm_client.py    data_loader.py    escalation_handler.py
│                 │                   │
└─────────┬───────┴───────┬───────────┘
          │               │
          ↓               ↓
      rag_engine.py       │
          │               │
          └───────┬───────┘
                  ↓
           chat_agent.py
                  ↓
           web_widget.py (Flask API)
```

---

## Testing Strategy

### Phase 1: Individual Module Tests ✅
Test each module in isolation:
1. ✅ **config.py** - Already works (used by all)
2. ✅ **llm_client.py** - TESTED (test_llm_client.py passed)
3. ⏳ **data_loader.py** - NEEDS TEST
4. ⏳ **rag_engine.py** - NEEDS TEST
5. ⏳ **escalation_handler.py** - NEEDS TEST
6. ⏳ **chat_agent.py** - Partial tests exist
7. ⏳ **web_widget.py** - API tests need debugging

### Phase 2: Integration Tests
- Unit tests: Components working together
- API tests: Full workflows through Flask

### Phase 3: End-to-End Tests
- Full conversation flows
- Multi-turn conversations
- Escalation workflows

---

## Module Status Summary

| Module | Type | Status | Last Tested |
|--------|------|--------|-------------|
| config.py | Config | ✅ Working | In use |
| llm_client.py | Core | ✅ Tested | Today |
| data_loader.py | Core | ⏳ Untested | - |
| rag_engine.py | Core | ⏳ Untested | - |
| escalation_handler.py | Core | ⏳ Untested | - |
| chat_agent.py | Core | ⚠️ Partial | Previous |
| web_widget.py | API | ⚠️ Partial | Previous |

---

## Next Steps

1. Create individual test scripts for each module
2. Run tests in dependency order:
   - data_loader (no deps)
   - rag_engine (depends on llm_client, data_loader)
   - escalation_handler (no deps)
   - chat_agent (depends on all above)
   - web_widget (depends on chat_agent)

3. Fix any issues discovered
4. Run integration tests
5. Document results

---

## How to Test Each Module

### Quick Test All
```bash
python test_individual_modules.py
```

### Test Individual Module
```bash
# Test data_loader
python -c "from data_loader import KnowledgeBase; kb = KnowledgeBase(); print('✓ KnowledgeBase loaded')"

# Test rag_engine
python -c "from rag_engine import RAGEngine; rag = RAGEngine(); print('✓ RAGEngine loaded')"

# Test escalation_handler
python -c "from escalation_handler import EscalationHandler; eh = EscalationHandler(); print('✓ Escalation handler loaded')"

# Test chat_agent
python tests/unit/test_agent.py
```

---

## File Sizes & Complexity

| Module | Size | Classes | Methods | Complexity |
|--------|------|---------|---------|------------|
| config.py | ~2KB | 0 | 0 | Low |
| llm_client.py | ~6KB | 1 | 7 | Medium |
| data_loader.py | ~8KB | 1 | 8 | Medium |
| rag_engine.py | ~5KB | 1 | 4 | Medium |
| escalation_handler.py | ~6KB | 1 | 6 | Medium |
| chat_agent.py | ~12KB | 1 | 10 | High |
| web_widget.py | ~15KB | 0 | 12 | High |

---

This is your complete module breakdown. Let me create individual test scripts for each module next!
