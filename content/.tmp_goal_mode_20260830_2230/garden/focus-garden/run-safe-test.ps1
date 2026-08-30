$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $root
& 'D:\anaconda\python.exe' (Join-Path $root 'app.py') --dry-run

