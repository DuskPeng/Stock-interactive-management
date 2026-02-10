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
    return io.update_quotes(provider)


def _enrich_target_allocation(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare editable target-allocation table for UI."""

    total_value = df["总值"].sum()
    table = df[["股票代码", "名称", "持仓", "当前价格", "总值"]].copy()
    table["当前占比(%)"] = (table["总值"] / total_value * 100) if total_value else 0
    table["目标占比(%)"] = table["当前占比(%)"]
    return table


def _calc_target_shares(df: pd.DataFrame, edited_target: pd.DataFrame) -> pd.DataFrame:
    """Calculate target shares and deltas from target allocation percentages."""

    total_value = df["总值"].sum()
    merged = edited_target.copy()
    merged["目标占比(%)"] = merged["目标占比(%)"].clip(lower=0)
    target_total = merged["目标占比(%)"].sum()

    # 若用户输入的总占比不等于100，按比例归一化，避免误操作导致不可解释结果。
    if target_total > 0:
        merged["目标占比(%)"] = merged["目标占比(%)"] / target_total * 100

    merged["目标总值"] = total_value * merged["目标占比(%)"] / 100
    merged["目标持仓"] = (merged["目标总值"] / merged["当前价格"].replace(0, pd.NA)).fillna(0)
    merged["调整数量"] = merged["目标持仓"] - merged["持仓"]
    return merged


def render_app() -> None:
    """Render the Streamlit application."""

    st.set_page_config(page_title="Portfolio Manager", layout="wide")
    st.title("持仓管理与模拟分析")

    st.sidebar.header("数据来源")
    file_path = st.sidebar.text_input("XLSX文件路径", value="portfolio.xlsx")
    use_demo = st.sidebar.checkbox("使用演示行情 (无需联网)", value=True)
    refresh = st.sidebar.button("刷新行情")

    if refresh:
        st.rerun()

    path = Path(file_path)
    if not path.exists():
        st.warning("找不到文件，请先准备好XLSX持仓文件。")
        return

    io = XlsxPortfolioIO(path)
    df = _load_portfolio(path, use_demo)
    tag_manager = TagManager()

    st.subheader("当前持仓")
    st.dataframe(df, use_container_width=True)

    st.subheader("标签编辑（可交互修改）")
    tag_editor = df[["股票代码", "名称"]].copy()
    if TAG_COLUMN in df.columns:
        tag_editor[TAG_COLUMN] = df[TAG_COLUMN].fillna("")
    else:
        tag_editor[TAG_COLUMN] = ""

    edited_tags = st.data_editor(
        tag_editor,
        use_container_width=True,
        column_config={TAG_COLUMN: st.column_config.TextColumn(help="多个标签请用逗号分隔，如：美股,红利")},
        key="tag_editor",
    )
    if st.button("保存标签到XLSX"):
        df_with_tags = df.copy()
        df_with_tags[TAG_COLUMN] = edited_tags[TAG_COLUMN]
        io.save_with_tags(df_with_tags)
        st.success("标签已保存到XLSX文件。")

    exploded = tag_manager.explode_tags(edited_tags.rename(columns={"名称": "名称_tmp"}).join(df[["总值"]]))
    if TAG_COLUMN in exploded.columns:
        tag_alloc = allocation_by_column(exploded, TAG_COLUMN)
        fig_tag = px.sunburst(
            tag_alloc,
            path=[TAG_COLUMN],
            values="总值",
            title="按标签分组的持仓占比（交互式）",
        )
        st.plotly_chart(fig_tag, use_container_width=True)

    st.subheader("目标仓位比例与模拟调仓")
    st.markdown("设置每个资产的目标占比，自动计算建议调仓数量，并展示调仓前后对比。")

    target_table = _enrich_target_allocation(df)
    edited_target = st.data_editor(
        target_table,
        use_container_width=True,
        disabled=["股票代码", "名称", "持仓", "当前价格", "总值", "当前占比(%)"],
        key="target_editor",
    )

    target_plan = _calc_target_shares(df, edited_target)
    st.dataframe(target_plan[["股票代码", "当前占比(%)", "目标占比(%)", "目标持仓", "调整数量"]], use_container_width=True)

    manual_adjustments = st.data_editor(
        df[["股票代码", "持仓"]].assign(调整数量=0.0),
        use_container_width=True,
        key="manual_adjust_editor",
    )

    auto_adjust = {
        row["股票代码"]: float(row["调整数量"])
        for _, row in target_plan.iterrows()
        if abs(float(row["调整数量"])) > 1e-9
    }
    extra_adjust = {
        row["股票代码"]: float(row["调整数量"])
        for _, row in manual_adjustments.iterrows()
        if abs(float(row["调整数量"])) > 1e-9
    }

    combined = auto_adjust.copy()
    for code, delta in extra_adjust.items():
        combined[code] = combined.get(code, 0.0) + delta

    simulated = apply_adjustments(df, combined)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("调整前总值", f"{df['总值'].sum():,.2f}")
    with col2:
        st.metric("调整后总值", f"{simulated['总值'].sum():,.2f}")

    compare = pd.DataFrame(
        {
            "股票代码": df["股票代码"],
            "调整前总值": df["总值"],
            "调整后总值": simulated["总值"],
            "调整前持仓": df["持仓"],
            "调整后持仓": simulated["持仓"],
        }
    )
    st.dataframe(compare, use_container_width=True)

    fig_compare = px.bar(
        compare.melt(id_vars="股票代码", value_vars=["调整前总值", "调整后总值"]),
        x="股票代码",
        y="value",
        color="variable",
        barmode="group",
        title="调仓前后总值对比",
    )
    st.plotly_chart(fig_compare, use_container_width=True)

    st.subheader("LLM分析建议入口")
    st.text_area("预留给LLM的提示词", height=120, placeholder="可在此拼接当前持仓、标签、目标仓位与模拟结果，提交至LLM接口。")
    st.info("后续可在此处接入LLM API，实现基于当前与模拟持仓的自动分析建议。")


if __name__ == "__main__":
    render_app()
