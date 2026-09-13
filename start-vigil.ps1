$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Start-Process powershell -ArgumentList '-NoExit','-Command',("Set-Location ''" + $Root + "'ackend'; python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000")
Start-Process powershell -ArgumentList '-NoExit','-Command',("Set-Location ''" + $Root + "'rontend'; npm run dev")
Write-Host "VIGIL backend and frontend terminals started."
