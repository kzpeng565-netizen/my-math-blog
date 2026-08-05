$ErrorActionPreference = 'Stop'
$taskName = 'Behavior Context Exporter'
$root = Split-Path -Parent $PSScriptRoot
$script = Join-Path $root 'behavior_context_exporter.py'
$config = Join-Path $root 'behavior_context_exporter.json'
$python = (Get-Command pythonw.exe -ErrorAction Stop).Source
$service = New-Object -ComObject 'Schedule.Service'
$service.Connect()
$folder = $service.GetFolder('\')
$task = $service.NewTask(0)
$task.RegistrationInfo.Description = 'Read-only Obsidian behavior context export'
$task.Settings.Enabled = $true
$task.Settings.Hidden = $true
$task.Settings.StartWhenAvailable = $true
$task.Settings.DisallowStartIfOnBatteries = $false
$task.Settings.StopIfGoingOnBatteries = $false
$task.Settings.MultipleInstances = 2 # TASK_INSTANCES_IGNORE_NEW
$task.Settings.RestartCount = 3
$task.Settings.RestartInterval = 'PT5M'
$logonTrigger = $task.Triggers.Create(9) # TASK_TRIGGER_LOGON
$logonTrigger.Enabled = $true

$timeTrigger = $task.Triggers.Create(1) # TASK_TRIGGER_TIME
$timeTrigger.Enabled = $true
$timeTrigger.StartBoundary = (Get-Date).AddMinutes(1).ToString("yyyy-MM-dd'T'HH:mm:ss")
$timeTrigger.Repetition.Interval = 'PT20M'
$timeTrigger.Repetition.Duration = 'P3650D'
$timeTrigger.Repetition.StopAtDurationEnd = $false
$action = $task.Actions.Create(0) # TASK_ACTION_EXEC
$action.Path = $python
$action.Arguments = "`"$script`" --config `"$config`""
$action.WorkingDirectory = $root
$user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$task.Principal.UserId = $user
$task.Principal.LogonType = 3
$task.Principal.RunLevel = 0
try {
    $folder.RegisterTaskDefinition($taskName, $task, 6, $null, $null, 3) | Out-Null
} catch [System.UnauthorizedAccessException] {
    throw 'Task Scheduler denied registration. Re-run this script from an elevated PowerShell window.'
}
Write-Host "Installed '$taskName'. It runs hidden at logon and every 20 minutes."
