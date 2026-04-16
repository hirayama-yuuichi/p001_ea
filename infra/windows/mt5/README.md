# mt5 — MT5 操作・管理

EC2 Windows 上の MetaTrader5 に関連するスクリプト・メモ。

## MT5 でやること

| 機能 | 説明 | 状況 |
|---|---|---|
| 価格データ取得 | MT5から価格を取得し Ubuntu へ提供 | `ml/fetch_mt5_data.py` で実装済み |
| EA 実行 | MT5 上で自動売買 EA を動かす | `mt5/` フォルダにEAスクリプト管理 |
| EA テスト | MT5 ストラテジーテスターで EA を検証 | 手動操作 |
| その他 | 今後追加予定 | - |

## Ubuntu → EC2 Windows 間のデータ連携

MT5 の価格データは SSH 経由で取得する：

```bash
# Ubuntu から EC2 の IP を SSM で取得
WIN_IP=$(aws ssm get-parameter --name /p001ea/windows/public_ip \
  --query Parameter.Value --output text \
  --profile AdministratorAccess-042608219431 --region ap-northeast-1)

# SSH 経由でデータ取得スクリプトを実行
ssh -i ~/.ssh/ec2_key.pem hy@${WIN_IP} \
  "cd p001_ea && .\.venv\Scripts\python.exe ml/fetch_mt5_data.py --year 2025"
```

## MT5 関連ファイルの場所

| ファイル | 場所 |
|---|---|
| EA スクリプト (.mq5) | `mt5/` |
| データ取得スクリプト | `ml/fetch_mt5_data.py` |
| 学習モデル | `ml/` |

## MT5 接続設定（Windows側）

MT5 は `C:\Program Files\MetaTrader 5\` にインストール。  
AutoTrading を有効にしてから EA を動かすこと。
