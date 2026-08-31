$startup = [Environment]::GetFolderPath('Startup')
$launcher = Join-Path $startup 'Pi Hotspot Fallback.vbs'
Remove-Item -LiteralPath $launcher -Force -ErrorAction SilentlyContinue

Get-CimInstance Win32_Process |
    Where-Object {
        $_.Name -match '^powershell(\.exe)?$' -and
        $_.CommandLine -like '*hotspot-watchdog.ps1*'
    } |
    ForEach-Object {
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }

if (Get-ScheduledTask -TaskName 'Pi Hotspot Fallback' -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName 'Pi Hotspot Fallback' -Confirm:$false
}
Write-Output "Removed startup launcher: $launcher"
