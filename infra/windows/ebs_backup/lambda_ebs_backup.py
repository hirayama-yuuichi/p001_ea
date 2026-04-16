"""
Lambda: EC2 停止時 EBS スナップショット → 旧スナップショット削除 → EBS デタッチ/削除
EventBridge で「EC2 が stopping になったとき」にトリガーする。

フロー:
  1. EC2 が stopping 状態になる
  2. この Lambda が起動
  3. アタッチされた EBS ボリュームのスナップショットを作成
  4. スナップショット完了を待つ
  5. 旧スナップショット（同タグ）を削除
  6. EBS ボリュームをデタッチ → 削除

トリガー設定（EventBridge ルール）:
  イベントパターン:
    {
      "source": ["aws.ec2"],
      "detail-type": ["EC2 Instance State-change Notification"],
      "detail": {
        "state": ["stopping"],
        "instance-id": ["i-040f46294faebb691"]
      }
    }

必要な Lambda IAM 権限:
  - ec2:DescribeInstances
  - ec2:DescribeVolumes
  - ec2:CreateSnapshot
  - ec2:DescribeSnapshots
  - ec2:DeleteSnapshot
  - ec2:DetachVolume
  - ec2:DeleteVolume
"""

import boto3
import os
import time

INSTANCE_ID  = os.environ.get("INSTANCE_ID", "i-040f46294faebb691")
REGION       = os.environ.get("AWS_REGION", "ap-northeast-1")
SNAPSHOT_TAG = "p001ea-backup"
# ルートボリュームは削除しない（OS が消えると再起動できない）
SKIP_DEVICE  = "/dev/sda1"


def lambda_handler(event, context):
    instance_id = event.get("detail", {}).get("instance-id", INSTANCE_ID)
    print(f"EC2 停止検知: {instance_id}")

    ec2 = boto3.client("ec2", region_name=REGION)

    # アタッチ済みボリュームを取得
    resp = ec2.describe_instances(InstanceIds=[instance_id])
    mappings = resp["Reservations"][0]["Instances"][0].get("BlockDeviceMappings", [])

    for mapping in mappings:
        device = mapping["DeviceName"]
        vol_id = mapping["Ebs"]["VolumeId"]

        if device == SKIP_DEVICE:
            print(f"スキップ（ルートボリューム）: {device} / {vol_id}")
            continue

        print(f"スナップショット作成: {device} / {vol_id}")
        snap = ec2.create_snapshot(
            VolumeId=vol_id,
            Description=f"p001ea backup {instance_id} {device}",
            TagSpecifications=[{
                "ResourceType": "snapshot",
                "Tags": [
                    {"Key": "Name",        "Value": SNAPSHOT_TAG},
                    {"Key": "InstanceId",  "Value": instance_id},
                    {"Key": "Device",      "Value": device},
                ],
            }],
        )
        snap_id = snap["SnapshotId"]
        print(f"スナップショット ID: {snap_id}")

        # 完了まで待機（最大 10 分）
        _wait_snapshot(ec2, snap_id, timeout=600)

        # 旧スナップショット削除（同 Name/Device タグ、今回作成分以外）
        _delete_old_snapshots(ec2, instance_id, device, snap_id)

        # EBS デタッチ → 削除
        print(f"デタッチ: {vol_id}")
        ec2.detach_volume(VolumeId=vol_id)
        _wait_volume_detached(ec2, vol_id)

        print(f"削除: {vol_id}")
        ec2.delete_volume(VolumeId=vol_id)
        print(f"完了: {vol_id} → {snap_id}")

    return {"status": "done"}


def _wait_snapshot(ec2, snap_id, timeout):
    elapsed = 0
    while elapsed < timeout:
        resp = ec2.describe_snapshots(SnapshotIds=[snap_id])
        state = resp["Snapshots"][0]["State"]
        if state == "completed":
            print(f"スナップショット完了: {snap_id}")
            return
        print(f"待機中 ({state}) ... {elapsed}s")
        time.sleep(30)
        elapsed += 30
    raise TimeoutError(f"スナップショットがタイムアウト: {snap_id}")


def _wait_volume_detached(ec2, vol_id, timeout=120):
    elapsed = 0
    while elapsed < timeout:
        resp = ec2.describe_volumes(VolumeIds=[vol_id])
        state = resp["Volumes"][0]["State"]
        if state == "available":
            return
        time.sleep(10)
        elapsed += 10
    raise TimeoutError(f"デタッチがタイムアウト: {vol_id}")


def _delete_old_snapshots(ec2, instance_id, device, keep_snap_id):
    resp = ec2.describe_snapshots(
        Filters=[
            {"Name": "tag:Name",       "Values": [SNAPSHOT_TAG]},
            {"Name": "tag:InstanceId", "Values": [instance_id]},
            {"Name": "tag:Device",     "Values": [device]},
        ]
    )
    for snap in resp["Snapshots"]:
        sid = snap["SnapshotId"]
        if sid != keep_snap_id:
            print(f"旧スナップショット削除: {sid}")
            ec2.delete_snapshot(SnapshotId=sid)
