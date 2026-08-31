[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$timestamp = Get-Date -Format 'yyyy-MM-dd_HHmmss'
$backupBase = 'C:\Users\15345\OpenSSH-Backup'
$backupRoot = Join-Path $backupBase "$timestamp-before-repair"
$programDataSsh = 'C:\ProgramData\ssh'
$userAuthorizedKeys = 'C:\Users\15345\.ssh\authorized_keys'
$codexLauncher = 'C:\Users\15345\bin\codex-project.ps1'
$sshdPath = 'C:\Windows\System32\OpenSSH\sshd.exe'
$sshKeygenPath = 'C:\Windows\System32\OpenSSH\ssh-keygen.exe'
$capabilityName = 'OpenSSH.Server~~~~0.0.1.0'

New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null

$currentPrincipal = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
& icacls.exe $backupRoot /inheritance:r | Out-Null
& icacls.exe $backupRoot /grant:r `
    "${currentPrincipal}:(OI)(CI)F" `
    '*S-1-5-18:(OI)(CI)F' `
    '*S-1-5-32-544:(OI)(CI)F' | Out-Null

if (Test-Path -LiteralPath $programDataSsh -PathType Container) {
    Copy-Item -LiteralPath $programDataSsh `
        -Destination (Join-Path $backupRoot 'ProgramData-ssh') `
        -Recurse -Force
    & icacls.exe $programDataSsh `
        /save (Join-Path $backupRoot 'ProgramData-ssh-acl.txt') `
        /t /c | Out-Null
}

if (Test-Path -LiteralPath $userAuthorizedKeys -PathType Leaf) {
    Copy-Item -LiteralPath $userAuthorizedKeys `
        -Destination (Join-Path $backupRoot 'authorized_keys') `
        -Force
    & icacls.exe $userAuthorizedKeys `
        /save (Join-Path $backupRoot 'authorized_keys-acl.txt') `
        /c | Out-Null
}

if (Test-Path -LiteralPath $codexLauncher -PathType Leaf) {
    Copy-Item -LiteralPath $codexLauncher `
        -Destination (Join-Path $backupRoot 'codex-project.ps1') `
        -Force
}

$capabilityBefore = Get-WindowsCapability -Online -Name $capabilityName
$serviceBefore = Get-Service -Name sshd -ErrorAction SilentlyContinue
$firewallBefore = Get-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -ErrorAction SilentlyContinue
$listenerBefore = Get-NetTCPConnection -LocalPort 22 -State Listen -ErrorAction SilentlyContinue

[pscustomobject]@{
    CapturedAt = Get-Date -Format o
    CapabilityState = $capabilityBefore.State
    ServiceExists = $null -ne $serviceBefore
    ServiceStatus = if ($serviceBefore) { $serviceBefore.Status.ToString() } else { 'Missing' }
    FirewallRuleExists = $null -ne $firewallBefore
    FirewallRuleEnabled = if ($firewallBefore) { $firewallBefore.Enabled.ToString() } else { 'Missing' }
    Port22Listening = $null -ne $listenerBefore
} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $backupRoot 'pre-repair-state.json') -Encoding UTF8

Get-ChildItem -LiteralPath $backupRoot -Recurse -File |
    Get-FileHash -Algorithm SHA256 |
    Select-Object Path, Hash |
    Export-Csv -LiteralPath (Join-Path $backupRoot 'backup-sha256.csv') -NoTypeInformation -Encoding UTF8

if ($capabilityBefore.State -ne 'Installed') {
    $capabilityAfterInstall = Add-WindowsCapability -Online -Name $capabilityName
    if ($capabilityAfterInstall.RestartNeeded) {
        throw 'OpenSSH Server installation requires a restart before repair can continue.'
    }
}

if (-not (Test-Path -LiteralPath $sshdPath -PathType Leaf)) {
    throw "OpenSSH server executable is missing: $sshdPath"
}

$hostKey = Get-ChildItem -LiteralPath $programDataSsh -Filter 'ssh_host_*_key' -File -ErrorAction SilentlyContinue |
    Select-Object -First 1
if (-not $hostKey) {
    & $sshKeygenPath -A
    if ($LASTEXITCODE -ne 0) {
        throw "ssh-keygen -A failed with exit code $LASTEXITCODE"
    }
}

& $sshdPath -t
if ($LASTEXITCODE -ne 0) {
    throw "sshd configuration validation failed with exit code $LASTEXITCODE"
}

$sshdService = Get-Service -Name sshd -ErrorAction SilentlyContinue
if (-not $sshdService) {
    New-Service `
        -Name 'sshd' `
        -BinaryPathName $sshdPath `
        -DisplayName 'OpenSSH SSH Server' `
        -Description 'OpenSSH SSH Server' `
        -StartupType Automatic `
        -DependsOn 'Tcpip' | Out-Null
}
else {
    Set-Service -Name sshd -StartupType Automatic
}

& sc.exe failure sshd reset= 86400 actions= restart/5000/restart/5000/restart/5000 | Out-Null
& sc.exe failureflag sshd 1 | Out-Null

$firewallRule = Get-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -ErrorAction SilentlyContinue
if ($firewallRule) {
    Set-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -Enabled True -Action Allow
}
else {
    New-NetFirewallRule `
        -Name 'OpenSSH-Server-In-TCP' `
        -DisplayName 'OpenSSH SSH Server (sshd)' `
        -Enabled True `
        -Direction Inbound `
        -Protocol TCP `
        -Action Allow `
        -LocalPort 22 `
        -Profile Any | Out-Null
}

Start-Service -Name sshd
Start-Sleep -Seconds 2

$serviceAfter = Get-Service -Name sshd
$listenerAfter = Get-NetTCPConnection -LocalPort 22 -State Listen -ErrorAction Stop
$firewallAfter = Get-NetFirewallRule -Name 'OpenSSH-Server-In-TCP'
$capabilityAfter = Get-WindowsCapability -Online -Name $capabilityName

[pscustomobject]@{
    CompletedAt = Get-Date -Format o
    BackupPath = $backupRoot
    CapabilityState = $capabilityAfter.State
    ServiceStatus = $serviceAfter.Status.ToString()
    ServiceStartType = $serviceAfter.StartType.ToString()
    FirewallEnabled = $firewallAfter.Enabled.ToString()
    FirewallAction = $firewallAfter.Action.ToString()
    ListeningAddresses = @($listenerAfter | ForEach-Object { "$($_.LocalAddress):$($_.LocalPort)" })
} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $backupRoot 'post-repair-state.json') -Encoding UTF8

Write-Output "BACKUP_PATH=$backupRoot"
Write-Output "CAPABILITY_STATE=$($capabilityAfter.State)"
Write-Output "SERVICE_STATUS=$($serviceAfter.Status)"
Write-Output "SERVICE_START_TYPE=$($serviceAfter.StartType)"
Write-Output "FIREWALL_ENABLED=$($firewallAfter.Enabled)"
Write-Output "PORT22_LISTENERS=$(@($listenerAfter).Count)"
