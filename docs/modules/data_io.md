# 行情更新与XLSX读写模块

## 功能
- 读取指定的XLSX文件，验证表头是否包含必要字段。
- 使用行情数据源刷新"名称"、"当前价格"、"昨日收盘价"、"涨跌幅"等字段。
- 自动计算"总值"、"当日盈亏"、"总盈亏"。
- **不会写入手动列**："股票代码"、"持仓"、"成本价"、"标签"。

## 入口
- `portfolio_manager.data_io.XlsxPortfolioIO`

## 接口说明
### `XlsxPortfolioIO.read()`
- 输入：无
- 输出：`pandas.DataFrame`

### `XlsxPortfolioIO.update_quotes(provider)`
- 输入：`QuoteProvider` 实例
- 输出：已更新行情字段的 `DataFrame`

### `XlsxPortfolioIO.save(df)`
- 输入：更新后的 `DataFrame`
- 行为：保留手动列并写回XLSX文件。

### `XlsxPortfolioIO.write_new(rows)`
- 输入：字典列表
- 行为：使用默认表头生成新的XLSX文件。

## 依赖
- pandas
- openpyxl

## 注意事项
- 行情字段来源由 `QuoteProvider` 决定（见行情数据源模块）。
- 若表头缺失会抛出 `ValueError`。
