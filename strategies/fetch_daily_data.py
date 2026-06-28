"""
获取股票日线数据并生成收盘价曲线图

用法:
    python fetch_daily_data.py
    python fetch_daily_data.py --ts_code 000988.SZ --days 365
    python fetch_daily_data.py --ts_code 600519.SH --days 180
"""
import argparse
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import tushare as ts

# Tushare Token（从项目环境变量或 .env 读取，避免硬编码）
import os

TUSHARE_TOKEN = os.environ.get(
    "TUSHARE_TOKEN", "72b6c6b3b124005a6a2ef2dc6a4f6314e02e49fac797fd55a8bb3966"
)

# 项目目录
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
FIG_DIR = ROOT / "figures"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="获取 A 股日线数据并画图")
    p.add_argument("--ts_code", default="000988.SZ", help="股票代码，如 000988.SZ")
    p.add_argument("--days", type=int, default=365, help="回看天数")
    p.add_argument("--name", default="huagong", help="文件名前缀")
    return p.parse_args()


def fetch_daily(ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """从 Tushare 拉取日线数据。"""
    pro = ts.pro_api(TUSHARE_TOKEN)
    df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    if df is None or df.empty:
        raise ValueError(f"未获取到 {ts_code} 的数据")
    return df.sort_values("trade_date").reset_index(drop=True)


def plot_close_price(df: pd.DataFrame, ts_code: str, save_path: Path) -> None:
    """画收盘价曲线图。"""
    plt.rcParams["font.sans-serif"] = ["Heiti TC", "SimHei", "Arial Unicode MS"]
    plt.rcParams["axes.unicode_minus"] = False
    df["trade_date"] = pd.to_datetime(df["trade_date"])

    plt.figure(figsize=(14, 6))
    plt.plot(df["trade_date"], df["close"], linewidth=1.5, color="#E02020")
    plt.title(f"{ts_code} 每日收盘价（{df['trade_date'].iloc[0].date()} ~ {df['trade_date'].iloc[-1].date()}）", fontsize=14, pad=15)
    plt.xlabel("日期", fontsize=11)
    plt.ylabel("收盘价 (元)", fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


def main() -> None:
    args = parse_args()
    DATA_DIR.mkdir(exist_ok=True)
    FIG_DIR.mkdir(exist_ok=True)

    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y%m%d")

    print(f"📥 获取 {args.ts_code} {start_date} ~ {end_date} 日线数据 ...")
    df = fetch_daily(args.ts_code, start_date, end_date)
    print(f"✅ 共 {len(df)} 个交易日")

    # 保存 CSV
    csv_path = DATA_DIR / f"{args.name}_{args.ts_code.replace('.', '_')}_daily.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"💾 CSV 已保存: {csv_path}")

    # 画图
    fig_path = FIG_DIR / f"{args.name}_{args.ts_code.replace('.', '_')}_close_price.png"
    plot_close_price(df, args.ts_code, fig_path)
    print(f"🖼  图表已保存: {fig_path}")

    # 简单统计
    print("\n📊 行情概览:")
    print(f"  - 起始价: {df['close'].iloc[0]:.2f} 元")
    print(f"  - 终止价: {df['close'].iloc[-1]:.2f} 元")
    print(f"  - 期间最高: {df['high'].max():.2f} 元")
    print(f"  - 期间最低: {df['low'].min():.2f} 元")
    period_return = (df["close"].iloc[-1] / df["close"].iloc[0] - 1) * 100
    print(f"  - 区间涨跌幅: {period_return:+.2f}%")


if __name__ == "__main__":
    main()
