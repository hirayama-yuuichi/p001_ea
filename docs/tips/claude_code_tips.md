# Claude Code 便利機能まとめ

## モデル管理

### モデル確認・切り替え
```
/model              # 現在のモデル確認＆選択
/model haiku        # Haiku 4.5 に切り替え
/model sonnet       # Sonnet 4.6 に切り替え
/model opus         # Opus 4.6 に切り替え
```

### 推論深度の調整
```
/effort low         # 高速・低コスト（簡単なタスク向け）
/effort medium      # バランス型（デフォルト）
/effort high        # 深い推論（複雑な問題向け）
```

## ステータス・使用量

```
/status             # 現在のモデル・アカウント情報
/cost               # セッション内の使用統計
/stats              # 使用パターン確認（Pro/Max）
```

## タスク管理

```
TodoWrite           # この会話中のタスク追跡ツール
                    # タスク完了後、todo.md に反映させる
```

## コード検索

```
Glob                # ファイルパターン検索
                    例: Glob("**/*.py")

Grep                # ファイル内容の検索
                    例: Grep("function_name", output_mode: "content")
```

## リモート実行

```
Agent               # サブエージェント起動（並列処理向け）
Bash                # ターミナルコマンド実行
```

## ファイル操作

```
Read                # ファイル読み込み
Write               # ファイル作成（新規）
Edit                # ファイル編集（既存）
NotebookEdit        # Jupyter Notebook 編集
```

## メモリ管理

```
/memory             # 記憶の確認・管理
                    # 会話をまたいで情報を保持できる
```

## その他

```
/help               # Claude Code ヘルプ
/compact            # コンテキスト圧縮（長い会話用）
/fast               # 高速モード（最初は Opus が使われるが出力が早い）
```

## 推奨使い分け

| 作業内容 | モデル | Effort |
|---------|--------|--------|
| 環境構築・スクリプト作成 | Haiku | low / medium |
| バグ調査・複雑なロジック | Sonnet | medium / high |
| 強化学習・アーキテクチャ設計 | Opus / opusplan | high / max |
