"""Example: tag assets and visualize allocation by tag."""
import pandas as pd
import plotly.express as px

from portfolio_manager.simulation import allocation_by_column
from portfolio_manager.tags import TAG_COLUMN, TagManager


def main() -> None:
    df = pd.DataFrame(
        {
            "股票代码": ["AAPL", "TSLA", "0700.HK"],
            "总值": [1200, 800, 500],
            TAG_COLUMN: ["美股,红利", "美股,成长", "港股,互联网"],
        }
    )

    manager = TagManager()
    exploded = manager.explode_tags(df)
    allocation = allocation_by_column(exploded, TAG_COLUMN)

    fig = px.pie(allocation, names=TAG_COLUMN, values="总值", title="按标签分组的持仓占比")
    fig.show()


if __name__ == "__main__":
    main()
