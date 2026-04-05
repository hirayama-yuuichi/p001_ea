"""
MT5からXAUUSD・DXYの価格データを取得してParquet形式で保存するスクリプト

動作環境: EC2 Windows（MetaTrader5ライブラリはWindowsのみ対応）
使用法:
  python ml/fetch_mt5_data.py              # 当年（2026年）のみ取得
  python ml/fetch_mt5_data.py --year 2025 # 指定年を取得

保存先: data/raw/[SYMBOL]_[TIMEFRAME]_YYYYMMDD_YYYYMMDD.parquet
"""

import argparse
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
DATA_DIR   = Path(__file__).parent.parent / "data" / "raw"

# 取得対象: (シンボル, 時間足)のタプルリスト
# 取得順序: XAUUSD(M1→M5→M15→H1) → DXY(M5)
FETCH_TARGETS = [
    ("XAUUSD", mt5.TIMEFRAME_M1),
    ("XAUUSD", mt5.TIMEFRAME_M5),
    ("XAUUSD", mt5.TIMEFRAME_M15),
    ("XAUUSD", mt5.TIMEFRAME_H1),
    ("DXY", mt5.TIMEFRAME_M5),
]

MAX_RETRIES = 3  # リトライ回数
# ---------------


def timeframe_to_string(timeframe: int) -> str:
    """時間足定数を文字列に変換"""
    timeframe_map = {
        mt5.TIMEFRAME_M1: "M1",
        mt5.TIMEFRAME_M5: "M5",
        mt5.TIMEFRAME_M15: "M15",
        mt5.TIMEFRAME_H1: "H1",
    }
    return timeframe_map.get(timeframe, "UNKNOWN")


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
    timeframe_str = timeframe_to_string(timeframe)
    print(f"データ取得中: {symbol} {timeframe_str} {date_from.date()} 〜 {date_to.date()}")

    rates = mt5.copy_rates_range(symbol, timeframe, date_from, date_to)
    if rates is None or len(rates) == 0:
        print(f"データ取得失敗: {symbol} {timeframe_str} - {mt5.last_error()}")
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

    print(f"  取得件数: {len(df):,}件  期間: {df.index[0]} 〜 {df.index[-1]}")
    return df


def save_parquet(df: pd.DataFrame, symbol: str, timeframe: int, date_from: datetime, date_to: datetime) -> Path:
    """Parquet形式で保存する"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    timeframe_str = timeframe_to_string(timeframe)
    filename = f"{symbol}_{timeframe_str}_{date_from.strftime('%Y%m%d')}_{date_to.strftime('%Y%m%d')}.parquet"
    filepath = DATA_DIR / filename
    df.to_parquet(filepath)
    size_mb = filepath.stat().st_size / 1024 / 1024
    print(f"  保存完了: {filename} ({size_mb:.1f} MB)")
    return filepath


def get_year_date_range(year: int) -> tuple[datetime, datetime]:
    """指定年の1月1日から12月31日のdatetimeを返す"""
    date_from = datetime(year, 1, 1, tzinfo=timezone.utc)
    date_to = datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

    # 当年の場合は今日までで制限
    today = datetime.now(timezone.utc)
    if year == today.year:
        date_to = today

    return date_from, date_to


def fetch_with_retry(symbol: str, timeframe: int, date_from: datetime, date_to: datetime, max_retries: int = MAX_RETRIES) -> pd.DataFrame:
    """リトライ機能付きでデータ取得"""
    for attempt in range(1, max_retries + 1):
        try:
            df = fetch_ohlcv(symbol, timeframe, date_from, date_to)
            if not df.empty:
                return df
        except Exception as e:
            print(f"  リトライ {attempt}/{max_retries}: エラー発生 - {e}")
            if attempt < max_retries:
                print(f"  {attempt}秒待機中...")
                import time
                time.sleep(attempt)

        if attempt == max_retries:
            print(f"  ⚠️  {symbol} {timeframe_to_string(timeframe)} の取得に失敗。スキップします。")
            return pd.DataFrame()

    return pd.DataFrame()


def main():
    # コマンドライン引数を解析
    parser = argparse.ArgumentParser(description="MT5からXAUUSD・DXYデータを取得してParquet保存")
    parser.add_argument("--year", type=int, default=None, help="取得対象年（例: 2026）。省略時は当年")
    args = parser.parse_args()

    target_year = args.year if args.year else datetime.now(timezone.utc).year
    date_from, date_to = get_year_date_range(target_year)

    print(f"=== MT5データ取得スクリプト ===")
    print(f"対象年: {target_year}")
    print(f"期間: {date_from.date()} 〜 {date_to.date()}")
    print(f"取得対象: XAUUSD(M1,M5,M15,H1) + DXY(M5)")
    print()

    # MT5接続
    if not connect_mt5():
        sys.exit(1)

    try:
        # シンボル確認
        print("シンボル確認中...")
        for symbol, _ in FETCH_TARGETS:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                print(f"エラー: シンボル '{symbol}' が見つかりません。")
                sys.exit(1)

            if not symbol_info.visible:
                mt5.symbol_select(symbol, True)

            print(f"  {symbol}: スプレッド={symbol_info.spread}, 小数点={symbol_info.digits}")

        print()

        # データ取得
        failed_targets = []
        successful_targets = []

        for symbol, timeframe in FETCH_TARGETS:
            df = fetch_with_retry(symbol, timeframe, date_from, date_to)

            if df.empty:
                failed_targets.append((symbol, timeframe_to_string(timeframe)))
            else:
                # 保存
                save_parquet(df, symbol, timeframe, date_from, date_to)
                successful_targets.append((symbol, timeframe_to_string(timeframe)))

        # 結果表示
        print()
        print("=== 取得完了 ===")
        print(f"成功: {len(successful_targets)}/{len(FETCH_TARGETS)}")
        if successful_targets:
            for symbol, timeframe in successful_targets:
                print(f"  ✓ {symbol} {timeframe}")

        if failed_targets:
            print(f"失敗: {len(failed_targets)}/{len(FETCH_TARGETS)}")
            for symbol, timeframe in failed_targets:
                print(f"  ✗ {symbol} {timeframe}")
            print("\n⚠️  失敗したシンボル・時間足は再度スクリプトを実行してください。")
            print("     または EC2 接続・MT5 起動状態を確認してください。")

    finally:
        mt5.shutdown()
        print("\nMT5切断")


if __name__ == "__main__":
    main()
