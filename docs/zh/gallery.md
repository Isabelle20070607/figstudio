# Gallery

这个 Gallery 汇集了当前 beta 中一组小而完整、已纳入仓库的示例。每个示例都包含可运行的 Python 脚本、配套的 `.figstudio.json` FigureSpec，以及按该配置生成的 SVG 预览图。

在仓库根目录运行任一示例脚本，即可打开编辑器：

```powershell
uv run python examples/gallery/faceted_dose_response.py
```

配套的 FigureSpec 文件可以带到别处继续使用。它们保存变量名、列名、面板布局、筛选条件、选中项、参考线、注释和样式选择，但不保存原始数据。

## README 预览图

README 从这些仓库示例中选了三张预览图，让新用户在打开完整文档前就能看到可复现的实际效果：

| README 预览图 | 对应示例 | 选择原因 |
| --- | --- | --- |
| [Faceted dose response](../assets/gallery/faceted-dose-response.svg) | [脚本](../../examples/gallery/faceted_dose_response.py)、[spec](../../examples/gallery/faceted_dose_response.figstudio.json) | 展示从 DataFrame 分面、统计 recipe、参考线和论文版式到预览图的完整流程 |
| [Stacked bar sample composition](../assets/gallery/stacked-bar-sample-composition.svg) | [脚本](../../examples/gallery/stacked_bar_sample_composition.py)、[spec](../../examples/gallery/stacked_bar_sample_composition.figstudio.json) | 展示分组计数、导出前检查和紧凑的 `stacked_bar` recipe 工作流 |
| [Neuro ephys event rate](../assets/gallery/neuro-ephys-event-rate.svg) | [脚本](../../examples/gallery/neuro_ephys_event_rate.py)、[spec](../../examples/gallery/neuro_ephys_event_rate.figstudio.json) | 展示无需加载外部扩展包即可使用的内置实验性领域 recipe |

## 短 GIF 录制参考

这些示例不需要额外提交 GIF 文件。如果要为项目页面或发布材料录制短演示 GIF，可以从以下仓库示例开始：

| 演示内容 | 录制步骤 |
| --- | --- |
| 从数据到分面预览 | 启动 `examples/gallery/faceted_dose_response.py`，选择重复测量 DataFrame，渲染三面板预览，然后导出 SVG。 |
| 从 recipe 到导出文件 | 启动 `examples/gallery/stacked_bar_sample_composition.py`，检查 `stacked_bar` recipe 的字段映射，预览分组计数，然后导出 SVG。 |
| 领域 recipe 示例 | 启动 `examples/gallery/neuro_ephys_event_rate.py`，检查内置 neuro recipe，预览 mean/SEM event rate，然后导出 SVG。 |

## Faceted Dose Response

![Faceted dose response](../assets/gallery/faceted-dose-response.svg)

| 项目 | 说明 |
| --- | --- |
| 文件 | [脚本](../../examples/gallery/faceted_dose_response.py)、[spec](../../examples/gallery/faceted_dose_response.figstudio.json) |
| 展示内容 | DataFrame 分面筛选、`mean_sem_line` recipes、共享坐标轴、参考线、期刊双栏尺寸 |
| 数据结构 | 模拟重复测量 DataFrame，包含 `condition`、`replicate`、`time` 和 `response` 列 |
| 图形配置 | 三个面板按 `condition` 过滤同一个 `df`，并根据当前 DataFrame 的列生成纯 Matplotlib recipe 代码 |

## Stacked Bar Sample Composition

![Stacked bar sample composition](../assets/gallery/stacked-bar-sample-composition.svg)

| 项目 | 说明 |
| --- | --- |
| 文件 | [脚本](../../examples/gallery/stacked_bar_sample_composition.py)、[spec](../../examples/gallery/stacked_bar_sample_composition.figstudio.json) |
| 展示内容 | `stacked_bar` recipes、分组计数汇总、发布模式标签、SVG 导出前检查 |
| 数据结构 | 模拟样本 QC DataFrame，包含 `sample_id`、`stage` 和 `qc_status` 列 |
| 图形配置 | 一个 recipe 按 `stage` 和 `qc_status` 对当前 `df` 分组，将计数堆叠为 Matplotlib 柱状图，并能通过 SVG 导出校验 |

## Category Boxplot Response

![Category boxplot response](../assets/gallery/category-boxplot-response.svg)

| 项目 | 说明 |
| --- | --- |
| 文件 | [脚本](../../examples/gallery/category_boxplot_response.py)、[spec](../../examples/gallery/category_boxplot_response.figstudio.json) |
| 展示内容 | `boxplot_by_category` recipes、按组汇总分布、发布模式标签、SVG 导出前检查 |
| 数据结构 | 模拟响应 DataFrame，包含 `condition`、`genotype`、`replicate` 和 `response` 列 |
| 图形配置 | 一个 recipe 按 `condition` 和 `genotype` 对当前 `df` 的数值分组，按组错开 Matplotlib 箱线图，并让生成代码不依赖 FigStudio |

## Category Violin Response

![Category violin response](../assets/gallery/category-violin-response.svg)

