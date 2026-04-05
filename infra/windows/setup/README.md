# Windows セットアップ

EC2 Windows に p001_ea の開発環境を一括構築するスクリプト。

## やること（自動）
1. GitHub からリポジトリをクローン（既存なら git pull）
2. Miniconda をインストール
3. Python 3.11 仮想環境 `fx59v2` を作成
4. 以下のライブラリをインストール

| カテゴリ | ライブラリ |
|---|---|
| MT5連携 | MetaTrader5, pandas, numpy, pyarrow, python-dotenv |
| 強化学習 | gymnasium, stable-baselines3, gym-anytrading, gym-mtsim |
| その他 | matplotlib, scikit-learn, ta |

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
```powershell
C:\ProgramData\miniconda3\envs\fx59v2\python.exe -c "import MetaTrader5; print('MT5 OK')"
C:\ProgramData\miniconda3\envs\fx59v2\python.exe -c "import stable_baselines3; print('SB3 OK')"
```
