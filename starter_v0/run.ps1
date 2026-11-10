param(
    [string]$BindAddress = '127.0.0.1',
    [int]$ListenPort = 8000,
    [switch]$InstallDependencies,
    [switch]$Reload
)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$pythonPath = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Cannot create .venv; install Python 3.10+ first.' }
    $InstallDependencies = $true
}
if ($InstallDependencies) {
    & $pythonPath -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
}
$env:PYTHONUTF8 = '1'
Write-Host "Research Chatbot: http://${BindAddress}:${ListenPort}/"
$uvicornArgs = @('-m', 'uvicorn', 'app.main:app', '--host', $BindAddress, '--port', "$ListenPort")
if ($Reload) { $uvicornArgs += '--reload' }
& $pythonPath @uvicornArgs
exit $LASTEXITCODE
