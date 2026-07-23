$ErrorActionPreference = "Stop"

$activityWatchApi = "http://127.0.0.1:5600/api/0/info"
$activityWatchSync = "D:\ActivityWatch\aw-server-rust\aw-sync.exe"
$syncDirectory = "C:\Users\15345\ActivityWatchSync"
$stateDirectory = Join-Path $env:LOCALAPPDATA "ActivityWatchPiSync"
$logDirectory = Join-Path $stateDirectory "logs"
$statusFile = Join-Path $stateDirectory "status.json"
$logFile = Join-Path $logDirectory ("sync-{0}.log" -f (Get-Date -Format "yyyy-MM-dd"))

New-Item -ItemType Directory -Path $syncDirectory -Force | Out-Null
New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null

$status = [ordered]@{
    checked_at = (Get-Date).ToString("o")
    ok = $false
    activitywatch_version = $null
    sync_directory = $syncDirectory
    last_error = $null
}

try {
    if (-not (Test-Path -LiteralPath $activityWatchSync)) {
        throw "aw-sync not found: $activityWatchSync"
    }

    $info = Invoke-RestMethod -Uri $activityWatchApi -TimeoutSec 10
    $status.activitywatch_version = $info.version

    "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Sync started" |
        Out-File -LiteralPath $logFile -Append -Encoding utf8

    & $activityWatchSync --sync-dir $syncDirectory sync-advanced --mode push *>> $logFile

    if ($LASTEXITCODE -ne 0) {
        throw "aw-sync exited with code $LASTEXITCODE. See log: $logFile"
    }

    $status.ok = $true
    "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Sync completed" |
        Out-File -LiteralPath $logFile -Append -Encoding utf8
}
catch {
    $status.last_error = $_.Exception.Message
    "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Sync failed: $($_.Exception.Message)" |
        Out-File -LiteralPath $logFile -Append -Encoding utf8
}
finally {
    $status.checked_at = (Get-Date).ToString("o")
    $status | ConvertTo-Json | Set-Content -LiteralPath $statusFile -Encoding utf8
}

if (-not $status.ok) {
    exit 1
}
