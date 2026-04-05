# p001_ea Windows セットアップスクリプト
# PowerShell を管理者として実行すること

Write-Host "=== p001_ea Windows セットアップ ===" -ForegroundColor Cyan

# ---- 設定 ----
$REPO_URL  = "https://github.com/hirayama-yuuichi/p001_ea.git"
$WORK_DIR  = "C:\Users\hy"
$REPO_DIR  = "$WORK_DIR\p001_ea"
$CONDA_URL = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
$CONDA_EXE = "$WORK_DIR\miniconda_installer.exe"
$CONDA_DIR = "C:\ProgramData\miniconda3"
$ENV_NAME  = "fx59v2"
$PYTHON_VER = "3.11"
# --------------

# ① git クローン
Write-Host "`n[1/4] リポジトリをクローン..." -ForegroundColor Yellow
if (Test-Path $REPO_DIR) {
    Write-Host "  既存フォルダあり → git pull で更新します"
    Set-Location $REPO_DIR
    git pull
} else {
    Set-Location $WORK_DIR
    git clone $REPO_URL
    Set-Location $REPO_DIR
}
Write-Host "  完了: $REPO_DIR" -ForegroundColor Green

# ② Miniconda インストール
Write-Host "`n[2/4] Miniconda をインストール..." -ForegroundColor Yellow
if (Test-Path "$CONDA_DIR\Scripts\conda.exe") {
    Write-Host "  Miniconda は既にインストール済みです"
} else {
    Write-Host "  ダウンロード中..."
    Invoke-WebRequest -Uri $CONDA_URL -OutFile $CONDA_EXE
    Write-Host "  インストール中（数分かかります）..."
    Start-Process -FilePath $CONDA_EXE -ArgumentList "/S /D=$CONDA_DIR" -Wait
    Remove-Item $CONDA_EXE
    Write-Host "  完了" -ForegroundColor Green
}

# conda コマンドをこのセッションで使えるように
$env:Path = "$CONDA_DIR\Scripts;" + $env:Path

# ③ 仮想環境作成 + 基本ライブラリ
Write-Host "`n[3/4] Python仮想環境 ($ENV_NAME) を作成..." -ForegroundColor Yellow
$envExists = & "$CONDA_DIR\Scripts\conda.exe" env list | Select-String $ENV_NAME
if ($envExists) {
    Write-Host "  環境 $ENV_NAME は既に存在します"
} else {
    & "$CONDA_DIR\Scripts\conda.exe" create -n $ENV_NAME python=$PYTHON_VER -y
    Write-Host "  完了" -ForegroundColor Green
}

# pip インストール先を仮想環境に向ける
$PIP = "$CONDA_DIR\envs\$ENV_NAME\Scripts\pip.exe"
$PYTHON = "$CONDA_DIR\envs\$ENV_NAME\python.exe"

Write-Host "`n[4/4] ライブラリをインストール..." -ForegroundColor Yellow

# MT5連携用
Write-Host "  MT5連携ライブラリ..."
& $PIP install MetaTrader5 pandas numpy pyarrow python-dotenv

# 強化学習用
Write-Host "  強化学習ライブラリ..."
& $PIP install gymnasium stable-baselines3 gym-anytrading gym-mtsim

# その他
Write-Host "  その他..."
& $PIP install matplotlib scikit-learn ta

Write-Host "`n=== セットアップ完了 ===" -ForegroundColor Cyan
Write-Host "リポジトリ: $REPO_DIR"
Write-Host "Python環境: $ENV_NAME"
Write-Host ""
Write-Host "動作確認:"
Write-Host "  & '$PYTHON' -c `"import MetaTrader5; print('MT5 OK')`""
Write-Host "  & '$PYTHON' -c `"import stable_baselines3; print('SB3 OK')`""
Write-Host ""
Read-Host "Enterキーで閉じる"
