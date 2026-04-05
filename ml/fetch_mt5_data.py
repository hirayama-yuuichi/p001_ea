"""
MT5からXAUUSDの価格データを取得してParquet形式で保存するスクリプト

動作環境: EC2 Windows（MetaTrader5ライブラリはWindowsのみ対応）
保存先: data/raw/XAUUSD_M5_YYYYMMDD_YYYYMMDD.parquet
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

# MetaTrader5はWindowsのみ
try:
    import MetaTrader5 as mt5
except ImportError:
    print("MetaTrader5 ライブラリが見つかりません。EC2 Windows上で実行してください。")
    sys.exit(1)

# ---- 設定 ----
SYMBOL     = "XAUUSD"
TIMEFRAME  = mt5.TIMEFRAME_M5       # 5分足
DATE_FROM  = datetime(2025, 7, 21, tzinfo=timezone.utc)  # MT5にロードされている最古日
DATE_TO    = datetime.now(timezone.utc)                   # 今日まで
DATA_DIR   = Path(__file__).parent.parent / "data" / "raw"
# --------------


def connect_mt5() -> bool:
    """MT5に接続する"""
    if not mt5.initialize():
        print(f"MT5初期化失敗: {mt5.last_error()}")
        return False
    info = mt5.terminal_info()
    print(f"MT5接続OK: {info.name} build={info.build}")
    return True


def fetch_ohlcv(symbol: str, timeframe: int, date_from: datetime, date_to: datetime) -> pd.DataFrame:
    """OHLCVデータを取得してDataFrameで返す"""
    print(f"データ取得中: {symbol} {date_from.date()} 〜 {date_to.date()}")

    rates = mt5.copy_rates_range(symbol, timeframe, date_from, date_to)
    if rates is None or len(rates) == 0:
        print(f"データ取得失敗: {mt5.last_error()}")
        return pd.DataFrame()

    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    df = df.set_index("time")
    df = df.rename(columns={
        "open": "open",
        "high": "high",
        "low": "low",
        "close": "close",
        "tick_volume": "volume",
    })
    df = df[["open", "high", "low", "close", "volume"]]

    print(f"取得件数: {len(df):,}件  期間: {df.index[0]} 〜 {df.index[-1]}")
    return df


def save_parquet(df: pd.DataFrame, symbol: str, date_from: datetime, date_to: datetime) -> Path:
    """Parquet形式で保存する"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{symbol}_M5_{date_from.strftime('%Y%m%d')}_{date_to.strftime('%Y%m%d')}.parquet"
    filepath = DATA_DIR / filename
    df.to_parquet(filepath)
    size_mb = filepath.stat().st_size / 1024 / 1024
    print(f"保存完了: {filepath} ({size_mb:.1f} MB)")
    return filepath


def main():
    # MT5接続
    if not connect_mt5():
        sys.exit(1)

    try:
        # シンボル確認
        symbol_info = mt5.symbol_info(SYMBOL)
        if symbol_info is None:
            print(f"シンボル '{SYMBOL}' が見つかりません。MT5のシンボル一覧を確認してください。")
            sys.exit(1)

        if not symbol_info.visible:
            # シンボルが非表示の場合は表示させる
            mt5.symbol_select(SYMBOL, True)

        print(f"スプレッド: {symbol_info.spread} ポイント")
        print(f"小数点桁数: {symbol_info.digits}")

        # データ取得
        df = fetch_ohlcv(SYMBOL, TIMEFRAME, DATE_FROM, DATE_TO)
        if df.empty:
            sys.exit(1)

        # 基本統計を表示
        print(f"\n--- 基本統計 ---")
        print(f"終値の平均: {df['close'].mean():.2f}")
        print(f"終値の最小: {df['close'].min():.2f}")
        print(f"終値の最大: {df['close'].max():.2f}")
        print(f"ATR(14)の平均: {(df['high'] - df['low']).rolling(14).mean().mean():.2f}")

        # 保存
        save_parquet(df, SYMBOL, DATE_FROM, DATE_TO)

    finally:
        mt5.shutdown()
        print("MT5切断")


if __name__ == "__main__":
    main()
