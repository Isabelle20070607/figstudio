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
| `grouped_points` | 保留首次出现的 category 顺序，按 category 绘制 individual points，并叠加 mean 加 SEM 或 SD。 |
| `paired_before_after` | 按 subject 分组配对 observation，绘制 subject traces，并叠加 condition means。 |

Recipes 会把变量名、列名、样式选择和目标 axes 存进 `FigureSpec`，不会保存原始 DataFrame 数据。生成代码仍只 import Matplotlib，并从 live DataFrame 变量计算统计量。

可以运行 `examples/general_stats_recipe.py`，用 synthetic repeated-measures 数据试用三种内置 recipes。

## 发表级精修

准备论文或展示输出时使用 **Publish** mode。它会展示字体家族、constrained layout 等偏发表场景的控件，同时保持和 **Explore** mode 相同的 generated-code path。

右侧 polish panel 覆盖：

- figure size、DPI、标题、字体设置、内置 presets 和项目 style profile；
- panel layout rows、columns 和 presets；
- axes titles、labels、scales、limits、grid、legend 和 colorbar fallback；
- layer 和 recipe 的 target axes、labels、colors、markers、line styles、linewidths、alpha、colormap、histogram bins 和 fill alpha；
- 当前 axes 上的 text 和 arrow annotations。

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
