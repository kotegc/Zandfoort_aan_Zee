# scripts\run_server.ps1
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot          # ...\sand_server
$venv = Join-Path $root "venv\Scripts\Activate.ps1"
$app  = Join-Path $root "app.py"

if (!(Test-Path $venv)) {
  Write-Host "ERROR: venv not found at $venv"
  Write-Host "Create it with: py -3.11 -m venv $root\venv"
  exit 1
}

. $venv
Set-Location $root

while ($true) {
  try {
    python $app
  } catch {
    Write-Host "Server crashed: $($_.Exception.Message)"
  }
  Start-Sleep -Seconds 1
  Write-Host "Restarting server..."
}
