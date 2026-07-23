$ErrorActionPreference = "Stop"

$modulePath = "C:\Users\15345\Documents\WindowsPowerShell\Modules\Posh-SSH\3.2.7\Posh-SSH.psd1"
$localSyncthing = "C:\Users\15345\AppData\Local\Microsoft\WinGet\Packages\Syncthing.Syncthing_Microsoft.Winget.Source_8wekyb3d8bbwe\syncthing-windows-amd64-v2.1.2\syncthing.exe"
$windowsDeviceId = "CUAX64H-HUZ2ARI-MTAVW7A-2GFXWOW-YKQQ3M6-GOQQFSL-5GZ6PJI-VQGKTAA"
$stateDirectory = Join-Path $env:LOCALAPPDATA "ActivityWatchPiSync"
$deploymentStatusFile = Join-Path $stateDirectory "pi-deployment-status.json"

New-Item -ItemType Directory -Path $stateDirectory -Force | Out-Null

$status = [ordered]@{
    checked_at = (Get-Date).ToString("o")
    ok = $false
    phase = "credential"
    pi_hostname = $null
    pi_addresses = $null
    system_state = $null
    memory = $null
    root_disk = $null
    throttled = $null
    syncthing_version = $null
    pi_device_id = $null
    remote_file = $null
    last_error = $null
}

$session = $null

