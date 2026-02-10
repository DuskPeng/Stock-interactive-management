# 交互式网页模块

## 功能
- 使用 Streamlit 构建交互式网页。
- 展示持仓表格、按标签聚合的交互图表（支持悬浮查看细节）。
- 提供标签编辑器：可在网页中直接修改各资产标签并保存回XLSX。
- 提供目标仓位比例编辑：输入目标占比后自动计算目标持仓与建议调仓数量。
- 支持手动叠加调仓数量，展示调仓前后总值/持仓变化（表格+图表）。
- 预留LLM分析建议入口。

## 入口
- `portfolio_manager.webapp.render_app`

## 运行方式
```bash
streamlit run portfolio_manager/webapp.py
```

## 依赖
- streamlit
- plotly
- pandas
