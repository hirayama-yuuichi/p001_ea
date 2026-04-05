# 仕様: データ取得ワークフロー（ローカル → EC2 SSH 実行）

## 概要
ローカルPC（Linux）から SSH で EC2 Windows を制御し、MT5 データを取得。
データは EC2 に保存、ローカルで必要に応じて読込。

## アーキテクチャ

```
ローカルPC (Linux)
  ↓ SSH コマンド実行
EC2 Windows
  ├─ MT5（起動状態）
  ├─ Python + MetaTrader5
  └─ ml/fetch_mt5_data.py 実行
       ↓ Parquet 保存
  data/raw/XAUUSD_M*.parquet
  data/raw/DXY_M5_*.parquet
```

## ワークフロー

### 1. ローカルからデータ取得実行

```bash
# ローカル PC（Linux）から実行
ssh -i ~/.ssh/ec2_key.pem hy@[EC2_PUBLIC_IP] \
  "cd p001_ea && python ml/fetch_mt5_data.py"
```

**実行内容（EC2 側）:**
- MT5 接続
- XAUUSD / DXY データ取得（M1, M5, M15, M60）
- Parquet 保存
- ログ出力

**実行時間:**
- 初回（5年）: 5〜10分
- 更新（1年）: 1〜2分

---

### 2. ローカルでデータを読込

**方法A: SCP で転送（推奨）**
```bash
# EC2 から取得
scp -i ~/.ssh/ec2_key.pem -r hy@[EC2_PUBLIC_IP]:~/p001_ea/data/raw/*.parquet ./data/raw/

# ローカルで読込
import pandas as pd

def load_xauusd_m5():
    df = pd.read_parquet("data/raw/XAUUSD_M5_*.parquet")
    return df.sort_index()
```

**方法B: SSH 経由で直接読込（Linux のみ、複雑）**
```python
# paramiko で SSH 接続 → リモートファイル読込
# 実装: 後で検討
```

---

## EC2 側の前提

### 必要な状態
- [ ] Windows にログイン済み（hy ユーザー）
- [ ] MT5 起動状態
- [ ] Python 仮想環境有効（`fx59v2`）
- [ ] SSH サーバー起動（標準で起動）

### 確認コマンド（ローカルから）
```bash
# 接続確認
ssh -i ~/.ssh/ec2_key.pem hy@[EC2_PUBLIC_IP] "echo OK"

# Python 確認
ssh -i ~/.ssh/ec2_key.pem hy@[EC2_PUBLIC_IP] \
  "python -c 'import MetaTrader5; print(\"OK\")'"
```

---

## ローカル側の前提

### SSH キー設定
```bash
# キーのパーミッション（600 必須）
chmod 600 ~/.ssh/ec2_key.pem

# config ファイルで簡略化（オプション）
# ~/.ssh/config に以下を追加
Host ec2-xauusd
    HostName [EC2_PUBLIC_IP]
    User hy
    IdentityFile ~/.ssh/ec2_key.pem
    StrictHostKeyChecking no

# その後
ssh ec2-xauusd "cd p001_ea && python ml/fetch_mt5_data.py"
```

### 必要なライブラリ
```bash
pip install pandas pyarrow paramiko  # paramiko は方法B用
```

---

## スクリプト例（ローカルの自動化）

### fetch_data.sh（ローカルで実行）
```bash
#!/bin/bash
EC2_HOST="hy@[EC2_PUBLIC_IP]"
EC2_KEY="~/.ssh/ec2_key.pem"
LOCAL_DATA_DIR="./data/raw"

echo "=== EC2 からデータ取得開始 ==="

# EC2 で取得実行
echo "EC2 で fetch_mt5_data.py 実行中..."
ssh -i $EC2_KEY $EC2_HOST "cd p001_ea && python ml/fetch_mt5_data.py"

# SCP で転送
echo "Parquet ファイルを転送中..."
scp -i $EC2_KEY -r $EC2_HOST:~/p001_ea/data/raw/*.parquet $LOCAL_DATA_DIR/

echo "=== 完了 ==="
```

実行：
```bash
bash infra/fetch_data.sh
```

---

## トラブルシューティング

| エラー | 原因 | 対応 |
|---|---|---|
| `Permission denied` | SSH キーの権限 | `chmod 600 ec2_key.pem` |
| `Connection refused` | EC2 SSH 未起動 | EC2 再起動 |
| `MT5 initialization failed` | MT5 未起動 | EC2 にログイン、MT5 起動 |
| `Data not found` | fetch 失敗 | `ssh ... "tail -100 nohup.out"` でログ確認 |

---

## 注意

- **EC2 の IP は起動のたびに変わる**可能性あり（Elastic IP 未設定）
  - EC2 コンソールで現在の IP を確認
- **MT5 は自動起動していない** → 手動で起動か自動起動設定が必要
- **4時間自動シャットダウン** → 長時間実行は注意
- **SSH はテキスト通信** → Parquet バイナリは SCP で転送推奨
