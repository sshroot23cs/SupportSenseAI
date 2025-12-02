# Architecture & Implementation Guide

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE LAYER                          │
├─────────────────────────────────────────────────────────────────────┤
│  Web Browser                  │  Mobile App           │  API Client   │
│  (Chat Widget)                │  (in progress)        │  (curl/SDK)   │
└────────────┬────────────────────────┬────────────────────────────────┘
             │                        │
             └────────────┬───────────┘
                          │
┌─────────────────────────▼──────────────────────────────────────────┐
│                     WEB_WIDGET.PY (Flask API)                       │
├───────────────────────────────────────────────────────────────────┤
│  Endpoints:                                                        │
│  • POST /chat          - Process user messages                    │
│  • GET /faq            - Retrieve FAQs                            │
│  • GET /escalations    - View escalation tickets                  │
│  • GET /widget         - Serve chat UI                            │
│  • GET /health         - System health check                      │
└────────────┬─────────────────────┬─────────────────────┬──────────┘
             │                     │                     │
    ┌────────▼──────┐   ┌──────────▼──────┐   ┌─────────▼────────┐
    │ SESSION        │   │ LOGGING         │   │ ERROR HANDLING   │
    │ MANAGEMENT     │   │ TRACKING        │   │ & VALIDATION     │
    └────────┬──────┘   └──────────┬──────┘   └─────────┬────────┘
             │                     │                     │
             └─────────┬───────────┴────────────┬────────┘
                       │                        │
┌──────────────────────▼────────────────────────▼──────────────────┐
│                    CHAT_AGENT.PY (Orchestrator)                  │
├──────────────────────────────────────────────────────────────────┤
│  SquareTradeAgent Class:                                         │
│  • Initializes all components                                    │
│  • Routes messages through pipeline                              │
│  • Handles escalation logic                                      │
│  • Provides system status                                        │
└────────────┬──────────────────┬──────────────┬───────────────────┘
             │                  │              │
    ┌────────▼──────┐  ┌────────▼──────┐  ┌───▼──────────┐
    │ DATA_LOADER   │  │ RAG_ENGINE    │  │ ESCALATION   │
    │               │  │               │  │ _HANDLER     │
    └────────┬──────┘  └────────┬──────┘  └───┬──────────┘
             │                  │              │
             │     ┌────────────▼───────────┐  │
             │     │  LLM_CLIENT.PY         │  │
             │     │                        │  │
             │     │ OllamaClient Class:   │  │
             │     │ • Connects to Ollama   │  │
             │     │ • Generates responses  │  │
             │     │ • Handles embeddings   │  │
             │     │ • Error recovery       │  │
             │     └────────────┬───────────┘  │
             │                  │              │
             └────────┬─────────┴──────────────┘
                      │
┌─────────────────────▼──────────────────────────────────────────┐
│                        DATA LAYER                               │
├──────────────────────────────────────────────────────────────────┤
│  CONFIG.PY              │  DATA/               │  LOGS/          │
│  • Settings             │  • knowledge_base.   │  • agent.log    │
│  • Constants            │    json              │  • timestamps   │
│  • Thresholds           │  • escalations.json  │  • errors       │
└────────────┬────────────┴───────────────────────┴────────────────┘
             │
┌────────────▼──────────────────────────────────────────────────────┐
│                   EXTERNAL SERVICES                               │
├────────────────────────────────────────────────────────────────────┤
│  Ollama Server (localhost:11434)                                 │
│  • Mistral LLM (or other models)                                 │
│  • Text generation                                                │
│  • Embeddings (future)                                            │
└────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
User Query Input
      │
      ▼
┌──────────────────────────┐
│ 1. Check Escalation      │  Check if user wants human support
│    Keywords              │  Keywords: "agent", "human", "manager"
└────────┬─────────────────┘
         │
    ┌────┴─────────────────────────────────────┐
    │ YES - Wants Human Support               │ NO - Continue
    ▼                                          ▼
┌──────────────────┐        ┌──────────────────────────────┐
│ Create Escalation│        │ 2. Detect Query Category     │
│ Ticket           │        │    (plans/claims/support)    │
│ Return to User   │        └────┬──────────────────────────┘
└──────────────────┘             │
                                 ▼
                        ┌──────────────────────────────┐
                        │ 3. Retrieve Top-K Docs from  │
                        │    Knowledge Base            │
                        │    (Keyword Search)          │
                        └────┬──────────────────────────┘
                             │
                             ▼
                        ┌──────────────────────────────┐
                        │ 4. Calculate Confidence      │
                        │    Score Based on Doc        │
                        │    Relevance Scores          │
                        └────┬──────────────────────────┘
                             │
                    ┌────────┴────────┐
                    │ Score >= 0.5?   │
                    └─────┬──────┬────┘
                          │      │
                    YES ◄─┘      └─► NO
                    │                  │
                    ▼                  ▼
         ┌────────────────────┐  ┌──────────────────┐
         │ 5. Generate Answer │  │ Create Escalation│
         │    with LLM        │  │ Ticket for Low   │
         │    (using context) │  │ Confidence       │
         └────┬───────────────┘  └────┬─────────────┘
              │                       │
              └───────────┬───────────┘
                          │
                          ▼
                    ┌──────────────┐
                    │ Return to    │
                    │ User with    │
                    │ Metadata     │
                    └──────────────┘
