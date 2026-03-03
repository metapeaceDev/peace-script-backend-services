# ==========================================
# PEACE SCRIPT AI - SYSTEM STARTUP SCRIPT
# ==========================================
# Description: Starts all required services for Peace Script AI
# Date: March 3, 2026
# GPU: RTX 5090 with CUDA 12.8 support
# ==========================================

param(
    [switch]$SkipDMM,
    [switch]$SkipJitta,
    [switch]$SkipFrontend,
    [switch]$QuietMode
)

$ErrorActionPreference = "SilentlyContinue"

function Write-Status {
    param([string]$Message, [string]$Color = "White")
    if (-not $QuietMode) {
        Write-Host $Message -ForegroundColor $Color
    }
}

function Test-Port {
    param([int]$Port)
    $connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    return $null -ne $connection
}

function Stop-ServiceOnPort {
    param([int]$Port)
    $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($connections) {
        $connections | Select-Object -ExpandProperty OwningProcess | Sort-Object -Unique | ForEach-Object {
            Write-Status "  Stopping process on port $Port (PID: $_)" "Yellow"
            Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
        }
        Start-Sleep -Seconds 2
    }
}

Write-Status "`n==========================================" "Cyan"
Write-Status "   🚀 PEACE SCRIPT AI - SYSTEM STARTUP" "Cyan"
Write-Status "==========================================/n" "Cyan"

# Step 1: Clear existing processes
Write-Status "📋 Step 1: Clearing existing processes..." "Yellow"
$portsToCheck = @(3000, 8000, 8003)
foreach ($port in $portsToCheck) {
    if (Test-Port $port) {
        Write-Status "  Port $port is occupied. Clearing..." "Yellow"
        Stop-ServiceOnPort $port
    }
}
Write-Status "  ✅ All ports cleared`n" "Green"

# Step 2: Start DMM Backend
if (-not $SkipDMM) {
    Write-Status "📋 Step 2: Starting DMM Backend (Port 8000)..." "Yellow"
    Write-Status "  Location: dmm_backend/" "Gray"
    
    $dmmPath = Join-Path $PSScriptRoot "dmm_backend"
    $pythonExe = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
    
    if (Test-Path $pythonExe) {
        Set-Location $dmmPath
        Start-Process -NoNewWindow -FilePath $pythonExe -ArgumentList "main.py"
        Write-Status "  ✅ DMM Backend started (waiting 8 seconds...)" "Green"
        Start-Sleep -Seconds 8
    } else {
        Write-Status "  ❌ Python not found at: $pythonExe" "Red"
        exit 1
    }
} else {
    Write-Status "📋 Step 2: Skipping DMM Backend (--SkipDMM flag)" "Gray"
}

# Step 3: Start Jitta Assistant
if (-not $SkipJitta) {
    Write-Status "`n📋 Step 3: Starting Jitta Assistant (Port 8003) - GPU Powered..." "Yellow"
    Write-Status "  Location: jitta-assistant/" "Gray"
    Write-Status "  GPU: NVIDIA RTX 5090 with CUDA" "Gray"
    
    $jittaPath = Join-Path $PSScriptRoot "jitta-assistant"
    $pythonExe = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
    
    if (Test-Path $pythonExe) {
        Set-Location $jittaPath
        Start-Process -NoNewWindow -FilePath $pythonExe `
            -ArgumentList "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8003", "--reload"
        Write-Status "  ✅ Jitta Assistant started (waiting 8 seconds...)" "Green"
        Start-Sleep -Seconds 8
    } else {
        Write-Status "  ❌ Python not found at: $pythonExe" "Red"
        exit 1
    }
} else {
    Write-Status "`n📋 Step 3: Skipping Jitta Assistant (--SkipJitta flag)" "Gray"
}

# Step 4: Start Frontend
if (-not $SkipFrontend) {
    Write-Status "`n📋 Step 4: Starting Frontend (Port 3000)..." "Yellow"
    Write-Status "  Location: peace-script-basic-v1/" "Gray"
    
    $frontendPath = Join-Path $PSScriptRoot "peace-script-basic-v1"
    
    if (Test-Path (Join-Path $frontendPath "package.json")) {
        Set-Location $frontendPath
        Start-Process -NoNewWindow -FilePath "npm" -ArgumentList "run", "dev", "--", "--port", "3000", "--host"
        Write-Status "  ✅ Frontend started (waiting 5 seconds...)" "Green"
        Start-Sleep -Seconds 5
    } else {
        Write-Status "  ❌ package.json not found in: $frontendPath" "Red"
        exit 1
    }
} else {
    Write-Status "`n📋 Step 4: Skipping Frontend (--SkipFrontend flag)" "Gray"
}

# Step 5: Verify all services
Write-Status "`n📋 Step 5: Verifying services..." "Yellow"
Start-Sleep -Seconds 5

Write-Status "`n==========================================" "Cyan"
Write-Status "         SYSTEM STATUS VERIFICATION" "Cyan"
Write-Status "==========================================/n" "Cyan"

# Check DMM Backend
if (-not $SkipDMM) {
    Write-Status "1️⃣  DMM Backend (Port 8000):" "Magenta"
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/" -Method Get -TimeoutSec 5
        Write-Status "     ✅ ONLINE" "Green"
        Write-Status "     📝 $($response.message)" "White"
    } catch {
        Write-Status "     ⚠️  Service starting... (may need more time)" "Yellow"
    }
}

# Check Jitta Assistant
if (-not $SkipJitta) {
    Write-Status "`n2️⃣  Jitta Assistant (Port 8003) - GPU:" "Magenta"
    try {
        $jitta = Invoke-RestMethod -Uri "http://localhost:8003/status/runtime" -Method Get -TimeoutSec 10
        Write-Status "     ✅ ONLINE & GPU READY" "Green"
        Write-Status "     🎮 Device: $($jitta.torch.devices[0].name)" "White"
        Write-Status "     🧠 Embedding: $($jitta.embedding.resolvedDevice)" "White"
    } catch {
        Write-Status "     ⚠️  Service starting... (GPU initialization may take time)" "Yellow"
    }
}

# Check Frontend
if (-not $SkipFrontend) {
    Write-Status "`n3️⃣  Frontend (Port 3000):" "Magenta"
    try {
        $fe = Invoke-WebRequest -Uri "http://localhost:3000" -Method Get -TimeoutSec 5 -UseBasicParsing
        Write-Status "     ✅ ONLINE (HTTP $($fe.StatusCode))" "Green"
    } catch {
        Write-Status "     ⚠️  Service starting..." "Yellow"
    }
}

Write-Status "`n==========================================" "Cyan"
Write-Status "  🌐 ACCESS: http://localhost:3000" "Green" 
Write-Status "  📚 DMM API: http://localhost:8000/docs" "Green"
Write-Status "  🤖 JITTA: http://localhost:8003/status/runtime" "Green"
Write-Status "==========================================" "Cyan"

Write-Status "`n✨ If any service shows 'Service starting...', wait 30 seconds and refresh the page." "Yellow"
Write-Status "✨ GPU initialization for Jitta may take up to 60 seconds on first start.`n" "Yellow"

# Return to original directory
Set-Location $PSScriptRoot

Write-Status "🎉 System startup complete!`n" "Green"
