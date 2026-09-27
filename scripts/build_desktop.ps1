# Build the Windows desktop app (Electron shell + PyInstaller backend).
# Output: desktop/release/VideoAnnotator-Setup-<ver>.exe (installer)
#         desktop/release/VideoAnnotator-<ver>-portable.exe (single exe, no install)
#         desktop/release/win-unpacked/VideoAnnotator.exe (unpacked folder)
# Usage: powershell -ExecutionPolicy Bypass -File scripts/build_desktop.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (-not (Test-Path ".venv")) { python -m venv .venv }
$py = Join-Path $root ".venv\Scripts\python.exe"
& $py -m pip install -q -e . pyinstaller
if ($LASTEXITCODE -ne 0) { throw "pip install failed" }

if (-not (Test-Path "labelu\internal\statics\index.html")) {
    & "$PSScriptRoot\fetch_frontend.ps1"
}

Write-Host "==> Building backend (PyInstaller)"
& (Join-Path $root ".venv\Scripts\pyinstaller.exe") desktop\backend\labelu-server.spec --noconfirm `
    --distpath desktop\backend\dist --workpath desktop\backend\build
if ($LASTEXITCODE -ne 0) { throw "PyInstaller build failed" }

Write-Host "==> Building Electron app"
Set-Location (Join-Path $root "desktop")
if (-not (Test-Path "node_modules")) { npm install }
npm run dist
if ($LASTEXITCODE -ne 0) { throw "electron-builder failed" }

Write-Host "Done. See desktop\release"
