"""Example: simulate adjustments and compare before/after values."""
import pandas as pd
import plotly.express as px

from portfolio_manager.simulation import apply_adjustments


def main() -> None:
    df = pd.DataFrame(
        {
            "股票代码": ["AAPL", "TSLA", "0700.HK"],
            "持仓": [10, 5, 20],
            "当前价格": [180, 200, 300],
            "昨日收盘价": [175, 195, 295],
            "成本价": [120, 210, 260],
        }
    )
    df["总值"] = df["持仓"] * df["当前价格"]
    df["当日盈亏"] = (df["当前价格"] - df["昨日收盘价"]) * df["持仓"]
    df["总盈亏"] = (df["当前价格"] - df["成本价"]) * df["持仓"]

    adjustments = {"AAPL": 5, "TSLA": -2}
    simulated = apply_adjustments(df, adjustments)

    compare = pd.DataFrame(
        {
            "股票代码": df["股票代码"],
            "调整前总值": df["总值"],
            "调整后总值": simulated["总值"],
        }
    )

    fig = px.bar(compare.melt(id_vars="股票代码"), x="股票代码", y="value", color="variable")
    fig.update_layout(title="调仓前后总值对比", yaxis_title="总值")
    fig.show()


if __name__ == "__main__":
    main()
