param([int]$ListenPort = 8000, [switch]$InstallDependencies)
$ErrorActionPreference = 'Stop'
$canonicalScript = Join-Path (Split-Path -Parent $PSScriptRoot) 'starter_v0\run.ps1'
& $canonicalScript -ListenPort $ListenPort -InstallDependencies:$InstallDependencies
exit $LASTEXITCODE
