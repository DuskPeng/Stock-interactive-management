"""Example: read XLSX, update quotes, and visualize total value."""
from pathlib import Path

import pandas as pd
import plotly.express as px

from portfolio_manager.data_io import XlsxPortfolioIO
from portfolio_manager.quotes import FakeQuoteProvider

SAMPLE_PATH = Path("sample_portfolio.xlsx")


def build_sample() -> None:
    rows = [
        {
            "股票代码": "AAPL",
            "名称": "Apple",
            "持仓": 10,
            "当前价格": 0,
            "昨日收盘价": 0,
            "涨跌幅": 0,
            "成本价": 120,
            "总值": 0,
            "当日盈亏": 0,
            "总盈亏": 0,
        },
        {
            "股票代码": "TSLA",
            "名称": "Tesla",
            "持仓": 5,
            "当前价格": 0,
            "昨日收盘价": 0,
            "涨跌幅": 0,
            "成本价": 200,
            "总值": 0,
            "当日盈亏": 0,
            "总盈亏": 0,
        },
    ]
    XlsxPortfolioIO(SAMPLE_PATH).write_new(rows)


def main() -> None:
    if not SAMPLE_PATH.exists():
        build_sample()

    io = XlsxPortfolioIO(SAMPLE_PATH)
    df = io.update_quotes(FakeQuoteProvider())
    io.save(df)

    fig = px.bar(df, x="股票代码", y="总值", title="示例：更新后的总值")
    fig.show()


if __name__ == "__main__":
    main()
