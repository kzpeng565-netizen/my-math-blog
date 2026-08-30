[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$TaskName = 'UCAS Humanity Lecture Watcher',
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing -and -not $Force) {
    throw "计划任务 '$TaskName' 已存在。若确需覆盖，请显式添加 -Force。"
}

$runnerPath = Join-Path $PSScriptRoot 'run-watcher.ps1'
$powerShellPath = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
$arguments = "-NoLogo -NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$runnerPath`""
$currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

$action = New-ScheduledTaskAction -Execute $powerShellPath -Argument $arguments -WorkingDirectory (Split-Path -Parent $PSScriptRoot)
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $currentUser
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit ([TimeSpan]::Zero)

if ($PSCmdlet.ShouldProcess($TaskName, '注册当前用户登录启动任务')) {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Description '每分钟检查国科大雁栖湖人文讲座；真实预约须由用户在本地面板确认。' `
        -User $currentUser `
        -Force | Out-Null
    Write-Host "已注册计划任务：$TaskName"
}
