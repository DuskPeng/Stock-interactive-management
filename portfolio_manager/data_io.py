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

MANUAL_COLUMNS = {"股票代码", "持仓", "成本价", "标签"}


@dataclass
class XlsxPortfolioIO:
    """Helper for reading and updating an XLSX portfolio."""

    path: Path
    sheet_name: str | int | None = 0

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
        """Update non-manual fields using a quote provider.

        This function only refreshes fields derived from market data and leaves
        manual columns untouched ("股票代码", "持仓", "成本价", "标签").
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

        merged["总值"] = merged["持仓"].fillna(0) * merged["当前价格"].fillna(0)
        merged["当日盈亏"] = (
            merged["当前价格"].fillna(0) - merged["昨日收盘价"].fillna(0)
        ) * merged["持仓"].fillna(0)
        merged["总盈亏"] = (
            merged["当前价格"].fillna(0) - merged["成本价"].fillna(0)
        ) * merged["持仓"].fillna(0)

        return merged

    def save(self, df: pd.DataFrame) -> None:
        """Persist the updated portfolio to disk.

        Manual columns are preserved from the existing file to avoid accidental
        overwrites when user-edited values are present.
        """

        existing = pd.read_excel(self.path, sheet_name=self.sheet_name)
        for col in MANUAL_COLUMNS:
            if col in existing.columns and col in df.columns:
                df[col] = existing[col]
        df.to_excel(self.path, index=False)

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
