# 行情数据源模块

## 功能
- 抽象行情数据源接口，允许替换不同提供方。
- 内置 `YFinanceQuoteProvider`（在线）与 `FakeQuoteProvider`（离线演示）。

## 入口
- `portfolio_manager.quotes.QuoteProvider`
- `portfolio_manager.quotes.YFinanceQuoteProvider`
- `portfolio_manager.quotes.FakeQuoteProvider`

## 接口说明
### `QuoteProvider.fetch(codes)`
- 输入：股票代码列表
- 输出：`Dict[str, Quote]`

### `Quote`
- `code`: 股票代码
- `name`: 股票名称
- `current_price`: 当前价格
- `previous_close`: 昨日收盘价
- `change_pct`: 涨跌幅（小数形式）
- `timestamp`: 行情时间

## 依赖
- pandas
- yfinance（仅在线行情）

## 合规与声明
- yfinance 使用 Yahoo Finance 数据源，请遵循其服务条款与许可要求。
- 离线模式可用 `FakeQuoteProvider` 进行演示与测试。
