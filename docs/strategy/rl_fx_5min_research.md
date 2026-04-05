# FX自動売買（5分足）強化学習戦略 リサーチまとめ

作成日: 2026-04-05

---

## 1. 戦略の選択肢

### DQN + マルチタイムフレーム

**結論**: DQNは研究実績が最も豊富だが、手数料ありの環境では単純なbuy-and-hold収束に陥りやすい。マルチペア・補助タスクとの組み合わせで改善傾向あり。

- 2025年のScientific Reports論文: LSTM + DQNハイブリッドで為替予測精度を向上。DQNが「マクロショックへの適応」を担う構造
- Ensemble DQN研究（ACM 2022）: 複数DQNエージェントのアンサンブルが単体より安定
- 実証的課題: DQNとA2Cはシンプルな一方向保有戦略に収束しやすい（高頻度売買を避ける）
- マルチタイムフレーム活用には、複数時間軸のOHLCを特徴量として入力するのが一般的

**情報源**:
- [Deep neural network + DQN for exchange rates (Scientific Reports 2025)](https://www.nature.com/articles/s41598-025-12516-3)
- [Optimized Forex Trading using Ensemble of Deep Q-Learning Agents (ACM 2022)](https://dl.acm.org/doi/10.1145/3549206.3549280)
- [Improving DRL Agent Trading Performance using Auxiliary Task (ResearchGate 2024)](https://www.researchgate.net/publication/385529053_Improving_Deep_Reinforcement_Learning_Agent_Trading_Performance_in_Forex_using_Auxiliary_Task)
- [Deep RL for Foreign Exchange Trading (arXiv 2019)](https://arxiv.org/abs/1908.08036)

### Transformer / Attention系

**結論**: TransformerベースのRLはFX予測で有望。EncoderのAttentionで時系列の重要区間を抽出し、naive戦略を上回る実績あり。ただし5分足への直接適用例は少なく、1分足データを集約する形が多い。

- SpringerLink 2024論文: EURUSD・GBPUSDでTransformer-based RLを実装。Encoder部分のAttentionで時系列トレンドを学習。TP/SLレベルを変化させてもnaive戦略より高い成功率を達成
- Spatial-temporal Graph Attention（OpenReview）: 複数通貨ペアの相関をグラフ構造で捉えるアプローチ
- ACM AI in Finance 2024サーベイ: Transformer/Attentionネットワークの定量的取引への応用を網羅的に調査

**情報源**:
- [Transformer-Based Reinforcement Learning for Forex Trading (Springer 2024)](https://link.springer.com/chapter/10.1007/978-981-97-3526-6_14)
- [Transformers and attention-based networks in quantitative trading: comprehensive survey (ACM 2024)](https://dl.acm.org/doi/10.1145/3677052.3698684)
- [Spatial-temporal Graph Attention Network for Forex Forecasting (OpenReview)](https://openreview.net/forum?id=5x9kfRXhBd)

### PPO（Proximal Policy Optimization）その他

**結論**: PPOは連続行動空間や複雑な報酬設計に向くが、FXでは高頻度売買に陥って損失を増やす報告もある。A3C（マルチエージェント非同期）はペア別専門エージェントとして有力。

- PPOはStable-Baselines3で最も実装しやすく、ハイパーパラメータ探索も容易
- A3C多エージェント研究（arXiv 2024）: 9通貨ペアで月次2.22%リターン、最大DD 10.39%
- DQN vs PPO比較: 下降トレンドではDQNが優位との報告あり

**情報源**:
- [Multi-Agent A3C Deep RL for Forex (arXiv 2024)](https://arxiv.org/abs/2405.19982)
- [Reinforcement Learning Framework for Quantitative Trading (arXiv 2024)](https://arxiv.org/html/2411.07585v1)
- [PPO Stable-Baselines3 ドキュメント](https://stable-baselines3.readthedocs.io/en/master/modules/ppo.html)

---

## 2. 決済手法の選択肢

### 固定時間決済（5分後クローズ）

**結論**: 実装が単純でバックテストしやすいが、トレンド継続時に利益を切り捨てる問題がある。スプレッドコストが直撃するため、エントリー精度が特に重要。

- 5分足1本で決済 = 保有コスト最小化・結果のばらつき小
- 「手数料0で検証 → 手数料ありで再検証」の2段階テストが必須（手数料導入で多くのエージェントが収益マイナスに転落する報告が複数）
- シンプルな離散行動（Buy/Sell/Hold）と相性が良い

### TP/SL設定の典型値（5分足FX）

**結論**: 論文では固定pips設定よりATRベースの動的TP/SLが主流。5分足EURUSDの場合、TP=5〜15pips・SL=5〜10pipsの範囲が多い。リスクリワード比1:1〜1:2が一般的。

- ATR(14)の0.5〜1.5倍をTP/SLに使うアダプティブ設定が安定しやすい
- Transformer論文では複数TP/SLレベルでテストし、Attentionモデルが全レベルでnaiveを上回った
- スプレッドが大きいペアはTP値をそのぶん広げる必要あり

### RLで決済も学習させる場合

**結論**: 行動空間に「Hold（保有継続）」を加えた3アクション設計が標準。ポジション保有ステップ数に応じたペナルティ報酬を設けることで過度な長期保有を防ぐ。

- 報酬設計の注意点:
  - スプレッドをステップ毎の報酬から差し引く
  - ポジション未決済のまま学習終了しないようエピソード終端で強制クローズ
  - Sharpe比ベース報酬（単純損益より安定した学習に繋がる）
- gym-mtsimはポジション管理・マルチアセット保有を標準サポート

---

## 3. バックテスト・MT5連携

### MetaTrader5 Pythonライブラリの使い方概要

**結論**: `mt5.copy_rates_from_pos()` / `copy_rates_range()` で5分足OHLCVを直接取得可能。Windows環境必須。データ取得→Pandas加工→RL環境への受け渡しが基本フロー。

主要API:
- `mt5.initialize()` / `mt5.shutdown()` — 接続管理
- `mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M5, date_from, date_to)` — 5分足取得
- `mt5.order_send(request)` — 発注（ライブ取引用）
- `mt5.positions_get()` — ポジション確認

**情報源**:
- [Algorithmic Forex Trading with Python + MT5 (Medium)](https://medium.com/mlearning-ai/algorithmic-forex-trading-with-python-using-metatrader5-python-library-for-accurate-data-19dbafb8573c)
- [Python Guide to MT5 Automation & AI Integration](https://www.digibeatrix.com/python/en/api-libraries/mt5-python-automation-guide/)
- [MT5 Python Trading Framework (GitHub)](https://github.com/ntungufhadzeni/MT5-Python-Trading)

### Python ↔ MT5 の連携パターン

| パターン | 概要 | 用途 |
|---|---|---|
| MT5 Pythonライブラリ（直接） | pip install MetaTrader5 でデータ取得・発注 | 最もシンプル |
| gym-mtsim | Gym環境としてMT5をラップ、RL訓練に直結 | RL開発一体型 |
| Backtrader-MQL5-API | BacktraderからMQL5経由で発注 | 既存Backtrader資産活用 |
| ONNX経由でEAに組み込み | PythonモデルをMT5 EAに埋め込む | 本番稼働向け |

**実装上の注意**:
- MT5 Pythonライブラリ is **Windowsのみ**（EC2 Windows環境で実行する）
- バックテストはローカルLinuxでPandasデータを使い、発注のみEC2 MT5へ投げる設計が効率的
- ライブ取引では非同期処理（asyncio）でティックを監視するパターンが一般的

---

## 4. 実装スタートに適したフレームワーク・ライブラリ

**結論**: 初期実装は `gym-anytrading + Stable-Baselines3(PPO)` が最速。MT5連携まで踏み込むなら `gym-mtsim` が直結。本番デプロイ後は ONNX経由でEA化する2段階戦略が現実的。

### ライブラリ比較

| ライブラリ | 特徴 | 向いている用途 | 注意点 |
|---|---|---|---|
| **gym-anytrading** | シンプル・軽量。Forex/Stocks環境を提供。SB3と公式統合例あり | プロトタイプ・アルゴ比較 | MT5非対応、データは自前準備 |
| **gym-mtsim** | MT5から直接データ取得、ヘッジング対応、OpenAI Gym互換 | MT5本番連携を見据えた開発 | Windowsのみ・複雑なアクション空間 |
| **Stable-Baselines3 (SB3)** | PPO/DQN/A2C等を統一APIで提供。最も活発にメンテ | エージェント学習全般 | 複雑なアクション空間はマスク要 |
| **FinRL** | 多数の金融環境・データソース統合。論文実装多数 | 比較実験・ベンチマーク | 依存が重い |
| **Ray RLlib** | 分散学習対応、A3C/PPOの大規模実験向け | 本格的なマルチエージェント | セットアップコスト高 |

### 推奨スタート構成

```
段階1（プロトタイプ）: gym-anytrading + Stable-Baselines3(PPO) + CSVデータ
段階2（MT5連携）: gym-mtsim + SB3 + EC2 Windows MT5
段階3（本番）: 学習済みモデル → ONNX → MT5 EAに組み込み or Python Socketで発注
```

**情報源**:
- [gym-anytrading GitHub](https://github.com/AminHP/gym-anytrading)
- [gym-mtsim GitHub](https://github.com/AminHP/gym-mtsim)
- [Stable-Baselines3 PPO ドキュメント](https://stable-baselines3.readthedocs.io/en/master/modules/ppo.html)
- [Gymnasium サードパーティ環境一覧](https://gymnasium.farama.org/environments/third_party_environments/)

---

## 総合判断・実装優先順位

1. **アルゴリズム選択**: まずPPO（SB3デフォルト）で動作確認 → DQNと比較 → Transformer Encoderを特徴量抽出に使う形で拡張
2. **決済設計**: 固定時間（5分後クローズ）からスタートし、TP/SL付き3アクション設計に移行
3. **報酬関数**: Sharpe比ベース + スプレッドペナルティを必ず組み込む（手数料なし実験は意味が薄い）
4. **MT5連携**: プロト段階はCSVで十分、MT5連携はgym-mtsimで段階的に組み込む
5. **本番移行**: ONNX経由のEA埋め込みが最も安定した本番運用パターン
