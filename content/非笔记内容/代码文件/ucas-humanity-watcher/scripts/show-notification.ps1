param(
    [Parameter(Mandatory = $true)]
    [string]$Title,

    [Parameter(Mandatory = $true)]
    [string]$Message,

    [string]$OpenUrl = '',

    [ValidateSet('true', 'false')]
    [string]$Sound = 'true'
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$notification = New-Object System.Windows.Forms.NotifyIcon
$notification.Icon = [System.Drawing.SystemIcons]::Information
$notification.Text = 'UCAS Humanity Watcher'
$notification.BalloonTipTitle = $Title
$notification.BalloonTipText = $Message
$notification.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Info
$notification.Visible = $true

$clicked = $false
if ($OpenUrl) {
    $notification.add_BalloonTipClicked({
        $script:clicked = $true
        Start-Process -FilePath $OpenUrl
    })
}

if ($Sound -eq 'true') {
    [System.Media.SystemSounds]::Asterisk.Play()
}
$notification.ShowBalloonTip(10000)

$deadline = (Get-Date).AddSeconds(12)
while ((Get-Date) -lt $deadline -and -not $clicked) {
    [System.Windows.Forms.Application]::DoEvents()
    Start-Sleep -Milliseconds 100
}

$notification.Visible = $false
$notification.Dispose()
