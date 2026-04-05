"""
MT5で取得可能な各足の期間とティック数を確認するスクリプト
"""

import sys
from datetime import datetime, timezone

try:
    import MetaTrader5 as mt5
except ImportError:
    print("MetaTrader5 ライブラリが見つかりません。")
    sys.exit(1)

import pandas as pd

SYMBOL = "XAUUSD"

TIMEFRAMES = [
    (mt5.TIMEFRAME_M1,  "M1  (1分足)"),
    (mt5.TIMEFRAME_M5,  "M5  (5分足)"),
    (mt5.TIMEFRAME_M15, "M15 (15分足)"),
    (mt5.TIMEFRAME_M30, "M30 (30分足)"),
    (mt5.TIMEFRAME_H1,  "H1  (1時間足)"),
    (mt5.TIMEFRAME_H4,  "H4  (4時間足)"),
    (mt5.TIMEFRAME_D1,  "D1  (日足)"),
    (mt5.TIMEFRAME_W1,  "W1  (週足)"),
    (mt5.TIMEFRAME_MN1, "MN1 (月足)"),
]


def main():
    if not mt5.initialize():
        print(f"MT5初期化失敗: {mt5.last_error()}")
        sys.exit(1)

    info = mt5.terminal_info()
    print(f"MT5接続OK: {info.name} build={info.build}\n")

    # ---- 各足の取得可能期間 ----
    print(f"{'='*60}")
    print(f"{'足':12} {'件数':>8}  {'最古':24} {'最新':24}")
    print(f"{'='*60}")

    for tf, label in TIMEFRAMES:
        rates = mt5.copy_rates_from_pos(SYMBOL, tf, 0, 99999)
        if rates is None or len(rates) == 0:
            print(f"{label:12} {'データなし':>8}")
            continue
        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
        oldest = str(df["time"].min())[:19]
        newest = str(df["time"].max())[:19]
        print(f"{label:12} {len(df):>8,}件  {oldest}  {newest}")

    # ---- ティックデータ ----
    print(f"\n{'='*60}")
    print("ティックデータ（直近 10,000件）")
    print(f"{'='*60}")

    date_from = datetime(2026, 4, 1, tzinfo=timezone.utc)
    date_to   = datetime.now(timezone.utc)
    ticks = mt5.copy_ticks_range(SYMBOL, date_from, date_to, mt5.COPY_TICKS_ALL)

    if ticks is None or len(ticks) == 0:
        print(f"ティック取得失敗: {mt5.last_error()}")
    else:
        df_tick = pd.DataFrame(ticks)
        df_tick["time"] = pd.to_datetime(df_tick["time"], unit="s", utc=True)
        print(f"件数  : {len(df_tick):,}")
        print(f"最古  : {df_tick['time'].min()}")
        print(f"最新  : {df_tick['time'].max()}")
        print(f"Bid最小: {df_tick['bid'].min():.2f}")
        print(f"Bid最大: {df_tick['bid'].max():.2f}")
        print(f"\n先頭5件:")
        print(df_tick[["time", "bid", "ask", "last", "volume"]].head())

    mt5.shutdown()
    print("\nMT5切断")


if __name__ == "__main__":
    main()
