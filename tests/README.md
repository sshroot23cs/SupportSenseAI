# SquareTrade Chat Agent - Test Suite

This directory contains comprehensive tests for the SquareTrade Chat Agent system.

## Test Structure

```
tests/
├── unit/           # Unit tests for individual components
│   ├── test_agent.py           # Direct agent testing
│   ├── test_intent.py          # Intent detection tests
│   └── test_components.py      # Component integration tests
├── integration/    # Integration tests (currently unused)
├── api/            # API endpoint tests
│   ├── test_quick.py           # Quick smoke tests
│   └── test_comprehensive.py   # Full API validation
└── README.md
```

## Running Tests

### Unit Tests (No Server Required)

**Test Direct Agent Functionality:**
```bash
python tests/unit/test_agent.py
```
Tests basic agent features like welcome intent, plan inquiry, pricing, claims, and escalation.

**Test Intent Detection:**
```bash
python tests/unit/test_intent.py
```
Tests the intent detection system with various queries.

**Test All Components:**
```bash
python tests/unit/test_components.py
```
Comprehensive component testing including KB, LLM, RAG, escalation, and full agent.

### API Tests (Server Required)

First, start the server:
```bash
python web_widget.py
# or
python run_server.py
```

Then run the API tests:

**Quick Smoke Test:**
```bash
python tests/api/test_quick.py
```
Fast validation of basic endpoints (4 tests, ~10 seconds).

**Comprehensive API Test:**
```bash
python tests/api/test_comprehensive.py
```
Full validation of all endpoints, intents, metadata, sessions, and knowledge base retrieval (11 tests, ~2-3 minutes with LLM).

## Expected Test Results

### Unit Tests
- ✓ Agent initialization
- ✓ Welcome intent with capabilities
- ✓ Plan inquiry with document retrieval  
- ✓ Pricing queries
- ✓ File claim workflows
- ✓ Claims support
- ✓ Escalation handling

**Expected: 7/7 PASS**

### API Tests
- ✓ Health check
- ✓ Response metadata structure
- ✓ All 9 intent flows
- ✓ Knowledge base retrieval
- ✓ Session management

**Expected: 11/11 PASS**

## Cross-Platform Compatibility

All tests use:
- `pathlib.Path` for file paths (works on Windows, Linux, macOS)
- Environment variables for configuration
- No hardcoded paths
- System-agnostic imports

Tests will work identically on Windows, Linux, and macOS.

## Environment Setup

Tests require the Python environment with dependencies installed:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\Activate.ps1  # Windows

pip install -r requirements.txt
```

## Continuous Integration

These tests are designed to be run in CI/CD pipelines:

**For CI Integration:**
```bash
# Run all unit tests
python tests/unit/test_agent.py && \
python tests/unit/test_intent.py && \
python tests/unit/test_components.py

# API tests require server - run separately if needed
```

Tests exit with `0` on success and `1` on failure for CI/CD compatibility.

## Troubleshooting

**"No module named 'requests'" in API tests:**
```bash
pip install requests
```

**Server not responding in API tests:**
- Ensure server is running: `python web_widget.py`
- Check Ollama is running: `ollama serve`
- Verify port 5000 is available

**Tests hang on LLM generation:**
- Ollama model may be loading first time
- Models are cached after first use
- Increase `TIMEOUT` in test files if needed

## Adding New Tests

Place new tests in appropriate directory:
- Component/unit logic → `tests/unit/`
- Multi-component workflows → `tests/integration/`
- HTTP API validation → `tests/api/`

Follow existing test structure:
```python
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Your imports and tests here
```

This ensures tests work on any system regardless of where they're run from.
