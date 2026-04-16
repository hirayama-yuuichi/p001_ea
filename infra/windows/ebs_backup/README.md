# ebs_backup — EBS S3退避（シャットダウン時）

EC2 Windows 停止時に **データ用EBSをスナップショット保存 → EBS削除** してコストを削減する。  
次回起動時はスナップショットから EBS を再作成してアタッチする。

## ファイル

| ファイル | 説明 |
|---|---|
| `lambda_ebs_backup.py` | Lambda 関数コード（EBSスナップショット → 削除） |

## 仕組み

```
EC2 停止開始 (stopping)
  └─► EventBridge ルール
        └─► Lambda (lambda_ebs_backup.py)
              ├─ データ用EBSのスナップショット作成
              ├─ スナップショット完了を待機
              ├─ 旧スナップショットを削除（直近1世代のみ保持）
              └─ EBS デタッチ → 削除
```

> ルートボリューム（/dev/sda1）は削除しない。データ用EBS（/dev/sdb など）のみ対象。

## コスト削減効果

| 状態 | コスト |
|---|---|
| EBS gp3 30GB 稼働中 | 約 $2.4/月 |
| スナップショット 30GB のみ | 約 $1.5/月（変更分のみ課金） |

## Lambda デプロイ手順

```bash
aws lambda create-function \
  --function-name p001ea-ebs-backup \
  --runtime python3.12 \
  --handler lambda_ebs_backup.lambda_handler \
  --role arn:aws:iam::042608219431:role/p001ea-lambda-role \
  --zip-file fileb://lambda_ebs_backup.zip \
  --timeout 900 \
  --environment "Variables={INSTANCE_ID=i-040f46294faebb691}" \
  --region ap-northeast-1 \
  --profile AdministratorAccess-042608219431
```

## EventBridge トリガー

```bash
aws events put-rule \
  --name "p001ea-ec2-stop-detect" \
  --event-pattern '{
    "source": ["aws.ec2"],
    "detail-type": ["EC2 Instance State-change Notification"],
    "detail": {"state": ["stopping"], "instance-id": ["i-040f46294faebb691"]}
  }' \
  --region ap-northeast-1 \
  --profile AdministratorAccess-042608219431
```

## 次回起動時の EBS 復元（手動 or Lambda で自動化）

```bash
# スナップショットから EBS を作成
aws ec2 create-volume \
  --snapshot-id <snap-id> \
  --availability-zone ap-northeast-1a \
  --volume-type gp3 \
  --region ap-northeast-1

# EC2 にアタッチ
aws ec2 attach-volume \
  --volume-id <vol-id> \
  --instance-id i-040f46294faebb691 \
  --device /dev/sdb \
  --region ap-northeast-1
```

## 注意
- Lambda タイムアウトは **15分** に設定すること（スナップショット完了待ちのため）
- ルートボリューム削除は不可（SKIP_DEVICE = `/dev/sda1`）
