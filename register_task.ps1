# Register scheduled task for morning English bot
# Run this in PowerShell as Administrator

$TaskName = "아침영어"

# Remove existing task if it exists
try {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
} catch {}

# Create trigger for 7:00 AM daily
$Trigger = New-ScheduledTaskTrigger -Daily -At 07:00

# Create action
$Action = New-ScheduledTaskAction `
    -Execute "C:\myenglishbot\아침영어.bat" `
    -WorkingDirectory "C:\myenglishbot"

# Create settings
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

# Register the task
Register-ScheduledTask `
    -TaskName $TaskName `
    -Trigger $Trigger `
    -Action $Action `
    -Settings $Settings `
    -Description "Daily morning English conversation at 7:00 AM"

Write-Host "Task registered successfully!" -ForegroundColor Green
