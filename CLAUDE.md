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

## 自動ワークフロー（Claude が自動で行うこと）

> ここを編集すれば Claude の自動行動を変更できる

### 作業依頼時（自動記録）
1. **TodoWrite でタスクを記録** — 依頼内容をTODOに追加してから作業開始
   - 複数ステップがある場合はサブタスクに分解して登録
   - 完了したタスクは随時 completed に更新

### 作業開始前（自動チェック）
1. `git pull` — 常に最新に同期
2. **AWS SSO 確認**（EC2/AWS 関連作業のとき）
   - `aws sts get-caller-identity --profile AdministratorAccess-042608219431` で確認
   - 切れていたらユーザーに通知（`aws sso login` はブラウザが必要なため自動実行しない）
3. **EC2 状態確認**（EC2 関連作業のとき）
   - インスタンス ID: `i-040f46294faebb691`
   - 起動中か・現在の IP を確認
   - 4時間自動シャットダウンに注意

### 作業完了後（自動実行）
1. `git add` → `git commit`（日本語メッセージ）→ `git push`
2. `docs/results/YYYY-MM-DD_タスク名.md` に作業記録を作成
   - テンプレート: 「やったこと」「結果」「次のアクション」
   - ドキュメントもコミットに含める

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
