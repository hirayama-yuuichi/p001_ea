# infra/windows フォルダ ルール

## 目的
EC2 Windows 上で MT5 を動かすためのインフラ管理。

## フォルダ構成
```
infra/windows/
├── claude.md          # このファイル（フォルダ専用ルール）
├── setup/             # EC2 Windows 初回セットアップ
├── startup/           # 起動時スクリプト（IP記録など）
├── autoshutdown/      # 自動停止（EC2外部 = Lambda + EventBridge）
├── ebs_backup/        # シャットダウン時 EBS → S3 退避
└── mt5/               # MT5 操作・管理
```

## 設計方針
- **シャットダウンは EC2 外部（Lambda）で行う** — Windows 内部のタスクスケジューラは使わない
- **EBSはコスト削減のため停止時に S3 退避 → 削除** — 起動時にスナップショットから復元
- **固定IP不使用** — 起動時に SSM Parameter Store へパブリックIPを記録
- **Ubuntu からは SSM 経由で IP を取得** して MT5 に接続

## SSM パラメータ名
| パラメータ | 内容 |
|---|---|
| `/p001ea/windows/public_ip` | 現在のパブリックIP |
| `/p001ea/windows/instance_id` | インスタンスID |

## EC2 インスタンス情報
- インスタンスID: `i-040f46294faebb691`
- 自動停止: 起動後 **4時間**（Lambda で管理）
- テスト運用期間中は 4 時間制限を維持

## このフォルダを変更するときのルール
- Lambda コードを変更したら **手動でデプロイが必要**（コード変更だけでは反映されない）
- PowerShell スクリプトを変更したら Windows 側にも反映すること
- EBS スナップショット戦略を変更する場合は `ebs_backup/README.md` を先に更新
