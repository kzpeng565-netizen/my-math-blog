[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$TaskName = 'UCAS Humanity Lecture Watcher'
)

$ErrorActionPreference = 'Stop'
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if (-not $existing) {
    Write-Host "计划任务不存在：$TaskName"
    exit 0
}

if ($PSCmdlet.ShouldProcess($TaskName, '删除登录启动任务')) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "已删除计划任务：$TaskName"
}
