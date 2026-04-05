# 仕様: MT5 データ取得スクリプト（年ごとファイル分割）

## 概要
MT5から XAUUSD・DXY データを取得し、年ごとに分割したParquetファイルで保存する。
初回は5年分を年ごとに保存、以降は最新の1年ファイルだけ更新。

## ファイル出力

### ディレクトリ構成
```
data/raw/
├── XAUUSD_M1_20210101_20211231.parquet
├── XAUUSD_M5_20210101_20211231.parquet
├── XAUUSD_M15_20210101_20211231.parquet
├── XAUUSD_M60_20210101_20211231.parquet
├── DXY_M5_20210101_20211231.parquet
├── ...（毎年）...
├── XAUUSD_M1_20260101_20261231.parquet  ← 最新（毎回更新）
├── XAUUSD_M5_20260101_20261231.parquet  ← 最新（毎回更新）
└── DXY_M5_20260101_20261231.parquet     ← 最新（毎回更新）
```

### ファイル名規則
```
[SYMBOL]_[TIMEFRAME]_[START_DATE]_[END_DATE].parquet

例: XAUUSD_M5_20260101_20261231.parquet
日付: YYYYMMDD（暦年: 1月1日～12月31日）
```

## 取得データ

| シンボル | 時間足 | 用途 |
|---|---|---|
| XAUUSD | M1 | MTF（微調整） |
| XAUUSD | M5 | **メイン** ★ |
| XAUUSD | M15 | MTF（フィルター） |
| XAUUSD | M60 | MTF（トレンド） |
| DXY | M5 | 相関分析用 |

合計: **25ファイル**（5年 × 5種類）

## 実行フロー

### パラメータ仕様
```bash
python ml/fetch_mt5_data.py [--year YYYY]

--year YYYY    : 指定年のみ取得（例: --year 2026）
（省略時）     : 当年（2026）のみ取得
```

### 初回実行（全5年取得）
```bash
# 各年ごとに1回ずつ実行（合計5回）
python ml/fetch_mt5_data.py --year 2021
python ml/fetch_mt5_data.py --year 2022
python ml/fetch_mt5_data.py --year 2023
python ml/fetch_mt5_data.py --year 2024
python ml/fetch_mt5_data.py --year 2025
python ml/fetch_mt5_data.py --year 2026  # 当年
```

処理内容：
```
1. MT5接続
2. シンボル確認
3. 指定年の1月1日～12月31日（または今日まで）を取得
4. 各時間足（M1, M5, M15, M60）で XAUUSD 取得
5. DXY を M5 で取得
6. 各Parquetで保存
```

### 2回目以降（当年だけ更新）
```bash
# パラメータ省略で当年のみ更新
python ml/fetch_mt5_data.py

# または明示的に
python ml/fetch_mt5_data.py --year 2026
```

処理内容：
```
1. 最新ファイル（XAUUSD_M5_20260101_20261231.parquet）から year を抽出
2. 1月1日～今日のデータを取得
3. 最新ファイルを上書き
```

## 取得順序

**優先度順:**
1. XAUUSD M1
2. XAUUSD M5（★メイン）
3. XAUUSD M15
4. XAUUSD M60
5. DXY M5

**理由**: シンボルごと取得により、接続をまとめられる。

---

## エラーハンドリング・リトライ戦略

### リトライ方針（Q&A #3）
- **対象**: 各シンボル・時間足単位
- **リトライ回数**: N回（実装時に決定、推奨3回）
- **失敗時の動作**: 該当ファイルをスキップし、スクリプト全体は続行
- **効果**: 1つのシンボルのエラーで全体が止まらない

```
例: XAUUSD M1 取得失敗
  → XAUUSD M1 をスキップ
  → XAUUSD M5, M15, M60, DXY は継続取得
  → スクリプト終了後、ユーザーが手動で XAUUSD M1 を再取得
```

### 部分失敗時の Parquet 処理（Q&A #4）
- **自動削除**: 行わない
- **自動リネーム**: 行わない
- **ユーザー判断**: 破損したファイルは ユーザーが手動確認・削除して再実行

**理由**: 部分的な破損の判定が難しく、自動処理より安全。

---

## パフォーマンス

| パターン | 時間 | サイズ |
|---|---|---|
| 初回（5年） | 5〜10分 | 1年 ≈ 4MB |
| 更新（1年） | 1〜2分 | 1年 ≈ 4MB |

## Linux側の読込例

```python
import pandas as pd
import glob

def load_xauusd_m5():
    """全XAUUSD M5ファイルを統合"""
    files = sorted(glob.glob("data/raw/XAUUSD_M5_*.parquet"))
    dfs = [pd.read_parquet(f) for f in files]
    return pd.concat(dfs).sort_index()

df = load_xauusd_m5()
print(f"期間: {df.index[0]} 〜 {df.index[-1]}")
print(f"件数: {len(df):,}行")
```

## スコープ決定（含めない理由）

### ティックデータ（1分以下）は不要
| | ティック | 1分足 |
|---|---|---|
| 1年分の行数 | 数百万行 | 525,600行 |
| ストレージ | 100MB+ | 4MB |
| エンジニアリング難度 | 高 | 低 |
| スキャル必要度 | 不要 | 十分 |

**判断**: スキャルピング（5分～15分決済）では1分足で十分。後で必要なら追加。

### 指標イベント（CPI・雇用統計等）は今は不要
| | 指標イベント有 | 無 |
|---|---|---|
| 実装難度 | 高 | 低 |
| 初回学習に必須か | 不要 | 足りる |
| 複雑度増加 | 大 | 小 |

**判断**: 本番運用時（ステップ⑦）に「指標発表時間帯は稼働しない」フィルターで対応。初回は不要。

## 【保留リスト】
```
- ティックデータ（1分以下）
- 指標イベント（CPI・雇用統計等）
- 米10年債利回り
```

## 注意

- Windows環境必須（MetaTrader5ライブラリ）
- MT5起動状態が必要
- 初回は遅い（5〜10分）、以降は1〜2分
