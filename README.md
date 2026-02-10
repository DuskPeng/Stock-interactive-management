# Stock-interactive-management

一个用于管理与分析持仓的Python项目，支持XLSX持仓表更新、标签管理、调仓模拟与交互式网页展示。

## 功能概览
1. 读取XLSX并刷新行情数据（严格保护人工列：`股票代码/持仓/成本价`）。
2. 标签管理与按标签聚合，可在Web页面交互式编辑标签并保存。
3. 目标仓位比例+调仓模拟，支持前后对比与交互图表。
4. Streamlit交互式网页，预留LLM分析入口。
5. 正式运行脚本支持一次更新/每日定时更新 `portfolio.xlsx`。

## 项目结构
```
portfolio_manager/    核心业务代码
run/                  正式运行脚本（数据更新）
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

### 2. 正式运行：在线更新行情（不改人工列）
```bash
python run/data_update_runner.py --file portfolio.xlsx --mode once
```
每日定时更新：
```bash
python run/data_update_runner.py --file portfolio.xlsx --mode daemon --time 15:30
```

### 3. 运行网页
```bash
streamlit run portfolio_manager/webapp.py
```

## 文档
详见 [docs/INDEX.md](docs/INDEX.md)。
