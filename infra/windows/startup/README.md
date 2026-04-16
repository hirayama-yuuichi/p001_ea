# startup — 起動時スクリプト

EC2 Windows 起動時に自動実行するスクリプト群。

## ファイル

| ファイル | 説明 |
|---|---|
| `record_ip.ps1` | パブリックIPを SSM Parameter Store に記録 |

## record_ip.ps1 の動作

1. EC2 インスタンスメタデータ（`169.254.169.254`）からパブリックIPを取得
2. SSM Parameter Store に書き込み
   - `/p001ea/windows/public_ip` ← パブリックIP
   - `/p001ea/windows/instance_id` ← インスタンスID

## Windows スタートアップへの登録方法

PowerShell（管理者）で以下を実行：

```powershell
$action  = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -File C:\Users\hy\p001_ea\infra\windows\startup\record_ip.ps1"
$trigger = New-ScheduledTaskTrigger -AtStartup
Register-ScheduledTask -TaskName "RecordIP" -Action $action -Trigger $trigger `
    -RunLevel Highest -Force
```

## Ubuntu 側からの IP 取得

```bash
# SSM から現在の Windows IP を取得
aws ssm get-parameter --name /p001ea/windows/public_ip \
    --query Parameter.Value --output text \
    --profile AdministratorAccess-042608219431 --region ap-northeast-1
```

## 前提条件
- Windows に AWS CLI がインストールされていること
- EC2 インスタンスに SSM Parameter Store への書き込み権限がある IAM ロールがアタッチされていること
