# 起動時 パブリックIP → SSM Parameter Store 記録スクリプト
# Windows スタートアップタスクとして登録すること（管理者権限必要）

$PARAM_IP      = "/p001ea/windows/public_ip"
$PARAM_INST    = "/p001ea/windows/instance_id"
$REGION        = "ap-northeast-1"

Write-Host "=== IP 記録スクリプト ===" -ForegroundColor Cyan

# EC2 メタデータからパブリックIPを取得
try {
    $TOKEN = (Invoke-RestMethod -Uri "http://169.254.169.254/latest/api/token" `
        -Method PUT -Headers @{"X-aws-ec2-metadata-token-ttl-seconds" = "60"})
    $PUBLIC_IP = (Invoke-RestMethod -Uri "http://169.254.169.254/latest/meta-data/public-ipv4" `
        -Headers @{"X-aws-ec2-metadata-token" = $TOKEN})
    $INSTANCE_ID = (Invoke-RestMethod -Uri "http://169.254.169.254/latest/meta-data/instance-id" `
        -Headers @{"X-aws-ec2-metadata-token" = $TOKEN})
} catch {
    Write-Host "ERROR: メタデータ取得失敗: $_" -ForegroundColor Red
    exit 1
}

Write-Host "パブリックIP    : $PUBLIC_IP"
Write-Host "インスタンスID  : $INSTANCE_ID"

# SSM Parameter Store に書き込み（aws CLI 使用）
try {
    aws ssm put-parameter --name $PARAM_IP --value $PUBLIC_IP `
        --type String --overwrite --region $REGION | Out-Null
    aws ssm put-parameter --name $PARAM_INST --value $INSTANCE_ID `
        --type String --overwrite --region $REGION | Out-Null
    Write-Host "SSM 書き込み完了" -ForegroundColor Green
} catch {
    Write-Host "ERROR: SSM 書き込み失敗: $_" -ForegroundColor Red
    exit 1
}

Write-Host "完了: $PUBLIC_IP を $PARAM_IP に記録しました"
