# 排错

FigStudio 会在渲染、保存或导出前校验常见问题。出现 issue card 时，优先从 preview 中的 issue card 开始。

## Validation Issues

点击 issue card。只要 API 提供了足够上下文，FigStudio 会选中受影响的 layer、recipe、axes 或 field。

常见 validation 问题：

| Issue | 修复方式 |
| --- | --- |
| 缺失变量或列 | 重新打开并确保变量在作用域内，或修改 layer/recipe mapping。 |
| Recipe source 不是 DataFrame | 切换为 pandas DataFrame 变量，或使用普通 plot layer。 |
| 缺失 target axes | Layout 改动后选择有效 target axes。 |
| 无效 layout geometry | 使用有效 panel preset，或修复重复 axes id、非正 span、越界 axes、重叠 axes。 |
| 维度不匹配 | 让 X、Y 和可选 Y error source 维度兼容。 |
| Heatmap 或 contour 缺少二维值 | 使用二维 ndarray 或 gridded value source。 |
| Log axis 上有非正数据 | 过滤数据、修改 limits，或切回 linear scale。 |
| 缺失 style profile | 选择可用 profile、恢复 `.figstudio/styles.json`，或接受 fallback defaults。 |

## Error Codes

| Code | 含义 |
| --- | --- |
| `validation_failed` | Spec 引用了缺失数据、无效 layout、不兼容维度、无效二维数据或 log-scale 非正数据。 |
| `render_failed` | 通过 validation 后，生成的 Matplotlib code 仍无法运行。 |
| `export_failed` | Export rendering 失败，或明确 output path 无法写入。 |
| `writeback_failed` | 受控 block 缺失、重复、嵌套、marker 不匹配，或使用了不同的 `block_id`。 |
| `writeback_io_failed` | Python 无法读取或写入目标脚本路径。 |

## Render 或 Export 失败

1. 先修复 validation issues。
2. 检查选中的变量是否仍存在于 live Python session。
3. 对 `heatmap` 和 `contour`，确认 value source 是二维。
4. 对导出到明确路径的情况，确认目录存在且可写。
5. 使用 generated code panel 查看实际 Matplotlib code path。

## Save Code 失败

确认：

- marker pair 与 session `block_id` 完全匹配；
- 只有一个 block 使用该 id；
- markers 没有嵌套；
- start 和 end markers 都存在；
- script path 可读可写。

生成代码仍会显示在 code panel 中，因此可以继续手动恢复。
