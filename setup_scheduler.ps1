# Creates a Windows Task Scheduler job that runs poll_dropbox.py once a day at 08:00.
# Run this once from PowerShell (no admin required for current-user tasks):
#   .\setup_scheduler.ps1

$taskName   = "PokemonNuzlockeSync"
$scriptPath = Join-Path $PSScriptRoot "poll_dropbox.py"
$python     = (Get-Command python).Source
$logPath    = Join-Path $PSScriptRoot "sync.log"

$action  = New-ScheduledTaskAction -Execute $python -Argument "`"$scriptPath`" >> `"$logPath`" 2>&1"
$trigger = New-ScheduledTaskTrigger -Daily -At "08:00"
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable

# Remove existing task if present
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger `
    -Settings $settings -Description "Download FireRed .sav files from Dropbox and update nuzlocke tracker"

Write-Host ""
Write-Host "Scheduled task '$taskName' created — runs daily at 08:00."
Write-Host "Log output: $logPath"
Write-Host ""
Write-Host "To run it now manually:"
Write-Host "  python `"$scriptPath`""
