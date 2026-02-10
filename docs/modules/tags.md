# 标签管理模块

## 功能
- 提供可编辑标签列（"标签"），支持多标签。
- 支持将标签拆分并用于分组统计。

## 入口
- `portfolio_manager.tags.TagManager`

## 接口说明
### `TagManager.normalize(raw)`
- 输入：原始字符串/空值
- 输出：标签列表

### `TagManager.set_tags(df, code, tags)`
- 输入：数据表、股票代码、标签列表
- 行为：设置对应股票代码的标签（逗号分隔）。

### `TagManager.explode_tags(df)`
- 输入：数据表
- 输出：每个标签独立成行的 `DataFrame`，方便聚合。

## 依赖
- pandas

## 数据格式建议
- 在XLSX中添加"标签"列，使用逗号分隔标签，例如：`美股,红利`。
