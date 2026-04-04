# AutoShutdown タスク登録スクリプト
# 管理者権限の PowerShell で実行すること

# ---- 設定 ----
$HOURS = 4        # 何時間後にシャットダウンするか（変更可）
# --------------

$shutdownTime = (Get-Date).AddHours($HOURS)
$action  = New-ScheduledTaskAction -Execute "shutdown.exe" -Argument "/s /f /t 60"
$trigger = New-ScheduledTaskTrigger -Once -At $shutdownTime

Register-ScheduledTask -TaskName "AutoShutdown" -Action $action -Trigger $trigger -RunLevel Highest -Force

Write-Host "AutoShutdown を登録しました"
Write-Host "シャットダウン予定: $shutdownTime (さらに60秒後に実行)"
