$ErrorActionPreference = 'Stop'
$taskName = 'Behavior Context Exporter'
$service = New-Object -ComObject 'Schedule.Service'
$service.Connect()
$folder = $service.GetFolder('\')
try {
    $null = $folder.GetTask($taskName)
    $folder.DeleteTask($taskName, 0)
    Write-Host "Removed '$taskName'. Exported files were kept."
} catch {
    Write-Host "'$taskName' is not installed."
}
