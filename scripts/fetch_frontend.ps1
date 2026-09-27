# Download the prebuilt labelU-Kit frontend (version from .VERSION) into labelu/internal/statics.
# Usage: powershell -File scripts/fetch_frontend.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$url = (Select-String -Path "$root\.VERSION" -Pattern "^release_assets_url: (.+)$").Matches[0].Groups[1].Value.Trim()

$zip = Join-Path $env:TEMP "labelu-frontend.zip"
$tmp = Join-Path $env:TEMP "labelu-frontend"
Write-Host "Downloading $url"
Invoke-WebRequest -Uri $url -OutFile $zip

if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
Expand-Archive -Path $zip -DestinationPath $tmp
Copy-Item -Recurse -Force "$tmp\dist\*" "$root\labelu\internal\statics\"
Remove-Item -Force $zip
Remove-Item -Recurse -Force $tmp
Write-Host "Frontend installed to labelu/internal/statics"
