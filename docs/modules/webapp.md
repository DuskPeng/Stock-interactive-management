# 交互式网页模块

## 功能
- 使用 Streamlit 构建交互式网页。
- 展示持仓表格、按标签聚合的饼图。
- 提供调仓模拟输入并展示调整前后总值对比。
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