try {
    Import-Module $modulePath -Force

    $credential = Get-Credential -UserName "conrad" -Message "Enter the password for conrad@pi.local. The password is used only in memory."
    if ($null -eq $credential) {
        throw "Credential entry was cancelled."
    }

    $status.phase = "connect"
    $session = New-SSHSession -ComputerName "pi.local" -Credential $credential -ConnectionTimeout 15 -KeepAliveInterval 10 -AcceptKey

    $snapshotCommand = @'
set -eu
printf 'HOSTNAME=%s\n' "$(hostname)"
printf 'ADDRESSES=%s\n' "$(hostname -I | xargs)"
printf 'SYSTEM_STATE=%s\n' "$(systemctl is-system-running || true)"
printf 'MEMORY=%s\n' "$(free -h | awk '/^Mem:/ {print $2 " total, " $3 " used, " $7 " available"}')"
printf 'ROOT_DISK=%s\n' "$(df -h / | awk 'NR==2 {print $2 " total, " $3 " used, " $4 " available, " $5 " used"}')"
printf 'THROTTLED=%s\n' "$(vcgencmd get_throttled 2>/dev/null || echo unavailable)"
'@
    $snapshot = Invoke-SSHCommand -SSHSession $session -Command $snapshotCommand -TimeOut 30
    if ($snapshot.ExitStatus -ne 0) {
        throw "Pi status snapshot failed."
    }

    foreach ($line in $snapshot.Output) {
        if ($line -match "^HOSTNAME=(.*)$") { $status.pi_hostname = $Matches[1] }
        elseif ($line -match "^ADDRESSES=(.*)$") { $status.pi_addresses = $Matches[1] }
        elseif ($line -match "^SYSTEM_STATE=(.*)$") { $status.system_state = $Matches[1] }
        elseif ($line -match "^MEMORY=(.*)$") { $status.memory = $Matches[1] }
        elseif ($line -match "^ROOT_DISK=(.*)$") { $status.root_disk = $Matches[1] }
        elseif ($line -match "^THROTTLED=(.*)$") { $status.throttled = $Matches[1] }
    }

    $status.phase = "install"
    $installCommand = @'
set -eu
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y syncthing
sudo install -d -m 0750 -o conrad -g conrad /home/conrad/workspace/activitywatch-sync
sudo systemctl enable --now syncthing@conrad.service
'@
    $install = Invoke-SSHCommand -SSHSession $session -Command $installCommand -TimeOut 900
    if ($install.ExitStatus -ne 0) {
        throw "Syncthing installation failed: $($install.Error -join ' ')"
    }

    $status.phase = "configure_pi"
    $piConfigCommand = @"
set -eu
for i in `$(seq 1 30); do
  if syncthing cli show system >/dev/null 2>&1; then break; fi
  sleep 1
done
syncthing cli config devices list | grep -Fx '$windowsDeviceId' >/dev/null ||
  syncthing cli config devices add --device-id='$windowsDeviceId' --name='Windows-xyh'
syncthing cli config folders list | grep -Fx 'activitywatch-sync' >/dev/null ||
  syncthing cli config folders add --id='activitywatch-sync' --label='ActivityWatch Sync from PC' --path='/home/conrad/workspace/activitywatch-sync' --type='receiveonly' --rescan-intervals='300'
syncthing cli config folders activitywatch-sync devices list | grep -Fx '$windowsDeviceId' >/dev/null ||
  syncthing cli config folders activitywatch-sync devices add --device-id='$windowsDeviceId'
printf 'VERSION=%s\n' "`$(syncthing --version | head -n 1)"
printf 'DEVICE_ID=%s\n' "`$(syncthing cli show system | python3 -c 'import json,sys; print(json.load(sys.stdin)["myID"])')"
"@
    $piConfig = Invoke-SSHCommand -SSHSession $session -Command $piConfigCommand -TimeOut 120
    if ($piConfig.ExitStatus -ne 0) {
        throw "Pi Syncthing configuration failed: $($piConfig.Error -join ' ')"
    }

    foreach ($line in $piConfig.Output) {
        if ($line -match "^VERSION=(.*)$") { $status.syncthing_version = $Matches[1] }
        elseif ($line -match "^DEVICE_ID=(.*)$") { $status.pi_device_id = $Matches[1] }
    }

    if ([string]::IsNullOrWhiteSpace($status.pi_device_id)) {
        throw "Pi Syncthing device ID was not returned."
    }

    $status.phase = "configure_windows"
    $windowsDevices = & $localSyncthing cli config devices list
    if ($windowsDevices -notcontains $status.pi_device_id) {
        & $localSyncthing cli config devices add --device-id=$status.pi_device_id --name="RaspberryPi"
        if ($LASTEXITCODE -ne 0) { throw "Adding the Pi device to Windows Syncthing failed." }
    }

    $sharedDevices = & $localSyncthing cli config folders activitywatch-sync devices list
    if ($sharedDevices -notcontains $status.pi_device_id) {
        & $localSyncthing cli config folders activitywatch-sync devices add --device-id=$status.pi_device_id
        if ($LASTEXITCODE -ne 0) { throw "Sharing the ActivityWatch folder with the Pi failed." }
    }

    $status.phase = "verify_transfer"
    for ($attempt = 1; $attempt -le 24; $attempt++) {
        $verify = Invoke-SSHCommand -SSHSession $session -Command "find /home/conrad/workspace/activitywatch-sync -maxdepth 3 -type f -name 'test.db' -printf '%p|%s\n' | head -n 1" -TimeOut 30
        if ($verify.ExitStatus -eq 0 -and $verify.Output.Count -gt 0) {
            $status.remote_file = $verify.Output[0]
            break
        }
        Start-Sleep -Seconds 5
    }

    if ([string]::IsNullOrWhiteSpace($status.remote_file)) {
        throw "The ActivityWatch database did not reach the Pi within two minutes."
    }

    $status.phase = "complete"
    $status.ok = $true
}
catch {
    $status.last_error = $_.Exception.Message
}
finally {
    if ($null -ne $session) {
        Remove-SSHSession -SSHSession $session | Out-Null
    }
    $status.checked_at = (Get-Date).ToString("o")
    $status | ConvertTo-Json | Set-Content -LiteralPath $deploymentStatusFile -Encoding utf8
}

if (-not $status.ok) {
    Write-Host "Deployment failed: $($status.last_error)" -ForegroundColor Red
    Write-Host "Status: $deploymentStatusFile"
    Read-Host "Press Enter to close"
    exit 1
}

Write-Host "Deployment completed and verified." -ForegroundColor Green
Write-Host "Status: $deploymentStatusFile"
Start-Sleep -Seconds 3
