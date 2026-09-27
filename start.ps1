# Start LabelU locally with SQLite (data stored in ./data, see .env).
# Usage: .\start.ps1 [-Port 8000]
param([int]$Port = 8000)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".venv")) {
    python -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -e .
}
if (-not (Test-Path "labelu\internal\statics\index.html")) {
    & "$PSScriptRoot\scripts\fetch_frontend.ps1"
}
if (-not (Test-Path ".env")) {
    Copy-Item .env.example .env
}

.\.venv\Scripts\labelu.exe --port $Port --media-host "http://localhost:$Port"
