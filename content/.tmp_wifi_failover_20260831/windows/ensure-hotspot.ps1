$ErrorActionPreference = 'Stop'

$expectedSsid = 'XYH 0563'
$logRoot = Join-Path $env:LOCALAPPDATA 'PiNetworkFallback'
$logPath = Join-Path $logRoot 'hotspot-ensure.jsonl'
New-Item -ItemType Directory -Force -Path $logRoot | Out-Null

function Write-Event {
    param(
        [string]$Action,
        [string]$State,
        [string]$Detail = ''
    )
    $event = [ordered]@{
        at = (Get-Date).ToString('o')
        action = $Action
        state = $State
        detail = $Detail
    }
    Add-Content -LiteralPath $logPath -Value ($event | ConvertTo-Json -Compress) -Encoding UTF8
}

function Wait-WinRtOperation {
    param(
        [Parameter(Mandatory = $true)]$Operation,
        [Parameter(Mandatory = $true)][Type]$ResultType,
        [int]$TimeoutMilliseconds = 30000
    )
    $definition = [System.WindowsRuntimeSystemExtensions].GetMethods() |
        Where-Object {
            $_.Name -eq 'AsTask' -and
            $_.IsGenericMethodDefinition -and
            $_.GetGenericArguments().Count -eq 1 -and
            $_.GetParameters().Count -eq 1 -and
            $_.ReturnType.Name -eq 'Task`1'
        } |
        Select-Object -First 1
    if ($null -eq $definition) {
        throw 'Unable to locate WinRT AsTask<TResult>.'
    }
    $task = $definition.MakeGenericMethod($ResultType).Invoke($null, @($Operation))
    if (-not $task.Wait($TimeoutMilliseconds)) {
        throw 'Windows Mobile Hotspot operation timed out.'
    }
    return $task.Result
}

try {
    Add-Type -AssemblyName System.Runtime.WindowsRuntime
    [Windows.Networking.Connectivity.NetworkInformation,Windows.Networking.Connectivity,ContentType=WindowsRuntime] | Out-Null
    [Windows.Networking.NetworkOperators.NetworkOperatorTetheringManager,Windows.Networking.NetworkOperators,ContentType=WindowsRuntime] | Out-Null
    [Windows.Networking.NetworkOperators.NetworkOperatorTetheringOperationResult,Windows.Networking.NetworkOperators,ContentType=WindowsRuntime] | Out-Null

    $profile = [Windows.Networking.Connectivity.NetworkInformation]::GetInternetConnectionProfile()
    if ($null -eq $profile) {
        throw 'No internet connection profile is available.'
    }
    $manager = [Windows.Networking.NetworkOperators.NetworkOperatorTetheringManager]::CreateFromConnectionProfile($profile)
    $configuration = $manager.GetCurrentAccessPointConfiguration()
    if ($configuration.Ssid -ne $expectedSsid) {
        throw "Unexpected Mobile Hotspot SSID: $($configuration.Ssid)"
    }

    $state = $manager.TetheringOperationalState.ToString()
    if ($state -eq 'On') {
        Write-Event -Action 'already_on' -State $state -Detail "clients=$($manager.ClientCount)"
        exit 0
    }

    $resultType = [Windows.Networking.NetworkOperators.NetworkOperatorTetheringOperationResult]
    $result = Wait-WinRtOperation -Operation ($manager.StartTetheringAsync()) -ResultType $resultType
    Start-Sleep -Seconds 2
    $after = $manager.TetheringOperationalState.ToString()
    Write-Event -Action 'start' -State $after -Detail $result.Status.ToString()
    if ($result.Status.ToString() -ne 'Success' -or $after -ne 'On') {
        throw "Mobile Hotspot did not start: $($result.Status) $($result.AdditionalErrorMessage)"
    }
}
catch {
    Write-Event -Action 'error' -State 'unknown' -Detail $_.Exception.Message
    exit 1
}
