# 科研制图工作流

FigStudio 最适合数据工作已经完成、接下来需要把准备好的变量快速变成可复现 Matplotlib 图版的场景。

## Plot Layers

Plot layer 用于把 live variables 直接映射为视觉元素。

公开 beta 支持的 plot kind 包括 `line`、`scatter`、`bar`、`barh`、`hist`、`boxplot`、`violin`、`errorbar`、`heatmap`、`contour`、`step` 和 `fill_between`。

DataFrame 列通常使用同一个 DataFrame 作为 X 和 Y source，然后选择对应列。独立 array 或 list 可以让 X 使用 `index`，也可以选择另一个变量作为 X source。

`hist`、`boxplot`、`violin` 这类单值来源图使用 Y/value source；生成代码会忽略 X。`errorbar` 可以使用可选 Y error source。`heatmap` 和 `contour` 最适合二维 ndarray 或网格化 value。

## 统计 Recipes

当选中的变量是 pandas DataFrame，且你希望快速生成常见统计图而不手写绘图模板时，使用 recipe mode。

内置 recipes：

| Recipe | 适用场景 |
| --- | --- |
| `mean_sem_line` | 按 X 和可选 group 列分组，计算 mean 加 SEM 或 SD，再绘制带误差线的折线。 |
| `mean_sem_bar` | 按 X 和可选 group 列分组，计算 mean 加 SEM 或 SD，再绘制带误差帽的分类柱状图。 |
| `count_bar` | 按 X category 和可选 group 列统计行数，再绘制分类频数柱状图。 |
| `grouped_points` | 保留首次出现的 category 顺序，按 category 绘制 individual points，并叠加 mean 加 SEM 或 SD。 |
| `paired_before_after` | 按 subject 分组配对 observation，绘制 subject traces，并叠加 condition means。 |

Recipes 会把变量名、列名、样式选择和目标 axes 存进 `FigureSpec`，不会保存原始 DataFrame 数据。`count_bar` 只使用 X 和可选 group 列；value/error columns 会被忽略。生成代码仍只 import Matplotlib，并从 live DataFrame 变量计算统计量。

可以运行 `examples/general_stats_recipe.py`，用 synthetic repeated-measures 数据试用内置 recipes。

## Faceted Panels

当 plot layer 或 statistics recipe 基于 pandas DataFrame 时，可以在 Explore builder 中使用 **Facet panels**。选择 categorical DataFrame 列、panel 上限和 shared-axis options 后，FigStudio 会按首次出现的取值创建一个 axes，并把带 filter 的 layers 或 recipes 放到对应 axes 上。

Facet specs 仍保持 data-light。它们保存 `condition == "drug"` 这样的等值 filters、显示 labels、target axes 和 shared-axis flags，不保存 DataFrame rows。生成代码会先用 pandas 表达式过滤 live DataFrame 变量，再调用 Matplotlib。

对于普通 plot layer，同一组 repeated-panel controls 也支持 mapping 和 sequence source。Mapping source 会按可安全写成 Python literal 的 key 拆 panel，list 或 tuple 会按 item index 拆 panel。FigStudio 会保存 `DatasetRef.selection`，在绘图前从 live object 选出对应 item，并跳过与当前 layer 设置不兼容的候选。

Mapping 和 sequence repeated panels 的 v1 边界是：使用 index X 或独立 X variable，暂不支持 same-source selected X 或 Y-error channel。Statistics recipes 仍保持 DataFrame-only。

## Secondary Y-Axis Overlays

当两个相关指标需要共享同一个 panel 和 X scale 时，可以使用 secondary Y axis，例如 signal amplitude 加 event rate。先正常添加 primary plot layer，再添加 overlay layer，然后在 polish panel 中把该 layer 的 **Y axis** 控件设为 **Right**。

当前 axes 会提供右侧 label、scale 和 limits 控件。FigStudio 会在 overlay layer 上保存 `PlotLayer.y_axis: "right"`，并用 `AxesSpec.secondary_y` 保存右侧 axis 设置。生成代码会为该 panel 创建一个 Matplotlib `twinx()` axes；当 panel legend 启用时，会合并 primary 和 secondary legend entries。

第一个 beta slice 支持简单 overlay plot layers：`line`、`scatter`、`bar`、`hist`、`errorbar`、`step` 和 `fill_between`。Statistics recipes、reference lines、heatmaps、contours、horizontal bars、boxplots 和 violins 目前仍保留在 primary Y axis。

## 发表级精修

准备论文或展示输出时使用 **Publish** mode。它会展示字体家族、constrained layout 等偏发表场景的控件，同时保持和 **Explore** mode 相同的 generated-code path。

右侧 polish panel 覆盖：

- figure size、DPI、标题、字体设置、内置 presets 和项目 style profile；
- panel layout rows、columns、shared-axis options 和 presets；
- axes titles、labels、scales、limits、secondary Y-axis settings、grid、legend 和 colorbar fallback；
- layer 和 recipe 的 target axes、layer left/right Y-axis target、labels、colors、markers、line styles、linewidths、alpha、colormap、histogram bins 和 fill alpha；
- 用于 baselines、thresholds、cutoff markers 和 guide labels 的 horizontal/vertical reference lines；
- 当前 axes 上的 text 和 arrow annotations。

## Reference Lines

使用 **Reference lines** 在当前 axes 上添加 horizontal 或 vertical guide line。它适用于 baselines、thresholds、cutoff values，以及其他应独立于 plotted data 的跨领域常量。

Reference line 会把 orientation、numeric value、可选 legend label、color、line style、linewidth 和 alpha 存进 `FigureSpec`。生成代码使用 Matplotlib `axhline` 或 `axvline`，因此 previews、exports 和 saved code 走同一条路径。

## Annotations

使用 **Annotations** 给当前 axes 添加文本标签或箭头 callout。Annotation 坐标是所选 axes 的 data coordinates。

文本 annotation 生成 `annotate(text, xy=(x, y))`。箭头 annotation 还会设置 `xytext` 和 `arrowprops`。

## 已有 Matplotlib Figure

可以传入已有 Matplotlib `Figure`：

```python
figstudio.open(locals(), figure=fig)
```

公开 beta 会检查受支持的 line、scatter、image 和 bar artists，并在可提取足够数据时重建可编辑 generated layers。不支持的 artists 只作为 best-effort metadata，应视为只读上下文，而不是恢复出的源码。

Histograms、boxplots、violins、legends 和 colorbars 可能作为 metadata 暴露，除非当前 `FigureSpec` 模型能诚实复现它们。
