# Quick Start Guide

Get the SquareTrade Chat Agent running in 5 minutes!

## Prerequisites Check

```bash
# Python 3.8+
python --version

# pip
pip --version
```

## 1. Install Ollama (5 min)

**macOS:**
```bash
brew install ollama
brew services start ollama
```

**Windows:**
- Download: https://ollama.ai/download/windows
- Install and run
- Verify: http://localhost:11434/api/tags

**Linux:**
```bash
curl https://ollama.ai/install.sh | sh
systemctl start ollama
```

## 2. Pull a Model (3 min)

```bash
ollama pull mistral
```

Verify:
```bash
curl http://localhost:11434/api/tags
```

## 3. Setup Project (2 min)

```bash
cd SupportSenseAI
pip install -r requirements.txt
python setup.py
```

## 4. Start the Agent

```bash
python web_widget.py
```

Expected output:
```
 * Running on http://0.0.0.0:5000
```

## 5. Test in Browser

Open: http://localhost:5000/widget

Try these questions:
- "What protection plans do you offer?"
- "How do I file a claim?"
- "What's covered in my plan?"

## Testing via API

```bash
# Test chat
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I file a claim?", "user_id": "test_user"}'

# Get FAQs
curl http://localhost:5000/faq

# Health check
curl http://localhost:5000/health
```

## Next Steps

1. **Customize Knowledge Base**: Edit `data_loader.py` to add real SquareTrade content
2. **Adjust Settings**: Modify `config.py` for response behavior
3. **Monitor**: Check `logs/agent.log` for issues
4. **Deploy**: Deploy web_widget.py to production server

## Common Issues

**"Cannot connect to Ollama"**
- Make sure Ollama is running (check http://localhost:11434)

**"Model not found"**
- Run: `ollama pull mistral`

**"Port 5000 already in use"**
- Edit `web_widget.py` line: `app.run(..., port=5001)`

## Resources

- 📖 Full Documentation: README.md
- 🔧 Configuration: config.py
- 🤖 Ollama Models: https://ollama.ai/library
- 📊 Architecture: See README.md - System Architecture
