# p001_ea Windows セットアップスクリプト（.venv版）
# PowerShell を管理者として実行すること

Write-Host "=== p001_ea Windows セットアップ ===" -ForegroundColor Cyan

# ---- 設定 ----
$REPO_URL  = "https://github.com/hirayama-yuuichi/p001_ea.git"
$WORK_DIR  = "C:\Users\hy"
$REPO_DIR  = "$WORK_DIR\p001_ea"
$VENV_DIR  = "$REPO_DIR\.venv"
# ---------------

# ① git クローン
Write-Host "`n[1/3] リポジトリをクローン..." -ForegroundColor Yellow
if (Test-Path $REPO_DIR) {
    Write-Host "  既存フォルダあり → git pull で更新します"
    Set-Location $REPO_DIR
    git pull
} else {
    Set-Location $WORK_DIR
    Write-Host "  クローン中..."
    git clone $REPO_URL
    Set-Location $REPO_DIR
}
Write-Host "  完了: $REPO_DIR" -ForegroundColor Green

# ② Python インストール確認
Write-Host "`n[2/3] Python インストール確認..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  Python は既にインストール済みです: $pythonVersion"
} catch {
    Write-Host "  ⚠️  Python がインストールされていません"
    Write-Host "  以下を実行して Python をインストールしてください:"
    Write-Host "    choco install python -y"
    Write-Host "    その後、このスクリプトを再実行してください"
    Read-Host "Enterキーで閉じる"
    exit 1
}

# ③ .venv 作成とライブラリインストール
Write-Host "`n[3/3] .venv を作成してライブラリをインストール..." -ForegroundColor Yellow

if (Test-Path $VENV_DIR) {
    Write-Host "  .venv は既に存在します（再作成はスキップ）"
} else {
    Write-Host "  .venv を作成中..."
    python -m venv .venv
    Write-Host "  完了"
}

$PIP = ".\.venv\Scripts\pip.exe"
$PYTHON = ".\.venv\Scripts\python.exe"

Write-Host "  requirements-windows.txt からライブラリをインストール中..."
& $PIP install -r requirements-windows.txt

Write-Host "`n=== セットアップ完了 ===" -ForegroundColor Cyan
Write-Host "リポジトリ: $REPO_DIR"
Write-Host "Python環境: $VENV_DIR"
Write-Host ""
Write-Host "動作確認コマンド:"
Write-Host "  & '$PYTHON' --version"
Write-Host "  & '$PYTHON' -c `"import MetaTrader5; print('MT5 OK')`""
Write-Host ""
Write-Host "EC2からローカルで実行する場合:"
Write-Host "  ssh ... `"cd p001_ea && .\.venv\Scripts\python.exe ml/fetch_mt5_data.py --year 2025`""
Write-Host ""
Read-Host "Enterキーで閉じる"
