# infra/windows — EC2 Windows (MT5) インフラ管理

## このフォルダの目的

EC2 Windows 上で MetaTrader5 を動かすための **インフラ一式を管理** する。  
Ubuntu（ローカルPC）から EC2 Windows を制御し、MT5 による自動売買を実現する。

---

## あるべき姿（仕様整理）

### 全体構成図

```
Ubuntu (ローカル PC)
  │
  ├─► connect/start_and_rdp.sh   EC2起動 → IP取得 → RDP接続
  │
  ├─► SSM Parameter Store        /p001ea/windows/public_ip を読む
  │       ↑
  │   startup/record_ip.ps1      Windows起動時に書き込む
  │
  └─► SSH / MT5接続              SSMから取得したIPで接続

EC2 Windows (MT5)
  │
  ├─ setup/setup.ps1             初回セットアップ（git clone + .venv）
  ├─ startup/record_ip.ps1       起動時: パブリックIP → SSM
  ├─ mt5/                        EA実行・価格データ取得
  │
  └─ 停止イベント (stopping)
       └─► Lambda: ebs_backup    EBSスナップショット → EBS削除

Lambda (AWS)
  ├─ autoshutdown/lambda_auto_stop.py   起動後4時間でEC2停止
  ├─ ebs_backup/lambda_ebs_backup.py    停止時EBS退避
  └─ startup/lambda_restore_ebs.py      起動時EBS復元 ← ★未実装
```

---

## 機能一覧と実装状況

### ✅ 実装済み

| 機能 | 場所 | 説明 |
|---|---|---|
| EC2 Windows セットアップ | `setup/setup.ps1` | Gitクローン + .venv + requirements |
| 自動停止（EC2外部） | `autoshutdown/lambda_auto_stop.py` | 起動後4時間でLambdaがEC2停止 |
| EBSスナップショット退避 | `ebs_backup/lambda_ebs_backup.py` | 停止時にスナップショット→EBS削除 |
| 起動時IP記録 | `startup/record_ip.ps1` | パブリックIP→SSM Parameter Store |
| EC2起動＋RDP接続 | `../start-ec2-and-rdp.sh` | Ubuntu側: EC2起動→Remmina自動更新 |
| CloudFormation | `../ec2-windows-mt5.yaml` | EC2・SG・IAM・UserData定義 |

> `autoshutdown/lambda_auto_stop.py` などは**コードのみ。AWSへのデプロイが別途必要。**

---

### ❌ 未実装（追加が必要）

| 機能 | 優先度 | 説明 |
|---|---|---|
| **EBS復元 Lambda** | 🔴 高 | 起動時にスナップショットからEBSを再作成→アタッチ。EBS削除と対になる必須機能 |
| **Ubuntu側IP取得スクリプト** | 🟡 中 | SSM→IP取得→SSH/MT5接続を1コマンドで行うwrapper |
| **Lambda IAMロール（CFn）** | 🔴 高 | Lambda用権限をCloudFormationで管理（現状未定義） |
| **EC2起動スクリプトの移動** | 🟢 低 | `../start-ec2-and-rdp.sh` を `connect/` に移動して整理 |
| **CFnテンプレートの移動** | 🟢 低 | `../ec2-windows-mt5.yaml` を `cfn/` に移動して整理 |
| **MT5起動確認スクリプト** | 🟡 中 | SSH経由でMT5プロセスが起動しているか確認 |
| **Lambda デプロイスクリプト** | 🟡 中 | `deploy.sh` で3つのLambdaを一括デプロイ |

---

## フォルダ構成（あるべき姿）

```
infra/windows/
├── README.md                        # ← このファイル
├── claude.md                        # フォルダ専用ルール
│
├── cfn/                             # CloudFormation テンプレート
│   ├── ec2-windows-mt5.yaml         # EC2・SG・IAM（現: ../ec2-windows-mt5.yaml）
│   └── lambda-roles.yaml            # Lambda用IAMロール ← ★未実装
│
├── setup/                           # EC2 Windows 初回セットアップ
│   ├── README.md
│   └── setup.ps1
│
├── connect/                         # Ubuntu → Windows 接続
│   ├── README.md
│   └── start_and_rdp.sh             # EC2起動+RDP（現: ../start-ec2-and-rdp.sh）
│
├── startup/                         # 起動時処理（Windows / Lambda）
│   ├── README.md
│   ├── record_ip.ps1                # Windows起動時: IP → SSM
│   └── lambda_restore_ebs.py        # Lambda: スナップショット→EBS復元 ← ★未実装
│
├── autoshutdown/                    # EC2外部からの自動停止
│   ├── README.md
│   ├── lambda_auto_stop.py          # Lambda本体
│   ├── autoshutdown_set.ps1         # 旧方式（緊急時バックアップ）
│   └── autoshutdown_check.ps1       # 旧方式（タスク確認）
│
├── ebs_backup/                      # 停止時EBS退避
│   ├── README.md
│   └── lambda_ebs_backup.py
│
└── mt5/                             # MT5操作・管理
    └── README.md
```

---

## 現状のフォルダとの差分（work.txt 要件 + 既存機能の洗い出し）

### work.txt 要件にはなかった既存機能
| 機能 | 場所 | 対応 |
|---|---|---|
| EC2起動＋Remmina自動更新 | `../start-ec2-and-rdp.sh` | → `connect/` に移動予定 |
| CloudFormation テンプレート | `../ec2-windows-mt5.yaml` | → `cfn/` に移動予定 |
| Windows内部タスクスケジューラ停止 | `autoshutdown/*.ps1` | 旧方式として残す（緊急時バックアップ） |

### work.txt 要件から新たに判明した不足機能
- **EBS復元が未実装** → EBS削除するなら復元もセットで必要
- **Lambda デプロイ手順が散在** → `deploy.sh` で一元化すべき
- **MT5プロセス監視が未実装** → EA稼働確認ができない

---

## 優先実装順

1. `startup/lambda_restore_ebs.py` — EBS削除と対になる必須機能
2. `cfn/lambda-roles.yaml` — Lambda権限のインフラ化
3. `deploy.sh` — Lambda一括デプロイ
4. `connect/` への整理移動
