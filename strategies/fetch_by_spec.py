"""
根据 spec 文件批量获取 A 股日线数据并生成图表。

用法:
    python fetch_by_spec.py --spec specs/three_stocks.yaml
    python fetch_by_spec.py --spec specs/three_stocks.yaml --no-plot
"""
import argparse
import os
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import yaml
import tushare as ts

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
FIG_DIR = ROOT / "figures"
SPEC_DIR = ROOT / "specs"

TUSHARE_TOKEN = os.environ.get(
    "TUSHARE_TOKEN", "72b6c6b3b124005a6a2ef2dc6a4f6314e02e49fac797fd55a8bb3966"
)


def load_spec(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def fetch_one(pro, ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """单只股票取日线。"""
    df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    if df is None or df.empty:
        raise ValueError(f"{ts_code} 取数失败（返回空）")
    return df.sort_values("trade_date").reset_index(drop=True)


def save_csv(df: pd.DataFrame, ts_code: str, name: str) -> Path:
    DATA_DIR.mkdir(exist_ok=True)
    code_part = ts_code.replace(".", "_")
    path = DATA_DIR / f"{name}_{code_part}_daily.csv"
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return path


def plot_single(df: pd.DataFrame, ts_code: str, stock_name: str, path: Path) -> None:
    plt.rcParams["font.sans-serif"] = ["Heiti TC", "SimHei", "Arial Unicode MS"]
    plt.rcParams["axes.unicode_minus"] = False
    df["trade_date"] = pd.to_datetime(df["trade_date"])

    plt.figure(figsize=(12, 5))
    plt.plot(df["trade_date"], df["close"], linewidth=1.5, color="#E02020")
    plt.title(f"{stock_name}({ts_code}) 收盘价曲线", fontsize=13, pad=12)
    plt.xlabel("日期")
    plt.ylabel("收盘价(元)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def plot_comparison(datasets: list[tuple[str, pd.DataFrame]], path: Path) -> None:
    """多股票归一化对比图(以起始日=100 起点)。"""
    plt.rcParams["font.sans-serif"] = ["Heiti TC", "SimHei", "Arial Unicode MS"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.figure(figsize=(14, 6))
    for stock_name, df in datasets:
        df = df.copy()
        df["trade_date"] = pd.to_datetime(df["trade_date"])
        df = df.sort_values("trade_date")
        base = df["close"].iloc[0]
        df["normalized"] = df["close"] / base * 100
        plt.plot(df["trade_date"], df["normalized"], linewidth=1.5, label=stock_name)
    plt.title("三只股票归一化对比(起点=100)", fontsize=14, pad=12)
    plt.xlabel("日期")
    plt.ylabel("归一化价格(起点=100)")
    plt.legend(loc="best")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--spec", type=Path, required=True, help="spec YAML 文件路径")
    p.add_argument("--no-plot", action="store_true", help="跳过图表生成")
    args = p.parse_args()

    spec = load_spec(args.spec)
    start_date = (datetime.now() - timedelta(days=spec["lookback_days"])).strftime("%Y%m%d")
    end_date = datetime.now().strftime("%Y%m%d")

    print(f"📋 spec: {args.spec.name} | 区间 {start_date} ~ {end_date}")
    print(f"🎯 标的数量: {len(spec['stocks'])}")

    pro = ts.pro_api(TUSHARE_TOKEN)
    summary = []
    plot_datasets = []

    for s in spec["stocks"]:
        ts_code = s["ts_code"]
        name = s["name"]
        stock_name = s.get("display_name", name)
        print(f"\n📥 {ts_code} {stock_name} ...")
        try:
            df = fetch_one(pro, ts_code, start_date, end_date)
        except Exception as e:
            print(f"❌ {ts_code} 失败: {e}")
            continue

        csv_path = save_csv(df, ts_code, name)
        period_return = (df["close"].iloc[-1] / df["close"].iloc[0] - 1) * 100
        print(
            f"  ✅ {len(df)} 个交易日 | "
            f"起 {df['close'].iloc[0]:.2f} → 终 {df['close'].iloc[-1]:.2f} | "
            f"区间 {period_return:+.2f}%"
        )
        print(f"  💾 {csv_path.relative_to(ROOT)}")

        if not args.no_plot:
            FIG_DIR.mkdir(exist_ok=True)
            fig_path = FIG_DIR / f"{name}_{ts_code.replace('.', '_')}_close_price.png"
            plot_single(df, ts_code, stock_name, fig_path)
            print(f"  🖼  {fig_path.relative_to(ROOT)}")
            plot_datasets.append((stock_name, df))

        summary.append(
            {
                "ts_code": ts_code,
                "name": stock_name,
                "trading_days": len(df),
                "start_close": df["close"].iloc[0],
                "end_close": df["close"].iloc[-1],
                "high": df["high"].max(),
                "low": df["low"].min(),
                "period_return_pct": round(period_return, 2),
            }
        )

    # 对比图(只有 ≥2 只股票才画)
    if not args.no_plot and len(plot_datasets) >= 2:
        comp_path = FIG_DIR / f"{spec.get('comparison_name', 'comparison')}_normalized.png"
        plot_comparison(plot_datasets, comp_path)
        print(f"\n📊 对比图: {comp_path.relative_to(ROOT)}")

    # 汇总表
    if summary:
        summary_df = pd.DataFrame(summary)
        summary_path = DATA_DIR / f"{spec.get('comparison_name', 'summary')}_summary.csv"
        summary_df.to_csv(summary_path, index=False, encoding="utf-8-sig")
        print(f"\n📑 汇总: {summary_path.relative_to(ROOT)}")
        print("\n" + summary_df.to_string(index=False))


if __name__ == "__main__":
    main()
