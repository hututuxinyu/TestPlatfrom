$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

Write-Host "Starting backend (http://localhost:8000)..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd `"$Root\backend`"; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

Write-Host "Starting frontend (http://localhost:5173)..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd `"$Root\frontend`"; npm run dev -- --host 0.0.0.0 --port 5173"

Write-Host "Both local services were launched in new terminals."
