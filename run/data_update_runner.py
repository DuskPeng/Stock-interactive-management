"""正式运行：在线更新 portfolio.xlsx 行情数据。

功能说明：
1. 读取指定XLSX（默认 portfolio.xlsx）。
2. 基于“股票代码”在线拉取行情。
3. 仅更新非人工列（名称、价格、涨跌幅、收益相关列），
   严格保留“股票代码/持仓/成本价”。
4. 支持 once（执行一次）与 daemon（按日定时）模式。

示例：
    python run/data_update_runner.py --file portfolio.xlsx --mode once
    python run/data_update_runner.py --file portfolio.xlsx --mode daemon --time 15:30
"""
from __future__ import annotations

import argparse
import time
from datetime import datetime, timedelta
from pathlib import Path

from portfolio_manager.data_io import XlsxPortfolioIO
from portfolio_manager.quotes import YFinanceQuoteProvider


def update_once(file_path: Path) -> None:
    """Run one online update cycle and save market fields back to XLSX."""

    io = XlsxPortfolioIO(file_path)
    provider = YFinanceQuoteProvider()
    updated_df = io.update_quotes(provider)
    io.save_market_update(updated_df)
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] 更新完成: {file_path}")


def _next_run_at(target_hhmm: str) -> datetime:
    """Compute next run datetime for a daily HH:MM target."""

    now = datetime.now()
    hh, mm = map(int, target_hhmm.split(":"))
    run_at = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
    if run_at <= now:
        run_at += timedelta(days=1)
    return run_at


def run_daily(file_path: Path, run_time: str) -> None:
    """Run daily update loop."""

    print(f"进入每日更新模式，目标时间 {run_time}，文件 {file_path}")
    while True:
        next_run = _next_run_at(run_time)
        wait_seconds = max(1, int((next_run - datetime.now()).total_seconds()))
        print(f"下次执行时间: {next_run:%Y-%m-%d %H:%M:%S}，等待 {wait_seconds} 秒")
        time.sleep(wait_seconds)
        try:
            update_once(file_path)
        except Exception as exc:  # noqa: BLE001
            print(f"更新失败: {exc}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="在线更新 portfolio.xlsx 行情数据")
    parser.add_argument("--file", type=Path, default=Path("portfolio.xlsx"), help="目标XLSX文件路径")
    parser.add_argument("--mode", choices=["once", "daemon"], default="once", help="执行模式")
    parser.add_argument("--time", default="15:30", help="每日执行时间，格式 HH:MM，仅 daemon 模式生效")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.file.exists():
        raise FileNotFoundError(f"未找到文件: {args.file}")

    if args.mode == "once":
        update_once(args.file)
    else:
        run_daily(args.file, args.time)


if __name__ == "__main__":
    main()
