# PowerShell startup script for SquareTrade Chat Agent
# Usage: .\start-server.ps1

param(
    [switch]$NoLogs = $false,
    [switch]$Background = $false
)

# Set strict mode
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Configuration
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPath = Join-Path $ProjectRoot "venv"
$LogDir = Join-Path $ProjectRoot "logs"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = Join-Path $LogDir "server_$Timestamp.log"
$PidFile = Join-Path $ProjectRoot "server.pid"
$Port = 5000

# Create log directory
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# Colors for output
$Colors = @{
    Info    = "Green"
    Warning = "Yellow"
    Error   = "Red"
    Server  = "Cyan"
}

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "Info"
    )
    
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "$Timestamp - $Level - $Message"
    
    Write-Host $LogMessage -ForegroundColor $Colors[$Level]
    Add-Content -Path $LogFile -Value $LogMessage
}

function Stop-ExistingProcesses {
    Write-Log "Cleaning up existing processes..." "Info"
    
    Get-Process python -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*web_widget*"
    } | ForEach-Object {
        Write-Log "Terminating existing process: PID $($_.Id)" "Warning"
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
    
    Start-Sleep -Seconds 2
}

function Check-PortAvailable {
    param([int]$Port)
    
    $PortInUse = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($PortInUse) {
        Write-Log "Port $Port is already in use" "Error"
        return $false
    }
    return $true
}

function Verify-Environment {
    # Check venv exists
    if (-not (Test-Path $VenvPath)) {
        Write-Log "Virtual environment not found at $VenvPath" "Error"
        Write-Log "Please run: python -m venv venv" "Error"
        return $false
    }
    
    # Check Python executable exists
    $PythonExe = Join-Path $VenvPath "Scripts" "python.exe"
    if (-not (Test-Path $PythonExe)) {
        Write-Log "Python executable not found at $PythonExe" "Error"
        return $false
    }
    
    return $true
}

function Start-Server {
    Write-Log "============================================================" "Info"
    Write-Log "SquareTrade Chat Agent - Server Startup" "Info"
    Write-Log "============================================================" "Info"
    
    # Stop existing processes
    Stop-ExistingProcesses
    
    # Check port availability
    if (-not (Check-PortAvailable $Port)) {
        return $false
    }
    
    # Verify environment
    if (-not (Verify-Environment)) {
        return $false
    }
    
    $PythonExe = Join-Path $VenvPath "Scripts" "python.exe"
    
    Write-Log "Working directory: $ProjectRoot" "Info"
    Write-Log "Server will listen on http://0.0.0.0:$Port" "Info"
    Write-Log "Logs: $LogFile" "Info"
    Write-Log "Starting server..." "Info"
    
    # Set environment variables
    $env:PYTHONUNBUFFERED = "1"
    $env:PYTHONDONTWRITEBYTECODE = "1"
    
    try {
        # Start process
        $ProcessArgs = @{
            FilePath               = $PythonExe
            ArgumentList           = @("web_widget.py")
            WorkingDirectory       = $ProjectRoot
            RedirectStandardOutput = $LogFile
            RedirectStandardError  = $LogFile
            PassThru              = $true
            NoNewWindow            = $false
        }
        
        if ($Background) {
            Write-Log "Starting server in background mode" "Info"
            $Process = Start-Process @ProcessArgs
        } else {
            Write-Log "Starting server in foreground mode (Press Ctrl+C to stop)" "Info"
            $Process = Start-Process @ProcessArgs -Wait -PassThru
        }
        
        # Save PID
        $Process.Id | Out-File -FilePath $PidFile -Force
        Write-Log "Server process started with PID: $($Process.Id)" "Info"
        
        return $true
        
    } catch {
        Write-Log "Failed to start server: $_" "Error"
        return $false
    }
}

function Stop-Server {
    if (Test-Path $PidFile) {
        try {
            $Pid = Get-Content $PidFile -Raw
            Write-Log "Stopping server (PID: $Pid)..." "Info"
            
            Stop-Process -Id $Pid -ErrorAction SilentlyContinue
            Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
            
            Write-Log "Server stopped" "Info"
        } catch {
            Write-Log "Error stopping server: $_" "Warning"
        }
    }
}

# Main execution
try {
    Write-Log "SquareTrade Server Manager Starting..." "Info"
    
    if (Start-Server) {
        Write-Log "Server started successfully" "Info"
        exit 0
    } else {
        Write-Log "Failed to start server" "Error"
        exit 1
    }
} catch {
    Write-Log "Error: $_" "Error"
    exit 1
}