```

## File Responsibilities

### Core Logic Files

#### `config.py`
- **Role**: Configuration management
- **Key Functions**:
  - Defines all environment variables
  - Sets LLM parameters
  - Defines response templates
  - Sets confidence thresholds

#### `data_loader.py`
- **Role**: Knowledge base management
- **Key Functions**:
  - Loads SquareTrade content
  - Performs keyword-based search
  - Categories documents
  - Persists data to JSON

#### `llm_client.py`
- **Role**: Ollama LLM interface
- **Key Functions**:
  - Connects to Ollama REST API
  - Generates text responses
  - Handles errors and timeouts
  - Validates model availability

#### `rag_engine.py`
- **Role**: Retrieval-Augmented Generation
- **Key Functions**:
  - Orchestrates retrieval and generation
  - Calculates confidence scores
  - Detects query categories
  - Decides when to escalate

#### `escalation_handler.py`
- **Role**: Human agent handoff management
- **Key Functions**:
  - Creates escalation tickets
  - Calculates priority levels
  - Tracks escalations
  - Persists to JSON database

#### `chat_agent.py`
- **Role**: Main orchestrator
- **Key Functions**:
  - Initializes all components
  - Routes messages through pipeline
  - Provides API endpoints data
  - Singleton pattern management

#### `web_widget.py`
- **Role**: REST API and chat UI
- **Key Functions**:
  - Flask REST endpoints
  - Session management
  - Embedded chat widget HTML
  - CORS support

### Utility Files

#### `setup.py`
- Initialization script
- Validates installation
- Creates directories
- Checks Ollama availability

#### `test_agent.py`
- Comprehensive test suite
- Tests each component
- Validates integration
- Provides diagnostic info

## Query Processing Pipeline

```
INPUT: User Question
│
├─► Step 1: Escalation Check (escalation_handler.py)
│   ├─► Detect escalation keywords
│   ├─► If match → Create ticket & return
│   └─► If no match → Continue
│
├─► Step 2: Category Detection (rag_engine.py)
│   ├─► Analyze query terms
│   ├─► Map to category (plans/claims/support)
│   └─► Store in metadata
│
├─► Step 3: Document Retrieval (data_loader.py)
│   ├─► Keyword search in KB
│   ├─► Calculate relevance scores
│   ├─► Return top-3 results
│   └─► Store in metadata
│
├─► Step 4: Confidence Scoring (rag_engine.py)
│   ├─► Average relevance scores
│   ├─► Normalize 0-1 range
│   └─► Compare vs. threshold
│
├─► Step 5: Response Generation or Escalation
│   │
│   ├─► If confidence >= 0.5:
│   │   ├─► Build context from docs
│   │   ├─► Create LLM prompt
│   │   ├─► Call LLM (llm_client.py)
│   │   ├─► Stream response
│   │   └─► Add confidence metadata
│   │
│   └─► If confidence < 0.5:
│       ├─► Create escalation ticket
│       ├─► Set priority
│       ├─► Return escalation message
│       └─► Add escalation metadata
│
OUTPUT: Response + Metadata
```

## Component Interactions

```
web_widget.py
    │
    ├─► POST /chat
    │   └─► chat_agent.SquareTradeAgent.process_message()
    │       │
    │       ├─► escalation_handler.should_escalate()
    │       │
    │       ├─► rag_engine.process_query()
    │       │   ├─► data_loader.search()
    │       │   ├─► rag_engine._generate_answer()
    │       │   │   └─► llm_client.generate()
    │       │   └─► Return response + metadata
    │       │
    │       ├─► escalation_handler.create_escalation()
    │       │   └─► Save to escalations.json
    │       │
    │       └─► Return final response
    │
    ├─► GET /faq
    │   └─► rag_engine.get_faq_answers()
    │       └─► data_loader (KB access)
    │
    ├─► GET /escalations
    │   └─► escalation_handler.get_pending_escalations()
    │
    └─► GET /health
        └─► chat_agent.get_agent_status()
            ├─► llm_client.is_available()
            ├─► data_loader (KB stats)
            └─► escalation_handler (pending count)
```

## Error Handling Strategy

```
Error Scenario                    → Action
─────────────────────────────────────────────────────────────
Ollama server not running         → Graceful failure + escalate
Model not available               → Use default + warn + escalate
Empty knowledge base              → Out-of-scope response + escalate
Low confidence score              → Escalate to human
LLM generation error              → Apologize + escalate
Network timeout                   → Retry + escalate on fail
No retrieved documents            → Out-of-scope response + escalate
```

## Development Workflow

### Adding New Features

1. **Add Config** (config.py)
   ```python
   NEW_SETTING = os.getenv("NEW_SETTING", "default")
   ```

2. **Update Component** (relevant file)
   ```python
   def new_feature(self, param):
       # Implementation
   ```

3. **Add Tests** (test_agent.py)
   ```python
   def test_new_feature():
       # Test implementation
   ```

4. **Update Docs** (README.md)
   - Add feature description
   - Update examples
   - Document API endpoint if applicable

### Common Modifications

**Change LLM Model:**
```python
# config.py
OLLAMA_MODEL = "llama2"  # Change from mistral
```

**Add KB Document:**
```python
# data_loader.py
kb.add_document({...})
kb.save_to_file()
```

**Adjust Confidence Threshold:**
```python
# config.py
CONFIDENCE_THRESHOLD = 0.6  # Change from 0.5
```

**Add Escalation Keyword:**
```python
# config.py
ESCALATION_KEYWORDS.append("urgent")
```