| 项目 | 说明 |
| --- | --- |
| 文件 | [脚本](../../examples/gallery/category_violin_response.py)、[spec](../../examples/gallery/category_violin_response.figstudio.json) |
| 展示内容 | `violin_by_category` recipes、按组汇总分布、发布模式标签、SVG 导出前检查 |
| 数据结构 | 模拟响应 DataFrame，包含 `condition`、`genotype`、`replicate` 和 `response` 列 |
| 图形配置 | 一个 recipe 按 `condition` 和 `genotype` 对当前 `df` 的数值分组，按组错开 Matplotlib 小提琴图，并让生成代码不依赖 FigStudio |

## ECDF Response Distribution

![ECDF response distribution](../assets/gallery/ecdf-response-distribution.svg)

| 项目 | 说明 |
| --- | --- |
| 文件 | [脚本](../../examples/gallery/ecdf_response_distribution.py)、[spec](../../examples/gallery/ecdf_response_distribution.figstudio.json) |
| 展示内容 | `ecdf` recipes、分组经验累积分布、发布模式标签、SVG 导出前检查 |
| 数据结构 | 模拟响应延迟 DataFrame，包含 `cohort`、`sample_id` 和 `latency_ms` 列 |
| 图形配置 | 一个 recipe 在每个 `cohort` 内排序当前 `df` 的数值，绘制 Matplotlib 阶梯 ECDF 曲线，并让生成代码不依赖 FigStudio |

## Neuro Core Trial Response

![Neuro core trial response](../assets/gallery/neuro-core-trial-response.svg)

| 项目 | 说明 |
| --- | --- |
| 文件 | [脚本](../../examples/gallery/neuro_core_trial_response.py)、[spec](../../examples/gallery/neuro_core_trial_response.figstudio.json) |
| 展示内容 | 内置实验性 `neuro.core.trial_response_timecourse` recipe、分组汇总 trial 对齐响应、刺激开始参考线、SVG 导出前检查 |
| 数据结构 | 模拟 trial 对齐的神经科学 DataFrame，包含 `condition`、`trial_id`、`time_ms` 和 `response_z` 列 |
| 图形配置 | `neuro.core` 下的 recipe 按 `time` 和 `condition` 汇总当前 `df` 的 `response_z`，绘制 Matplotlib mean/SEM 时间曲线；无需加载外部扩展包，neuro 功能仍随主包提供 |

## Neuro Ephys Event Rate

![Neuro ephys event rate](../assets/gallery/neuro-ephys-event-rate.svg)

| 项目 | 说明 |
| --- | --- |
| 文件 | [脚本](../../examples/gallery/neuro_ephys_event_rate.py)、[spec](../../examples/gallery/neuro_ephys_event_rate.figstudio.json) |
| 展示内容 | 内置实验性 `neuro.ephys.event_rate_timecourse` recipe、分组汇总 event rate、发布模式标签、SVG 导出前检查 |
| 数据结构 | 模拟电生理 DataFrame，包含 `condition`、`unit_id`、`time_s` 和 `event_rate_hz` 列 |
| 图形配置 | `neuro.ephys` 下的 recipe 按 `time` 和 `condition` 汇总当前 `df` 的 `event_rate_hz`，绘制 Matplotlib mean/SEM 时间曲线，并说明这类 neuroscience recipe 可以随主包提供 |

## Secondary-Axis Timecourse

![Secondary-axis timecourse](../assets/gallery/secondary-axis-timecourse.svg)

| 项目 | 说明 |
| --- | --- |
| 文件 | [脚本](../../examples/gallery/secondary_axis_timecourse.py)、[spec](../../examples/gallery/secondary_axis_timecourse.figstudio.json) |
| 展示内容 | 左右 Y 轴叠加、合并图例、竖直参考线、箭头注释、适合导出的图形尺寸 |
| 数据结构 | 一个 DataFrame，包含对齐的 `time`、`fluorescence`、`event_rate` 和 `stimulus` 列 |
| 图形配置 | fluorescence 曲线使用左侧主轴，event rate 通过 `AxesSpec.secondary_y` 渲染到右侧 Y 轴 |

## Spanned Layout Signal Map

![Spanned layout signal map](../assets/gallery/spanned-layout-signal-map.svg)

| 项目 | 说明 |
| --- | --- |
| 文件 | [脚本](../../examples/gallery/spanned_layout_signal_map.py)、[spec](../../examples/gallery/spanned_layout_signal_map.figstudio.json) |
| 展示内容 | GridSpec 跨格布局、heatmap colorbar、按 mapping key 选择重复面板、注释、基线参考线 |
| 数据结构 | 共享 `time`、一个 `signal_map` 字典和一个二维 `spectral_power` 数组 |
| 图形配置 | 大 heatmap 跨两行，所选 mapping 项分别渲染成独立的曲线面板 |

## 验证

Gallery 示例由 `tests/test_gallery_examples.py` 覆盖。该测试会在不打开 editor 的情况下导入每个脚本、加载配套 spec、用脚本中的变量验证配置，并运行 Matplotlib 代码生成。
