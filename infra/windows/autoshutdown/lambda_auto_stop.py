"""
Lambda: EC2 Windows 自動停止
EventBridge で「EC2 が running になったとき」にトリガーし、
4時間後に停止する EventBridge ワンショットルールを作成する。

トリガー設定（EventBridge ルール）:
  イベントパターン:
    {
      "source": ["aws.ec2"],
      "detail-type": ["EC2 Instance State-change Notification"],
      "detail": {
        "state": ["running"],
        "instance-id": ["i-040f46294faebb691"]
      }
    }

必要な Lambda IAM 権限:
  - ec2:StopInstances
  - events:PutRule
  - events:PutTargets
  - lambda:AddPermission
"""

import json
import boto3
import os
from datetime import datetime, timezone, timedelta

INSTANCE_ID = os.environ.get("INSTANCE_ID", "i-040f46294faebb691")
HOURS       = int(os.environ.get("SHUTDOWN_HOURS", "4"))
REGION      = os.environ.get("AWS_REGION", "ap-northeast-1")
LAMBDA_ARN  = os.environ.get("LAMBDA_ARN", "")  # この Lambda 自身の ARN


def lambda_handler(event, context):
    instance_id = event.get("detail", {}).get("instance-id", INSTANCE_ID)
    print(f"EC2 起動検知: {instance_id}")

    stop_at = datetime.now(timezone.utc) + timedelta(hours=HOURS)
    # EventBridge cron は分単位なので秒を切り捨て
    cron_expr = f"cron({stop_at.minute} {stop_at.hour} {stop_at.day} {stop_at.month} ? {stop_at.year})"
    rule_name = f"AutoStop-{instance_id}"

    events = boto3.client("events", region_name=REGION)

    # ワンショットルールを作成
    events.put_rule(
        Name=rule_name,
        ScheduleExpression=cron_expr,
        State="ENABLED",
        Description=f"{instance_id} を {stop_at.isoformat()} に停止",
    )

    # このLambda自身をターゲットに（停止実行用）
    events.put_targets(
        Rule=rule_name,
        Targets=[{
            "Id": "stop-target",
            "Arn": LAMBDA_ARN,
            "Input": json.dumps({
                "action": "stop",
                "instance_id": instance_id,
                "rule_name": rule_name,
            }),
        }],
    )

    print(f"停止スケジュール登録完了: {stop_at.isoformat()} ({cron_expr})")
    return {"status": "scheduled", "stop_at": stop_at.isoformat()}


def stop_instance(event, context):
    """ワンショットルールから呼ばれる停止処理"""
    instance_id = event["instance_id"]
    rule_name   = event["rule_name"]

    ec2 = boto3.client("ec2", region_name=REGION)
    ec2.stop_instances(InstanceIds=[instance_id])
    print(f"停止命令送信: {instance_id}")

    # ワンショットルールを削除
    events = boto3.client("events", region_name=REGION)
    events.remove_targets(Rule=rule_name, Ids=["stop-target"])
    events.delete_rule(Name=rule_name)
    print(f"ルール削除: {rule_name}")

    return {"status": "stopped", "instance_id": instance_id}
