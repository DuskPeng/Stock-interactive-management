"""Quote provider interfaces and implementations.

This module defines a small abstraction layer so data sources can be swapped
(e.g., online providers, offline mocks, or a cached snapshot) without changing
business logic.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, Protocol

import pandas as pd

try:
    import yfinance as yf
except ImportError:  # pragma: no cover - optional dependency
    yf = None


@dataclass(frozen=True)
class Quote:
    """Structured quote information for a single ticker."""

    code: str
    name: str
    current_price: float
    previous_close: float
    change_pct: float
    timestamp: datetime


class QuoteProvider(Protocol):
    """Protocol for quote providers."""

    def fetch(self, codes: Iterable[str]) -> Dict[str, Quote]:
        """Return a mapping of stock code -> Quote."""


class YFinanceQuoteProvider:
    """Quote provider backed by yfinance.

    Notes:
        - Requires network access and the optional ``yfinance`` dependency.
        - ``codes`` should match Yahoo Finance tickers.
    """

    def fetch(self, codes: Iterable[str]) -> Dict[str, Quote]:
        if yf is None:
            raise RuntimeError("yfinance is not installed. Please add it to your environment.")

        quotes: Dict[str, Quote] = {}
        now = datetime.now()
        for code in codes:
            ticker = yf.Ticker(code)
            info = ticker.fast_info
            name = ticker.get_info().get("shortName", "")
            current_price = float(info.get("last_price", 0.0))
            previous_close = float(info.get("previous_close", 0.0))
            change_pct = 0.0
            if previous_close:
                change_pct = (current_price - previous_close) / previous_close
            quotes[code] = Quote(
                code=code,
                name=name,
                current_price=current_price,
                previous_close=previous_close,
                change_pct=change_pct,
                timestamp=now,
            )
        return quotes


class FakeQuoteProvider:
    """Deterministic provider for demos and tests."""

    def __init__(self, base_prices: Dict[str, float] | None = None) -> None:
        self._base_prices = base_prices or {}

    def fetch(self, codes: Iterable[str]) -> Dict[str, Quote]:
        now = datetime.now()
        quotes: Dict[str, Quote] = {}
        for idx, code in enumerate(codes, start=1):
            base = self._base_prices.get(code, 10.0 + idx)
            current_price = base * (1 + (idx % 5) * 0.01)
            previous_close = base
            change_pct = (current_price - previous_close) / previous_close
            quotes[code] = Quote(
                code=code,
                name=f"DEMO-{code}",
                current_price=current_price,
                previous_close=previous_close,
                change_pct=change_pct,
                timestamp=now,
            )
        return quotes


def quotes_to_frame(quotes: Dict[str, Quote]) -> pd.DataFrame:
    """Convert a quote mapping to a pandas DataFrame for merging."""

    rows = [
        {
            "股票代码": quote.code,
            "名称": quote.name,
            "当前价格": quote.current_price,
            "昨日收盘价": quote.previous_close,
            "涨跌幅": quote.change_pct,
        }
        for quote in quotes.values()
    ]
    return pd.DataFrame(rows)
