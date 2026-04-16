# autoshutdown — EC2 自動停止

EC2 Windows を **起動後 4 時間** で自動停止する仕組み。  
Windows 内部ではなく **EC2 外部（Lambda + EventBridge）** で制御する。

## ファイル

| ファイル | 説明 |
|---|---|
| `lambda_auto_stop.py` | Lambda 関数コード（EC2起動検知 → 停止スケジュール登録） |
| `autoshutdown_set.ps1` | ※旧方式（Windows内部タスク）。緊急時の手動バックアップ用 |
| `autoshutdown_check.ps1` | ※旧方式。タスク状態確認 |

## 仕組み

```
EC2 起動
  └─► EventBridge ルール（state: running）
        └─► Lambda (lambda_auto_stop.py)
              ├─ ワンショット EventBridge ルール作成（4時間後）
              └─ 4時間後: EC2 StopInstances → ルール削除
```

## Lambda デプロイ手順

### 1. Lambda 関数作成
```bash
aws lambda create-function \
  --function-name p001ea-auto-stop \
  --runtime python3.12 \
  --handler lambda_auto_stop.lambda_handler \
  --role arn:aws:iam::042608219431:role/p001ea-lambda-role \
  --zip-file fileb://lambda_auto_stop.zip \
  --environment "Variables={INSTANCE_ID=i-040f46294faebb691,SHUTDOWN_HOURS=4,LAMBDA_ARN=<ARN>}" \
  --region ap-northeast-1 \
  --profile AdministratorAccess-042608219431
```

### 2. EventBridge ルール作成（EC2 起動検知）
```bash
aws events put-rule \
  --name "p001ea-ec2-start-detect" \
  --event-pattern '{
    "source": ["aws.ec2"],
    "detail-type": ["EC2 Instance State-change Notification"],
    "detail": {"state": ["running"], "instance-id": ["i-040f46294faebb691"]}
  }' \
  --region ap-northeast-1 \
  --profile AdministratorAccess-042608219431
```

### 3. Lambda IAM ロールに必要な権限
- `ec2:StopInstances`
- `events:PutRule` / `events:PutTargets` / `events:RemoveTargets` / `events:DeleteRule`
- `lambda:AddPermission`

## 時間を変更する場合
Lambda の環境変数 `SHUTDOWN_HOURS` を変更する。
