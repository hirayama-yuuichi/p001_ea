# 作業記録: FX強化学習戦略リサーチ

日付: 2026-04-05

## やったこと
- FX自動売買（5分足）の強化学習戦略について、WebSearch 5回・WebFetch 2回でリサーチ
- DQN・Transformer・PPO・A3Cの実績、決済手法、MT5連携、ライブラリ比較をまとめた
- `docs/strategy/rl_fx_5min_research.md` に詳細ドキュメントを作成

## 結果
- **アルゴ**: PPOがSB3で最も実装しやすく、DQNはFXで実績あり。Transformerは特徴量抽出に有効
- **決済**: まず固定時間（5分後）からスタート、ATRベースTP/SL付き3アクションに移行が定石
- **手数料問題**: 手数料なし環境で成功したモデルが手数料込みで収益マイナスになる例が多数 → 最初から組み込む
- **MT5連携**: gym-mtsim（Windows必須）がRL+MT5の最短経路

## 次のアクション
- `gym-anytrading + SB3(PPO)` でプロトタイプ実装開始
- EURUSDの5分足CSVデータ収集（MT5から取得）
- 報酬関数設計（Sharpe比ベース + スプレッドペナルティ）
