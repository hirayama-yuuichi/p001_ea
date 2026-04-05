# Windows セットアップ（.venv版）

EC2 Windows に p001_ea の開発環境を一括構築するスクリプト。

## やること（自動）
1. GitHub からリポジトリをクローン（既存なら git pull）
2. Python がインストール済みか確認
3. p001_ea ディレクトリに `.venv` を作成
4. requirements-windows.txt からライブラリをインストール

## インストール内容

| カテゴリ | ライブラリ |
|---|---|
| データ処理 | pandas, numpy, pyarrow |
| MT5連携 | MetaTrader5 |
| ユーティリティ | python-dotenv |

**注**: ML（gymnasium, stable-baselines3など）は必要に応じて後で追加

## 前提条件

- Windows PowerShell が実行できること（管理者権限推奨）
- Python 3.10+ が**システムパス**に入っていること
  - CloudFormation UserData で自動インストール済み
  - 確認: `python --version`

## 実行手順

### 初回（gitクローン前）
PowerShell を**管理者として実行**し、以下を貼り付けて実行：

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/hirayama-yuuichi/p001_ea/main/infra/windows/setup/setup.ps1" -OutFile "$env:TEMP\setup.ps1"
& "$env:TEMP\setup.ps1"
```

### クローン済みの場合
```powershell
cd C:\Users\hy\p001_ea
.\infra\windows\setup\setup.ps1
```

## 動作確認

セットアップ完了後、PowerShell で以下を実行：

```powershell
cd C:\Users\hy\p001_ea

# Python バージョン確認
.\.venv\Scripts\python.exe --version

# MetaTrader5 ライブラリ確認
.\.venv\Scripts\python.exe -c "import MetaTrader5; print('MT5 OK')"
```

## ローカル PC からのデータ取得実行

Linux ローカル PC から SSH 経由でスクリプトを実行：

```bash
# EC2 から当年のデータを取得
ssh -i ~/.ssh/ec2_key.pem hy@[EC2_PUBLIC_IP] \
  "cd p001_ea && .\.venv\Scripts\python.exe ml/fetch_mt5_data.py"

# または指定年を取得
ssh -i ~/.ssh/ec2_key.pem hy@[EC2_PUBLIC_IP] \
  "cd p001_ea && .\.venv\Scripts\python.exe ml/fetch_mt5_data.py --year 2025"
```

## トラブルシューティング

| 症状 | 原因 | 対応 |
|---|---|---|
| `python: コマンドが見つかりません` | Python がインストール未済 | `choco install python -y` してから再実行 |
| `.venv\Scripts\python.exe` が見つからない | .venv 作成失敗 | `python -m venv .venv` を手動実行 |
| `ModuleNotFoundError: MetaTrader5` | ライブラリ未インストール | `.\.venv\Scripts\pip.exe install -r requirements-windows.txt` |
