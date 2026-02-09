"""Portfolio simulation helpers for hypothetical adjustments."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import pandas as pd


@dataclass
class PositionAdjustment:
    """A hypothetical adjustment to a position."""

    code: str
    delta_shares: float


def apply_adjustments(df: pd.DataFrame, adjustments: Dict[str, float]) -> pd.DataFrame:
    """Apply adjustments and return a new dataframe.

    Args:
        df: Original portfolio dataframe.
        adjustments: Mapping of stock code -> delta shares.

    Returns:
        A new dataframe with updated holdings and recalculated value/profit columns.
    """

    updated = df.copy()
    updated["持仓"] = updated["持仓"].fillna(0)
    for code, delta in adjustments.items():
        updated.loc[updated["股票代码"] == code, "持仓"] += delta

    updated["总值"] = updated["持仓"].fillna(0) * updated["当前价格"].fillna(0)
    updated["当日盈亏"] = (
        updated["当前价格"].fillna(0) - updated["昨日收盘价"].fillna(0)
    ) * updated["持仓"].fillna(0)
    updated["总盈亏"] = (
        updated["当前价格"].fillna(0) - updated["成本价"].fillna(0)
    ) * updated["持仓"].fillna(0)
    return updated


def allocation_by_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Calculate allocation ratio grouped by a column."""

    if column not in df.columns:
        raise ValueError(f"Column '{column}' is required for allocation analysis.")
    grouped = df.groupby(column, dropna=False)["总值"].sum().reset_index()
    total = grouped["总值"].sum()
    grouped["比例"] = grouped["总值"] / total if total else 0
    return grouped
