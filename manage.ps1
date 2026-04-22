param (
    [Parameter(Mandatory = $true)]
    [ValidateSet("start", "stop")]
    [string]$Action
)

function Start-All {
    Write-Host "[START] Starting Pathfinder.Ai Ecosystem..." -ForegroundColor Cyan

    # 0. Start Redis (using full path since it may not be in PATH)
    Write-Host "-> Starting Redis Server..."
    $redisExe = "C:\Program Files\Redis\redis-server.exe"
    if (Test-Path $redisExe) {
        Start-Process $redisExe -WindowStyle Minimized
        Write-Host "   Redis started." -ForegroundColor Green
    }
    else {
        Write-Host "[WARNING] Redis not found at $redisExe" -ForegroundColor Red
    }

    Start-Sleep -Seconds 2

    # 1. Start Backend (Flask)
    Write-Host "-> Launching Flask API..."
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PSScriptRoot'; .\venv\Scripts\activate; python app.py" -WindowStyle Normal

    Start-Sleep -Seconds 2

    # 2. Start Celery Worker (--pool=solo required on Windows)
    Write-Host "-> Launching Celery Worker..."
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PSScriptRoot'; .\venv\Scripts\activate; celery -A app.celery_app worker --loglevel=info --pool=solo" -WindowStyle Normal

    # 3. Start Celery Beat
    Write-Host "-> Launching Celery Beat..."
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PSScriptRoot'; .\venv\Scripts\activate; celery -A app.celery_app beat --loglevel=info" -WindowStyle Normal

    # 4. Start Frontend
    Write-Host "-> Launching Vue Frontend..."
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PSScriptRoot\pathfinder-frontend'; npm run serve" -WindowStyle Normal

    Write-Host "[OK] All processes launched!" -ForegroundColor Green
    Write-Host "Frontend : http://localhost:8080" -ForegroundColor Yellow
    Write-Host "Backend  : http://localhost:5000" -ForegroundColor Yellow
}

function Stop-All {
    Write-Host "[STOP] Shutting down all Pathfinder processes..." -ForegroundColor Red

    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
    Get-Process node   -ErrorAction SilentlyContinue | Stop-Process -Force
    Get-Process redis-server -ErrorAction SilentlyContinue | Stop-Process -Force

    Write-Host "[OK] All processes cleared." -ForegroundColor Green
}

if ($Action -eq "start") { Start-All }
elseif ($Action -eq "stop") { Stop-All }
