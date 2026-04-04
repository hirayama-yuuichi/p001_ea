# AutoShutdown タスク確認スクリプト

Write-Host "=== AutoShutdown タスク状態 ==="
try {
    $task = Get-ScheduledTask -TaskName "AutoShutdown" -ErrorAction Stop
    $info = $task | Get-ScheduledTaskInfo

    Write-Host "状態        : $($task.State)"
    Write-Host "次回実行    : $($info.NextRunTime)"
    Write-Host "前回実行    : $($info.LastRunTime)"
    Write-Host ""
    Write-Host "--- アクション ---"
    $task.Actions | ForEach-Object { Write-Host "  $($_.Execute) $($_.Arguments)" }
    Write-Host ""
    Write-Host "--- トリガー ---"
    $task.Triggers | ForEach-Object { Write-Host "  実行時刻: $($_.StartBoundary)" }
} catch {
    Write-Host "AutoShutdown タスクが見つかりません（未登録または削除済み）"
}

Write-Host ""
Write-Host "=== ユーザー登録タスク一覧 ==="
Get-ScheduledTask | Where-Object { $_.TaskPath -eq "\" } | Select-Object TaskName, State | Sort-Object TaskName | Format-Table -AutoSize

Read-Host "Enterキーで閉じる"
