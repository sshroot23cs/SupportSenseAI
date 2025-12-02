# SquareTrade Chat Agent - Server Startup Guide

This guide explains how to start and manage the SquareTrade Chat Agent server in production.

## Quick Start

### Windows (PowerShell)
```powershell
# Run the startup script
.\start-server.ps1

# Run in background (Windows Terminal recommended)
.\start-server.ps1 -Background
```

### Linux/Mac (Bash)
```bash
# Make script executable (first time only)
chmod +x start-server.sh

# Run the startup script
./start-server.sh

# Run in background with nohup
nohup ./start-server.sh > server.log 2>&1 &
```

### Python (Cross-platform)
```bash
# With virtual environment activated
python run_server.py

# From anywhere
cd /path/to/SupportSenseAI
python run_server.py
```

## What Each Script Does

### `run_server.py` (Python)
**Best for:** Cross-platform, Python-native deployment

Features:
- ✅ Automatic virtual environment detection
- ✅ Process monitoring and logging
- ✅ Graceful shutdown handling
- ✅ Port availability checking
- ✅ Stale process cleanup
- ✅ Signal handling (SIGTERM, SIGINT)
- ✅ Works on Windows, Linux, Mac

**Requirements:** `psutil` package
```bash
pip install psutil
```

### `start-server.ps1` (PowerShell)
**Best for:** Windows systems, Enterprise environments

Features:
- ✅ Native PowerShell implementation
- ✅ Automatic process cleanup
- ✅ Port availability checking
- ✅ Comprehensive logging
- ✅ Optional background mode
- ✅ Real-time log output

**Requirements:** Windows PowerShell 5.0+

**Usage:**
```powershell
# Foreground (recommended for development)
.\start-server.ps1

# Background mode
.\start-server.ps1 -Background

# With custom log directory
.\start-server.ps1 -LogDir "C:\Custom\Path"
```

### `start-server.sh` (Bash)
**Best for:** Linux, Mac, Docker, production servers

Features:
- ✅ POSIX-compliant shell script
- ✅ Signal handling (SIGTERM, SIGINT)
- ✅ Port availability checking
- ✅ Comprehensive logging
- ✅ Color-coded output
- ✅ Process monitoring

**Requirements:** Bash 4.0+

**Usage:**
```bash
# Interactive foreground
./start-server.sh

# Background with output capture
./start-server.sh > logs/background.log 2>&1 &

# With systemd
systemctl start squaretrade-chat-agent
```

## Server Configuration

All scripts use these defaults (modify in script files as needed):

```
HOST: 0.0.0.0 (all interfaces)
PORT: 5000
LOG_DIR: ./logs/
PID_FILE: ./server.pid
VENV_PATH: ./venv/
```

## Log Files

Logs are automatically created in `./logs/` directory:

```
logs/
├── server_20251202_125000.log  # Timestamped server log
├── server_20251202_130000.log
└── ...
```

View logs in real-time:
```bash
# Windows PowerShell
Get-Content logs/*.log -Tail 50 -Wait

# Linux/Mac
tail -f logs/*.log
```

## Stopping the Server

### Windows
```powershell
# Using Get-Process
Get-Process python | Where-Object {$_.CommandLine -like "*web_widget*"} | Stop-Process

# Or manually
taskkill /F /IM python.exe
```

### Linux/Mac
```bash
# Using process file
kill $(cat server.pid)

# Using pkill
pkill -f "python.*web_widget"

# Force kill
pkill -9 -f "python.*web_widget"
```

## Production Deployment

### Docker
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .

RUN python -m venv venv
RUN ./venv/bin/pip install -r requirements.txt

EXPOSE 5000
CMD ["python", "run_server.py"]
```

### Systemd Service (Linux)
Create `/etc/systemd/system/squaretrade-chat.service`:

```ini
[Unit]
Description=SquareTrade Chat Agent
After=network.target

[Service]
Type=simple
User=squaretrade
WorkingDirectory=/opt/squaretrade-chat-agent
Environment="PATH=/opt/squaretrade-chat-agent/venv/bin"
ExecStart=/opt/squaretrade-chat-agent/start-server.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable squaretrade-chat
sudo systemctl start squaretrade-chat
```

### Supervisor (Process Monitor)
Create `/etc/supervisor/conf.d/squaretrade-chat.conf`:

```ini
[program:squaretrade-chat]
directory=/opt/squaretrade-chat-agent
command=/opt/squaretrade-chat-agent/start-server.sh
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/squaretrade-chat.log
```

Start with supervisor:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start squaretrade-chat
```

### PM2 (Node.js style process manager)
```bash
pm2 start run_server.py --name "squaretrade-chat"
pm2 save
pm2 startup
```

## Health Check

Test if server is running:

```bash
# Using curl
curl http://localhost:5000/health

# Using Python
python -c "import requests; print(requests.get('http://localhost:5000/health').json())"

# Using PowerShell
Invoke-WebRequest -Uri "http://localhost:5000/health" | Select-Object -ExpandProperty Content
```

## Troubleshooting

### Port already in use
```bash
# Find process using port 5000
# Windows: netstat -ano | findstr :5000
# Linux: lsof -i :5000

# Kill the process
# Windows: taskkill /PID <PID> /F
# Linux: kill -9 <PID>
```

### Server crashes on startup
1. Check logs: `logs/server_*.log`
2. Verify Ollama is running: `http://localhost:11434`
3. Check virtual environment: `python -m venv venv`
4. Reinstall requirements: `pip install -r requirements.txt`

### Slow response time
- Ensure Ollama model is loaded: `ollama list`
- Check system resources: CPU, memory, disk
- Monitor logs for errors or warnings

### Connection refused
1. Check if server is running
2. Verify port 5000 is open in firewall
3. Check if running on correct host (0.0.0.0 vs localhost)
4. Try accessing from different machine to verify network connectivity

## Environment Variables

Optional environment variables:

```bash
# Python optimization
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# Flask settings
export FLASK_ENV=production
export FLASK_DEBUG=0

# Ollama settings (if needed)
export OLLAMA_BASE_URL=http://localhost:11434
```

## Performance Tuning

For production deployments, consider:

1. **Use WSGI server instead of Flask development server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 web_widget:app
   ```

2. **Add reverse proxy (Nginx)**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       location / {
           proxy_pass http://127.0.0.1:5000;
       }
   }
   ```

3. **Enable caching**
   ```python
   # In web_widget.py
   from flask_caching import Cache
   cache = Cache(app, config={'CACHE_TYPE': 'simple'})
   ```

4. **Monitor resources**
   ```bash
   # Linux
   top -p $(cat server.pid)
   
   # Windows
   Get-Process -Id (Get-Content server.pid)
   ```

## Security Notes

For production:

- [ ] Run server behind reverse proxy (Nginx, Apache)
- [ ] Use SSL/TLS certificates
- [ ] Restrict access with firewall rules
- [ ] Use strong authentication
- [ ] Implement rate limiting
- [ ] Monitor logs for suspicious activity
- [ ] Keep dependencies updated
- [ ] Use environment variables for secrets

## Support

For issues or questions:
1. Check the logs in `logs/` directory
2. Review `/chat` endpoint response
3. Test `/health` endpoint
4. Check Ollama connectivity
5. Verify knowledge base files exist
