# AutoShutdown スクリプト

EC2 Windows の自動シャットダウンタスクを管理する PowerShell スクリプト。

## ファイル

| ファイル | 説明 |
|---|---|
| `autoshutdown_set.ps1` | タスクを登録する（何時間後か設定可） |
| `autoshutdown_check.ps1` | タスクの状態を確認する |

## 使い方

### デスクトップへのコピー
このフォルダのファイルを Windows デスクトップにコピーして使う。

### 実行方法
PowerShell を **管理者として実行** し、以下を実行：

```powershell
# 設定（4時間後にシャットダウン）
.\autoshutdown_set.ps1

# 確認
.\autoshutdown_check.ps1
```

または `.ps1` ファイルを右クリック → **PowerShell で実行**。

### 時間を変更したい場合
`autoshutdown_set.ps1` の以下の行を編集：

```powershell
$HOURS = 4   # ← ここを変える
```

## 注意
- EC2 を再起動するとタスクは消えるため、再起動後は `autoshutdown_set.ps1` を再実行すること
- タスク起動から実際のシャットダウンまで **さらに60秒** かかる（`/t 60` の設定）
- 管理元: `p001_ea/infra/windows/autoshutdown/`（GitHub で管理）
