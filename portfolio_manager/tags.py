"""Tag utilities for portfolio assets."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

import pandas as pd


TAG_COLUMN = "标签"


@dataclass
class TagManager:
    """Manage tags stored in a dataframe column.

    Tags are stored as comma-separated text to keep XLSX files human-editable.
    """

    separator: str = ","

    def normalize(self, raw: str | float | None) -> List[str]:
        """Normalize raw tag input into a list of tags."""

        if raw is None or (isinstance(raw, float) and pd.isna(raw)):
            return []
        if not isinstance(raw, str):
            raw = str(raw)
        return [tag.strip() for tag in raw.split(self.separator) if tag.strip()]

    def set_tags(self, df: pd.DataFrame, code: str, tags: Iterable[str]) -> pd.DataFrame:
        """Set tags for a given stock code in the dataframe."""

        if TAG_COLUMN not in df.columns:
            df[TAG_COLUMN] = ""
        tag_text = self.separator.join(sorted(set(tags)))
        df.loc[df["股票代码"] == code, TAG_COLUMN] = tag_text
        return df

    def explode_tags(self, df: pd.DataFrame) -> pd.DataFrame:
        """Expand tags into multiple rows for aggregation."""

        if TAG_COLUMN not in df.columns:
            return df.assign(**{TAG_COLUMN: ""})
        df = df.copy()
        df[TAG_COLUMN] = df[TAG_COLUMN].apply(self.normalize)
        return df.explode(TAG_COLUMN)
