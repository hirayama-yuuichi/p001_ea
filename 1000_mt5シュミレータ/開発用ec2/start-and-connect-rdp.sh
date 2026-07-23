#!/usr/bin/env bash
#
# 開発用EC2(Windows/mt5)が停止していたら起動し、パブリックIPを取得して
# リモートデスクトップ(remmina)で接続する。
#
# 使い方:
#   ./start-and-connect-rdp.sh
#
# 前提:
#   - aws sso login 済み、または本スクリプトが自動で aws sso login を実行できること
#   - remmina がインストールされていること
#
set -euo pipefail

PROFILE="AdministratorAccess-042608219431"
REGION="ap-northeast-1"
INSTANCE_ID="i-06f228c7623eba3a7"

# 起動待ち・IP取得待ちのタイムアウト（秒）
WAIT_TIMEOUT=180
WAIT_INTERVAL=5

aws_cli() {
  aws "$@" --profile "$PROFILE" --region "$REGION"
}

echo "[1/4] AWS SSO ログイン状態を確認しています..."
if ! aws_cli sts get-caller-identity >/dev/null 2>&1; then
  echo "SSO セッションが無効なため、ログインします。"
  aws sso login --profile "$PROFILE"
fi

echo "[2/4] インスタンス状態を確認しています... (${INSTANCE_ID})"
STATE=$(aws_cli ec2 describe-instances \
  --instance-ids "$INSTANCE_ID" \
  --query 'Reservations[0].Instances[0].State.Name' \
  --output text)
echo "現在の状態: ${STATE}"

case "$STATE" in
  running)
    echo "既に起動しています。"
    ;;
  stopped)
    echo "停止中のため起動します。"
    aws_cli ec2 start-instances --instance-ids "$INSTANCE_ID" >/dev/null
    ;;
  stopping | pending | shutting-down)
    echo "状態が ${STATE} のため、running になるまで待機します。"
    ;;
  *)
    echo "予期しない状態です: ${STATE}" >&2
    exit 1
    ;;
esac

if [ "$STATE" != "running" ]; then
  echo "起動完了を待機しています..."
  aws_cli ec2 wait instance-running --instance-ids "$INSTANCE_ID"
  echo "起動しました。"
fi

echo "[3/4] パブリックIPアドレスを取得しています..."
ELAPSED=0
PUBLIC_IP=""
while [ "$ELAPSED" -lt "$WAIT_TIMEOUT" ]; do
  PUBLIC_IP=$(aws_cli ec2 describe-instances \
    --instance-ids "$INSTANCE_ID" \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)
  if [ -n "$PUBLIC_IP" ] && [ "$PUBLIC_IP" != "None" ]; then
    break
  fi
  sleep "$WAIT_INTERVAL"
  ELAPSED=$((ELAPSED + WAIT_INTERVAL))
  PUBLIC_IP=""
done

if [ -z "$PUBLIC_IP" ]; then
  echo "パブリックIPの取得に失敗しました（タイムアウト）。" >&2
  exit 1
fi

echo "パブリックIP: ${PUBLIC_IP}"

echo "[4/4] リモートデスクトップで接続します..."
if command -v remmina >/dev/null 2>&1; then
  remmina -c "rdp://${PUBLIC_IP}" &
else
  echo "remmina が見つかりません。以下のIPへ手動でRDP接続してください: ${PUBLIC_IP}" >&2
  exit 1
fi
