$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$desktop = [Environment]::GetFolderPath('Desktop')
$shell = New-Object -ComObject WScript.Shell
$shortcutName = (-join @(0x6211,0x7684,0x4E13,0x6CE8,0x82B1,0x56ED | ForEach-Object { [char]$_ })) + '.lnk'
$shortcutPath = Join-Path $desktop $shortcutName
Get-ChildItem -LiteralPath $desktop -Filter '*.lnk' -File | ForEach-Object {
    $old = $shell.CreateShortcut($_.FullName)
    if ($old.TargetPath -eq 'D:\anaconda\pythonw.exe' -and $old.Arguments -like '*MyFocusGarden*launch.pyw*' -and $_.FullName -ne $shortcutPath) {
        Remove-Item -LiteralPath $_.FullName -Force
    }
}
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = 'D:\anaconda\pythonw.exe'
$shortcut.Arguments = '"' + (Join-Path $root 'launch.pyw') + '"'
$shortcut.WorkingDirectory = $root
$shortcut.Description = 'Launch My Focus Garden'
$shortcut.Save()
Write-Output $shortcutPath
