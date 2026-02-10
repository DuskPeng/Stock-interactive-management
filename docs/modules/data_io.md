# 行情更新与XLSX读写模块

## 功能
- 读取指定的XLSX文件，验证表头是否包含必要字段。
- 使用行情数据源刷新"名称"、"当前价格"、"昨日收盘价"、"涨跌幅"等字段。
- 自动计算"总值"、"当日盈亏"、"总盈亏"。
- **严格保护人工列**："股票代码"、"持仓"、"成本价" 不会被行情更新流程写入。
- 支持 `save_market_update`（仅写回行情字段）与 `save_with_tags`（行情+标签）两种保存策略。

## 入口
- `portfolio_manager.data_io.XlsxPortfolioIO`

## 接口说明
### `XlsxPortfolioIO.read()`
- 输入：无
- 输出：`pandas.DataFrame`

### `XlsxPortfolioIO.update_quotes(provider)`
- 输入：`QuoteProvider` 实例
- 输出：已更新行情字段并重算收益列的 `DataFrame`

### `XlsxPortfolioIO.save_market_update(df)`
- 输入：更新后的 `DataFrame`
- 行为：仅将市场可更新字段写回XLSX，不覆盖人工列。

### `XlsxPortfolioIO.save_with_tags(df)`
- 输入：更新后的 `DataFrame`
- 行为：在 `save_market_update` 基础上额外保存 `标签` 列。

## 依赖
- pandas
- openpyxl

## 注意事项
- 行情字段来源由 `QuoteProvider` 决定（见行情数据源模块）。
- 若表头缺失会抛出 `ValueError`。
