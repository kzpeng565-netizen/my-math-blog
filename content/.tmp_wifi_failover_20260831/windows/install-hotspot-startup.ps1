$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$watchdog = Join-Path $root 'hotspot-watchdog.ps1'
$startup = [Environment]::GetFolderPath('Startup')
$launcher = Join-Path $startup 'Pi Hotspot Fallback.vbs'
$powershell = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'

if (-not (Test-Path -LiteralPath $watchdog -PathType Leaf)) {
    throw "Missing $watchdog"
}

$escapedPowerShell = $powershell.Replace('"', '""')
$escapedWatchdog = $watchdog.Replace('"', '""')
$vbs = @"
Set shell = CreateObject("WScript.Shell")
shell.Run """$escapedPowerShell"" -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File ""$escapedWatchdog""", 0, False
"@
Set-Content -LiteralPath $launcher -Value $vbs -Encoding ASCII

Start-Process `
    -FilePath (Join-Path $env:SystemRoot 'System32\wscript.exe') `
    -ArgumentList ('"{0}"' -f $launcher) `
    -WindowStyle Hidden

Write-Output "Installed startup launcher: $launcher"
