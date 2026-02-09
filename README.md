# Stock-interactive-management

一个用于管理与分析持仓的Python项目，支持XLSX持仓表更新、标签管理、调仓模拟与交互式网页展示。

## 功能概览
1. 读取XLSX并刷新行情数据（保护手动列）。
2. 标签管理与按标签聚合。
3. 调仓模拟与收益对比。
4. Streamlit交互式网页，可视化与LLM入口。

## 项目结构
```
portfolio_manager/    核心业务代码
examples/             模块示例与可视化
docs/                 模块文档与索引
```

## 安装依赖
```bash
pip install -r requirements.txt
```

## 快速开始
### 1. 准备XLSX持仓表
表头需包含：
```
股票代码  名称  持仓  当前价格  昨日收盘价  涨跌幅  成本价  总值  当日盈亏  总盈亏
```
可手动新增 `标签` 列用于标签管理。

### 2. 更新行情
```python
from portfolio_manager.data_io import XlsxPortfolioIO
from portfolio_manager.quotes import YFinanceQuoteProvider

io = XlsxPortfolioIO("portfolio.xlsx")
df = io.update_quotes(YFinanceQuoteProvider())
io.save(df)
```

### 3. 运行网页
```bash
streamlit run portfolio_manager/webapp.py
```

## 文档
详见 [docs/INDEX.md](docs/INDEX.md)。
