$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$nodePath = (Get-Command node -ErrorAction Stop).Source
$entryPath = Join-Path $projectRoot 'src\main.mjs'

Set-Location -LiteralPath $projectRoot
& $nodePath $entryPath
exit $LASTEXITCODE
