# 🚀 Getting Started - Step by Step

## Step 1: Verify Prerequisites (2 minutes)

### Check Python Installation
```powershell
python --version
# Should show: Python 3.8 or higher
```

### Check pip
```powershell
pip --version
# Should show: pip 20.0 or higher
```

---

## Step 2: Install Ollama (5 minutes)

### Download and Install
1. Visit: https://ollama.ai/download/windows
2. Download the Windows installer
3. Run the installer and follow prompts
4. Ollama will start automatically

### Verify Ollama is Running
```powershell
# In PowerShell, test the API
curl http://localhost:11434/api/tags

# You should see a JSON response with available models
# If you see "Connection refused", Ollama is not running
```

---

## Step 3: Download a Language Model (3 minutes)

### Pull Mistral Model (Recommended)
```powershell
ollama pull mistral
```

**This will**:
- Download ~4GB model file
- Take 2-5 minutes depending on internet
- Show progress bar
- Store in Ollama's cache

### Verify Model Installed
```powershell
curl http://localhost:11434/api/tags

# Look for "mistral" in the response
```

**Alternative Models** (if preferred):
```powershell
ollama pull llama2        # Larger, better quality
ollama pull neural-chat   # Smaller, faster
```

---

## Step 4: Setup Python Project (3 minutes)

### Open Terminal in Project Folder
```powershell
cd C:\Users\Sushrut\gitrepos\SupportSenseAI
```

### Create Virtual Environment (Optional but Recommended)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Install Python Dependencies
```powershell
pip install -r requirements.txt
```

**This will install**:
- Flask (web framework)
- Flask-CORS (cross-origin support)
- requests (HTTP client)
- python-dotenv (config management)

---

## Step 5: Validate Setup (2 minutes)

### Run Setup Script
```powershell
python setup.py
```

**Expected Output**:
```
==================================================
SquareTrade Chat Agent - Setup Script
==================================================

1. Creating directories...
✓ Created directory: data
✓ Created directory: logs

2. Setting up configuration...
✓ Created .env file

3. Checking Ollama installation...
✓ Ollama server is running
  Available models: 1
    - mistral

4. Validating Python dependencies...
✓ Flask
✓ Flask-CORS
✓ Requests
✓ Config module
✓ Data Loader
✓ LLM Client
✓ RAG Engine
✓ Escalation Handler
✓ Chat Agent
✓ All imports successful!

==================================================
Setup Summary:
==================================================
Directories: ✓
Configuration: ✓
Ollama Server: ✓
Python Dependencies: ✓

Setup complete! You can now run:
  python web_widget.py
==================================================
```

---

## Step 6: Start the Chat Agent (1 minute)

### Run the Web Server
```powershell
python web_widget.py
```

**Expected Output**:
```
 * Serving Flask app 'web_widget'
 * Debug mode: on
 * Running on http://0.0.0.0:5000
 * Press CTRL+C to quit
```

### Server is Ready! ✓

---

## Step 7: Test the Chat Widget (2 minutes)

### Open in Browser
```
http://localhost:5000/widget
```

### You should see:
1. Purple header: "SquareTrade Support Assistant"
2. Chat message area
3. Input field with "Send" button
4. Welcome message from the bot

### Try these test questions:
1. "What protection plans do you offer?"
2. "How do I file a claim?"
3. "What is covered in my plan?"
4. "I want to speak to an agent"

### Example Response:
```
User: "What protection plans do you offer?"
Agent: "Based on our knowledge base: SquareTrade offers 
comprehensive protection plans for electronics including 
smartphones, tablets, laptops, and appliances. Plans cover 
accidental damage, hardware failure, and more depending on 
the product."
```

---

## Step 8: Test API Endpoints (2 minutes)

### In a New PowerShell Terminal:

#### Test 1: Chat Endpoint
```powershell
$body = @{
    message = "How do I file a claim?"
    user_id = "test_user"
} | ConvertTo-Json

curl -X POST http://localhost:5000/chat `
  -H "Content-Type: application/json" `
  -Body $body
```

#### Test 2: FAQ Endpoint
```powershell
curl http://localhost:5000/faq
```

#### Test 3: Health Check
```powershell
curl http://localhost:5000/health
```

#### Test 4: System Test
```powershell
curl http://localhost:5000/test
```

---

## Step 9: Review Logs and Status

### View Application Logs
```powershell
Get-Content logs/agent.log -Tail 20
# Shows last 20 log lines
```

### Watch Real-Time Logs
```powershell
Get-Content logs/agent.log -Wait
# Shows new logs as they appear (Ctrl+C to stop)
```

### Expected Log Entries
```
2024-01-15 10:30:45 - chat_agent - INFO - Initializing SquareTrade Chat Agent...
2024-01-15 10:30:46 - llm_client - INFO - Model 'mistral' is available
2024-01-15 10:30:47 - data_loader - INFO - Loaded 5 documents from knowledge base
2024-01-15 10:30:48 - chat_agent - INFO - SquareTrade Chat Agent initialized successfully
2024-01-15 10:30:50 - rag_engine - INFO - Retrieved 3 documents for query: What protection...
```

---

## Troubleshooting

### ❌ "Cannot connect to Ollama server"

**Solution**: Make sure Ollama is running
```powershell
# Check if Ollama is running
Get-Process ollama

# If not found, start Ollama:
# 1. Open Ollama application from Start Menu
# 2. Or run: ollama serve
```

### ❌ "Model 'mistral' not found"

**Solution**: Pull the model
```powershell
ollama pull mistral
# Wait for download to complete
```

### ❌ "Port 5000 already in use"

**Solution**: Use a different port
```powershell
# Edit web_widget.py, line ~365, change:
# app.run(..., port=5001)  # Use 5001 instead

python web_widget.py
# Now runs on http://localhost:5001
```

### ❌ "ImportError: No module named 'flask'"

**Solution**: Install dependencies
```powershell
pip install -r requirements.txt
```

### ❌ Slow responses (>10 seconds)

**Solution**: Use a faster model
```powershell
ollama pull neural-chat
# Edit config.py: OLLAMA_MODEL = "neural-chat"
```

---

## Next Steps

### 1. ✅ Explore the Code
- Open `config.py` to see configuration options
- Read `ARCHITECTURE.md` for system design
- Check `FILE_BY_FILE_GUIDE.md` for file purposes

### 2. ✅ Customize Knowledge Base
- Edit `data_loader.py`
- Replace sample data with real SquareTrade content
- Run `python test_agent.py` to validate

### 3. ✅ Embed in Website
- Use `/widget` endpoint in an iframe
- Or integrate REST API with your website

### 4. ✅ Deploy to Production
- Deploy Flask app to server
- Set up Ollama on server
- Configure database for escalations
- Set up monitoring and alerts

---

## 📞 Getting Help

**Check these files in order**:
1. `README.md` - Full documentation
2. `QUICKSTART.md` - Quick troubleshooting
3. `ARCHITECTURE.md` - Technical details
4. `FILE_BY_FILE_GUIDE.md` - File purposes
5. `logs/agent.log` - Error messages

**Run diagnostics**:
```powershell
python setup.py
python test_agent.py
curl http://localhost:5000/test
```

---

## ✨ You're All Set!

Your SquareTrade Chat Agent is now running! 🎉

- 🌐 **Web UI**: http://localhost:5000/widget
- 📡 **API**: http://localhost:5000/chat (POST)
- 📊 **Status**: http://localhost:5000/health
- 📚 **FAQs**: http://localhost:5000/faq

**To stop the server**: Press `Ctrl+C` in the terminal

**To restart**: Run `python web_widget.py` again
