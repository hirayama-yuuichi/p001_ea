# p001_ea プロジェクト

## 目標
自動売買システムを構築し、強化学習を使った FX 5分足売買戦略で収益を得る

## 環境
- **ローカルPC**: このワークスペース（/home/hy/workspace/p001_ea）
- **EC2 Windows**: MT5 + EA 稼働環境（RDP + SSH 経由でコントロール）
- **通知**: X (Twitter) への自動投稿で売買結果を記録

## フォルダ構成
```
p001_ea/
├── CLAUDE.md              # このファイル
├── todo.md                # タスク管理
├── docs/                  # ドキュメント
│   ├── setup/            # EC2・MT5 環境構築手順
│   ├── strategy/         # 売買戦略の設計メモ
│   ├── ml/               # 強化学習・モデル関連
│   ├── results/          # バックテスト・実績記録
│   └── tips/             # Claude Code 等のツールTips
├── mt5/                  # EAスクリプト（.mq5）
├── ml/                   # 強化学習モデル・学習コード
├── data/                 # 価格データ等
├── infra/                # EC2 設定・シャットダウンスクリプト
└── 未整理の案/            # 調査メモ・参考資料
```

## 主要タスク
1. **環境構築**: EC2 Windows + MT5 + Claude Code
2. **Git管理**: GitHub に push 済み
3. **ドキュメント**: docs/ に簡素なMDファイルで記録
4. **情報発信**: X API で売買結果を自動投稿
5. **売買戦略**: 強化学習（DQN / Transformer）で実装

## 作業フロー
- 各タスク終了後、簡潔な記録を `docs/results/` に残す
- テンプレート: 「やったこと」「結果」「次のアクション」
- todo.md で進捗管理

## Claude Code 便利機能
- `/status` - 現在のモデル確認（Haiku 4.5 使用中）
- `/cost` - 使用統計確認
- `TodoWrite` - タスク追跡
- `Glob` / `Grep` - コード検索
- `/memory` - 記憶の確認・管理

## 注意
- EC2 は起動後 4時間 で自動シャットダウン
- git は GitHub に自動連携（.git-credentials で認証）
