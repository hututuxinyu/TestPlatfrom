param(
    [switch]$SkipFrontend
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

Write-Host "[1/5] Ensuring backend virtual environment..."
if (-not (Test-Path "$Root\backend\.venv\Scripts\python.exe")) {
    python -m venv "$Root\backend\.venv"
}

if (-not (Test-Path "$Root\backend\.env")) {
    Copy-Item "$Root\backend\.env.example" "$Root\backend\.env"
}

Write-Host "[2/5] Installing backend dependencies into .venv..."
Push-Location "$Root\backend"
& ".\.venv\Scripts\python.exe" -m pip install -r ".\requirements.txt"
& ".\.venv\Scripts\python.exe" -m app.init_db
Pop-Location

if (-not $SkipFrontend) {
    Write-Host "[3/5] Installing frontend dependencies..."
    npm install --prefix "$Root\frontend"
} else {
    Write-Host "[3/5] Skipped frontend dependency install."
}

Write-Host "[4/5] Backend database initialized."
Write-Host "[5/5] Local setup complete."
