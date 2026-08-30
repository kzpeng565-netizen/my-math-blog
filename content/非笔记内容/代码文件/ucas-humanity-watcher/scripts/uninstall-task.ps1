[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$TaskName = 'UCAS Humanity Lecture Watcher'
)

$ErrorActionPreference = 'Stop'
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if (-not $existing) {
    Write-Host "Scheduled task does not exist: $TaskName"
    exit 0
}

if ($PSCmdlet.ShouldProcess($TaskName, 'Remove logon task')) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Removed scheduled task: $TaskName"
}
