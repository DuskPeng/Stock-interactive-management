"""Read/write portfolio data from XLSX files and refresh market fields."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import pandas as pd

from portfolio_manager.quotes import QuoteProvider, quotes_to_frame


DEFAULT_HEADERS = [
    "股票代码",
    "名称",
    "持仓",
    "当前价格",
    "昨日收盘价",
    "涨跌幅",
    "成本价",
    "总值",
    "当日盈亏",
    "总盈亏",
]

# 用户要求必须由人工维护、程序不可写入的列。
MANUAL_COLUMNS = {"股票代码", "持仓", "成本价"}
# 标签允许人工维护，也允许在web交互中编辑并保存。
TAG_COLUMN = "标签"

# 市场刷新流程允许写入/重算的字段。
MARKET_UPDATABLE_COLUMNS = {"名称", "当前价格", "昨日收盘价", "涨跌幅", "总值", "当日盈亏", "总盈亏"}


@dataclass
class XlsxPortfolioIO:
    """Helper for reading and updating an XLSX portfolio."""

    path: Path | str
    sheet_name: str | int | None = 0

    def __post_init__(self) -> None:
        self.path = Path(self.path)

    def read(self) -> pd.DataFrame:
        """Read the portfolio data from disk.

        Raises:
            ValueError: if required headers are missing.
        """

        df = pd.read_excel(self.path, sheet_name=self.sheet_name)
        missing = [col for col in DEFAULT_HEADERS if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required headers: {missing}")
        return df

    def update_quotes(self, provider: QuoteProvider) -> pd.DataFrame:
        """Update market fields using a quote provider.

        Important:
            This function only recalculates market-derived fields and leaves
            manual columns untouched by design.
        """

        df = self.read()
        codes = df["股票代码"].dropna().astype(str).tolist()
        quotes = provider.fetch(codes)
        quote_df = quotes_to_frame(quotes)

        merged = df.merge(quote_df, on="股票代码", how="left", suffixes=("", "_new"))

        for col in ["名称", "当前价格", "昨日收盘价", "涨跌幅"]:
            new_col = f"{col}_new"
            if new_col in merged:
                merged[col] = merged[new_col].combine_first(merged[col])
                merged.drop(columns=[new_col], inplace=True)

        merged = self.recalculate_metrics(merged)
        return merged

    @staticmethod
    def recalculate_metrics(df: pd.DataFrame) -> pd.DataFrame:
        """Recalculate total value and P/L metrics based on current fields."""

        updated = df.copy()
        updated["总值"] = updated["持仓"].fillna(0) * updated["当前价格"].fillna(0)
        updated["当日盈亏"] = (
            updated["当前价格"].fillna(0) - updated["昨日收盘价"].fillna(0)
        ) * updated["持仓"].fillna(0)
        updated["总盈亏"] = (
            updated["当前价格"].fillna(0) - updated["成本价"].fillna(0)
        ) * updated["持仓"].fillna(0)
        return updated

    def save(self, df: pd.DataFrame) -> None:
        """Persist a dataframe to disk while preserving manual columns.

        This is the safest default write mode.
        """

        existing = pd.read_excel(self.path, sheet_name=self.sheet_name)
        for col in MANUAL_COLUMNS:
            if col in existing.columns and col in df.columns:
                df[col] = existing[col]
        df.to_excel(self.path, index=False)

    def save_market_update(self, df: pd.DataFrame) -> None:
        """Save only market-updatable columns back to XLSX.

        Use this for formal data update runs where user-managed columns must not
        be touched: 股票代码 / 持仓 / 成本价.
        """

        existing = self.read()
        merged = existing.copy()

        # 允许写回行情与计算列。
        for col in MARKET_UPDATABLE_COLUMNS:
            if col in df.columns:
                merged[col] = df[col]

        # 如果数据文件已包含标签列，则保留原始标签（不在行情流程中覆盖）。
        if TAG_COLUMN in existing.columns:
            merged[TAG_COLUMN] = existing[TAG_COLUMN]

        merged.to_excel(self.path, index=False)

    def save_with_tags(self, df: pd.DataFrame) -> None:
        """Save market fields + tag field while preserving strict manual columns."""

        existing = self.read()
        merged = existing.copy()

        for col in MARKET_UPDATABLE_COLUMNS:
            if col in df.columns:
                merged[col] = df[col]

        if TAG_COLUMN in df.columns:
            merged[TAG_COLUMN] = df[TAG_COLUMN]

        merged.to_excel(self.path, index=False)

    def write_new(self, rows: Sequence[dict]) -> None:
        """Write a brand new portfolio file using the default headers."""

        df = pd.DataFrame(rows, columns=DEFAULT_HEADERS)
        df.to_excel(self.path, index=False)


def ensure_headers(df: pd.DataFrame, headers: Iterable[str]) -> pd.DataFrame:
    """Ensure a dataframe has specific headers, adding empty columns if needed."""

    for header in headers:
        if header not in df.columns:
            df[header] = None
    return df
