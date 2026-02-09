"""Streamlit web app for interactive portfolio management."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from portfolio_manager.data_io import XlsxPortfolioIO
from portfolio_manager.quotes import FakeQuoteProvider, YFinanceQuoteProvider
from portfolio_manager.simulation import allocation_by_column, apply_adjustments
from portfolio_manager.tags import TAG_COLUMN, TagManager


def _load_portfolio(file_path: Path, use_demo: bool) -> pd.DataFrame:
    provider = FakeQuoteProvider() if use_demo else YFinanceQuoteProvider()
    io = XlsxPortfolioIO(file_path)
    df = io.update_quotes(provider)
    return df


def render_app() -> None:
    """Render the Streamlit application."""

    st.set_page_config(page_title="Portfolio Manager", layout="wide")
    st.title("持仓管理与模拟分析")

    st.sidebar.header("数据来源")
    file_path = st.sidebar.text_input("XLSX文件路径", value="portfolio.xlsx")
    use_demo = st.sidebar.checkbox("使用演示行情 (无需联网)", value=True)
    refresh = st.sidebar.button("刷新行情")

    if refresh:
        st.experimental_rerun()

    path = Path(file_path)
    if not path.exists():
        st.warning("找不到文件，请先准备好XLSX持仓文件。")
        return

    df = _load_portfolio(path, use_demo)

    st.subheader("当前持仓")
    st.dataframe(df, use_container_width=True)

    if TAG_COLUMN in df.columns:
        tag_manager = TagManager()
        exploded = tag_manager.explode_tags(df)
        tag_alloc = allocation_by_column(exploded, TAG_COLUMN)
        fig = px.pie(tag_alloc, names=TAG_COLUMN, values="总值", title="按标签分组的持仓占比")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("未检测到'标签'列，可在XLSX中手动添加并填写标签。")

    st.subheader("模拟调整")
    st.markdown("输入调整后的持仓数量（增减股数），并查看调整前后的对比。")
    simulation_df = df[["股票代码", "持仓"]].copy()
    simulation_df["调整数量"] = 0
    edited = st.data_editor(simulation_df, use_container_width=True)

    adjustments = {
        row["股票代码"]: row["调整数量"] for _, row in edited.iterrows() if row["调整数量"]
    }
    simulated = apply_adjustments(df, adjustments)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**调整前总值**")
        st.metric("总值", f"{df['总值'].sum():,.2f}")
    with col2:
        st.markdown("**调整后总值**")
        st.metric("总值", f"{simulated['总值'].sum():,.2f}")

    compare = pd.DataFrame(
        {
            "股票代码": df["股票代码"],
            "调整前总值": df["总值"],
            "调整后总值": simulated["总值"],
        }
    )
    st.dataframe(compare, use_container_width=True)

    st.subheader("LLM分析建议入口")
    st.text_area("预留给LLM的提示词", height=120)
    st.info("此处可接入LLM服务，输入当前持仓与模拟结果后生成建议。")


if __name__ == "__main__":
    render_app()
