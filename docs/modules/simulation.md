# 持仓模拟模块

## 功能
- 支持对持仓进行假设性的增减并计算新的收益指标。
- 输出调整前后占比变化，辅助做调仓决策。

## 入口
- `portfolio_manager.simulation.apply_adjustments`
- `portfolio_manager.simulation.allocation_by_column`

## 接口说明
### `apply_adjustments(df, adjustments)`
- 输入：原始持仓 `DataFrame` 与调整字典 `{代码: 增减股数}`
- 输出：调整后的持仓 `DataFrame`

### `allocation_by_column(df, column)`
- 输入：带有分组列的数据表
- 输出：分组占比 `DataFrame`

## 依赖
- pandas
