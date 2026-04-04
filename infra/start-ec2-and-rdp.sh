#!/bin/bash
# EC2を起動してRemminaのIPを更新し、RDP接続するスクリプト

set -e

AWS_PROFILE="AdministratorAccess-042608219431"
INSTANCE_ID="i-040f46294faebb691"
REMMINA_DIR="/home/hy/.local/share/remmina"
# ファイル名のIPは変わるので、パターンで動的に検索する
REMMINA_PATTERNS=(
    "group_rdp_ea-hy_*.remmina"
    "group_rdp_ea_*.remmina"
)

echo "=== EC2 起動 ==="
aws ec2 start-instances --instance-ids "$INSTANCE_ID" --profile "$AWS_PROFILE" --output text --query "StartingInstances[0].CurrentState.Name"

echo "EC2 が running になるまで待機中..."
aws ec2 wait instance-running --instance-ids "$INSTANCE_ID" --profile "$AWS_PROFILE"
echo "EC2 起動完了"

echo "=== パブリック IP 取得 ==="
NEW_IP=$(aws ec2 describe-instances \
    --instance-ids "$INSTANCE_ID" \
    --profile "$AWS_PROFILE" \
    --query "Reservations[0].Instances[0].PublicIpAddress" \
    --output text)

echo "新しい IP: $NEW_IP"

echo "=== Remmina プロファイル更新 ==="
UPDATED_PROFILE=""
for PATTERN in "${REMMINA_PATTERNS[@]}"; do
    PROFILE=$(ls "$REMMINA_DIR"/$PATTERN 2>/dev/null | head -1)
    [ -n "$PROFILE" ] && [ -f "$PROFILE" ] || { echo "プロファイルが見つかりません: $PATTERN"; continue; }
    OLD_IP=$(grep "^server=" "$PROFILE" | cut -d= -f2)
    if [ "$OLD_IP" = "$NEW_IP" ]; then
        echo "$(basename $PROFILE): IP は変わっていません ($NEW_IP)"
        UPDATED_PROFILE="$PROFILE"
    else
        sed -i "s/^server=.*/server=$NEW_IP/" "$PROFILE"
        OLD_IP_DASH=$(echo "$OLD_IP" | tr '.' '-')
        NEW_IP_DASH=$(echo "$NEW_IP" | tr '.' '-')
        NEW_PROFILE=$(echo "$PROFILE" | sed "s/$OLD_IP_DASH/$NEW_IP_DASH/g")
        if [ "$PROFILE" != "$NEW_PROFILE" ]; then
            mv "$PROFILE" "$NEW_PROFILE"
        fi
        echo "$(basename $PROFILE): $OLD_IP -> $NEW_IP に更新"
        UPDATED_PROFILE="$NEW_PROFILE"
    fi
done

echo "=== RDP 接続起動 ==="
remmina &
echo "Remmina を起動しました"
