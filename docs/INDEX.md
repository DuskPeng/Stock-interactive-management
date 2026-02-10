# 模块索引

本项目围绕“读取持仓数据、刷新行情、标签管理、持仓模拟、交互式分析”五大模块构建。

| 模块 | 说明 | 入口文件 |
| --- | --- | --- |
| 行情更新与XLSX读写 | 读取持仓XLSX并刷新市场字段（严格不覆盖人工列）。 | `portfolio_manager/data_io.py` |
| 行情数据源 | 定义可替换的数据源接口，支持yfinance与离线演示。 | `portfolio_manager/quotes.py` |
| 标签管理 | 为资产添加可编辑标签，并支持按标签聚合。 | `portfolio_manager/tags.py` |
| 持仓模拟 | 模拟调仓并输出调整后的收益与占比。 | `portfolio_manager/simulation.py` |
| 交互式网页 | Streamlit交互页面，支持标签编辑、目标仓位和前后对比。 | `portfolio_manager/webapp.py` |
| 正式运行脚本 | 在线更新 `portfolio.xlsx` 行情（一次/每日定时）。 | `run/data_update_runner.py` |

## 模块详细文档

- [行情更新与XLSX读写](modules/data_io.md)
- [行情数据源](modules/quotes.md)
- [标签管理](modules/tags.md)
- [持仓模拟](modules/simulation.md)
- [交互式网页](modules/webapp.md)
