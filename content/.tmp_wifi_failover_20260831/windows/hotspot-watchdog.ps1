$ErrorActionPreference = 'Continue'

$created = $false
$mutex = New-Object System.Threading.Mutex(
    $true,
    'Local\PiHotspotFallbackWatchdog',
    [ref]$created
)
if (-not $created) {
    exit 0
}

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ensureScript = Join-Path $root 'ensure-hotspot.ps1'
$powershell = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
$watchdogLogRoot = Join-Path $env:LOCALAPPDATA 'PiNetworkFallback'
$watchdogLog = Join-Path $watchdogLogRoot 'watchdog.jsonl'
New-Item -ItemType Directory -Force -Path $watchdogLogRoot | Out-Null

try {
    while ($true) {
        $started = Get-Date
        try {
            $process = Start-Process `
                -FilePath $powershell `
                -ArgumentList (
                    '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "{0}"' -f $ensureScript
                ) `
                -WindowStyle Hidden `
                -Wait `
                -PassThru
            $exitCode = $process.ExitCode
        }
        catch {
            $exitCode = -1
        }
        $event = [ordered]@{
            at = $started.ToString('o')
            ensure_exit_code = $exitCode
        }
        Add-Content `
            -LiteralPath $watchdogLog `
            -Value ($event | ConvertTo-Json -Compress) `
            -Encoding UTF8
        Start-Sleep -Seconds 300
    }
}
finally {
    $mutex.ReleaseMutex()
    $mutex.Dispose()
}
