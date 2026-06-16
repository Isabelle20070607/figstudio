# FigStudio User Guide / 用户指南

This guide explains the public beta workflow for people using FigStudio to build Matplotlib figures from data already available in a Python process.

本指南说明公开 beta 阶段的使用流程，面向已经在 Python 进程中准备好数据、希望用 FigStudio 制作 Matplotlib 图形的用户。

## Before Opening the Editor / 打开编辑器前

Prepare data first, then open FigStudio from the same scope. The editor can summarize public variables from `locals()` when they are DataFrames, Series, ndarrays, lists, tuples, or Matplotlib Figures.

先完成数据准备，再从同一作用域打开 FigStudio。编辑器会摘要展示 `locals()` 中的公开变量，支持 DataFrame、Series、ndarray、list、tuple 和 Matplotlib Figure。

Private variables whose names start with `_` are not shown. The UI receives summaries; live Python objects stay in the local Python server.

以下划线 `_` 开头的私有变量不会显示。UI 收到的是摘要；真实 Python 对象保留在本地 Python server 中。

## Script Workflow / 脚本工作流

Add a controlled block where generated plotting code should live:

在希望生成绘图代码的位置加入受控代码块：

```python
import figstudio

# data processing above this line
session = figstudio.open(locals(), script_path=__file__, block_id="main")

# figstudio:start main
# figstudio:end main
```

After editing the figure, click **Save code**. FigStudio replaces only the code between `# figstudio:start main` and `# figstudio:end main`. Data loading, cleaning, modeling, and other code outside the markers is not modified.

编辑图形后点击 **Save code**。FigStudio 只替换 `# figstudio:start main` 和 `# figstudio:end main` 之间的代码。marker 外的数据读取、清洗、建模和其他代码不会被修改。

Use a different `block_id` when one script contains multiple FigStudio-controlled figures:

如果一个脚本中有多个 FigStudio 受控图，可以使用不同的 `block_id`：

```python
figstudio.open(locals(), script_path=__file__, block_id="summary")

# figstudio:start summary
# figstudio:end summary
```

## Notebook Workflow / Notebook 工作流

Notebook sessions should omit `script_path`:

Notebook 会话应省略 `script_path`：

```python
import figstudio

session = figstudio.open(locals())
```

The editor still maps data, renders previews, exports files, and generates code. **Save code** returns replacement cell code in the response and code panel instead of mutating the notebook file.

编辑器仍可映射数据、渲染预览、导出文件并生成代码。**Save code** 会在响应和代码面板中返回替换 cell 代码，而不会直接修改 notebook 文件。

## Editor Areas / 编辑器区域

- Left: variables and layer creation.
- Center: Matplotlib preview, validation messages, export controls, and generated code.
- Right: figure, axes, subplot, annotation, and layer controls.

- 左侧：变量和图层创建。
- 中间：Matplotlib 预览、校验消息、导出控件和生成代码。
- 右侧：图、坐标轴、subplot、注释和图层控件。

Use **Explore** mode for everyday figure assembly and **Publish** mode for publication-oriented controls such as preset sizes, DPI, font family, font size, and constrained layout.

日常组图使用 **Explore** 模式；需要论文或展示输出时使用 **Publish** 模式，以配置预设尺寸、DPI、字体、字号和 constrained layout。

## Mapping Data / 映射数据

Use **Variables** to choose source data and **Create layer** to map channels.

使用 **Variables** 选择数据源，并在 **Create layer** 中映射通道。

- DataFrame columns: choose the same DataFrame for X and Y, then select columns.
- Independent arrays or lists: choose `index` for X or choose another variable as the X source.
- Single-value-source plots: `hist`, `boxplot`, and `violin` use the Y/value source; the X source is ignored by generated code.
- Error bars: choose `errorbar`, then select an optional Y error source.
- Heatmap and contour: use a 2D ndarray or a gridded value source when possible.

- DataFrame 列：X 和 Y 选择同一个 DataFrame，再选择列。
- 独立数组或列表：X 可以选择 `index`，也可以选择另一个变量作为 X source。
- 单值来源图：`hist`、`boxplot` 和 `violin` 使用 Y/value source；生成代码会忽略 X source。
- Error bars：选择 `errorbar`，再按需选择 Y error source。
- Heatmap 和 contour：尽量使用 2D ndarray 或网格化 value source。

Supported public beta plot types are `line`, `scatter`, `bar`, `barh`, `hist`, `boxplot`, `violin`, `errorbar`, `heatmap`, `contour`, `step`, and `fill_between`.

公开 beta 支持的图层类型包括 `line`、`scatter`、`bar`、`barh`、`hist`、`boxplot`、`violin`、`errorbar`、`heatmap`、`contour`、`step` 和 `fill_between`。

## Editing Figures / 编辑图形

The figure inspector controls size, DPI, rows, columns, title, font settings, and style preset. Rows and columns create a simple subplot grid with axes ids such as `ax0`, `ax1`, and `ax2`.

Figure inspector 控制图尺寸、DPI、行数、列数、总标题、字体设置和样式预设。行数和列数会创建基础 subplot 网格，坐标轴 id 形如 `ax0`、`ax1`、`ax2`。

The axes inspector controls title, axis labels, scales, limits, grid, legend, and contour colorbar. Log-scaled axes are validated before rendering so non-positive data can be fixed before Matplotlib fails.

Axes inspector 控制标题、坐标轴标签、缩放、范围、网格、图例和 contour colorbar。log 坐标轴会在渲染前校验，便于在 Matplotlib 报错前修复非正数据。

Layer controls can change the target axes, plot type, label, color, marker, line style, line width, alpha, colormap, histogram bins, and fill alpha where those options apply.

Layer controls 可在适用时调整目标坐标轴、图层类型、标签、颜色、marker、线型、线宽、透明度、colormap、histogram bins 和 fill alpha。

## Annotations / 注释

Use **Annotations** in the inspector to add text labels or arrow callouts to the active axes. Text annotations generate `annotate(text, xy=(x, y))`; arrow annotations also set `xytext` and `arrowprops`.

在 inspector 的 **Annotations** 区域可以给当前 axes 添加文本标签或箭头 callout。文本注释会生成 `annotate(text, xy=(x, y))`；箭头注释还会设置 `xytext` 和 `arrowprops`。

Annotation coordinates are data coordinates on the selected axes.

注释坐标是所选 axes 上的数据坐标。

## Existing Matplotlib Figures / 已有 Matplotlib Figure

You can pass an existing Matplotlib `Figure`:

可以传入已有 Matplotlib `Figure`：

```python
figstudio.open(locals(), figure=fig)
```

The public beta inspects supported line, scatter, image, and bar artists and recreates editable generated layers. Unsupported artists remain best-effort metadata and should be treated as read-only context, not as recovered source code.

公开 beta 会检查受支持的 line、scatter、image 和 bar artist，并重建可编辑的生成图层。不支持的 artist 只作为 best-effort metadata，应视为只读上下文，而不是恢复出的源码。

## FigureSpec Import and Export / FigureSpec 导入导出

Use the FigureSpec import/export buttons in the top toolbar to save or restore a `.figstudio.json` GUI session. A FigureSpec stores the editor state, not the original data.

使用顶部工具栏里的 FigureSpec 导入/导出按钮，可以保存或恢复 `.figstudio.json` GUI 会话。FigureSpec 保存的是编辑器状态，不保存原始数据。

Python helpers are also available:

也可以使用 Python helper：

```python
figstudio.save_spec(session.spec, "figure.figstudio.json")
spec = figstudio.load_spec("figure.figstudio.json")
```

Reusing a spec requires the new Python session to provide variables with names and shapes compatible with the spec.

复用 spec 时，新的 Python 会话需要提供与 spec 兼容的变量名和数据形状。

## Exporting Figures / 导出图形

Use the PNG, SVG, or PDF buttons in the preview toolbar. Exports are generated by Matplotlib Agg from the current `FigureSpec`, so exported files match the generated Matplotlib code path rather than a browser approximation.

使用预览工具栏里的 PNG、SVG 或 PDF 按钮。导出由 Matplotlib Agg 根据当前 `FigureSpec` 生成，因此导出文件对应生成 Matplotlib 代码路径，而不是浏览器近似渲染。

When using the API directly, `/api/export` can either return base64 data or write to an explicit `output_path`.

直接使用 API 时，`/api/export` 可以返回 base64 data，也可以写入明确指定的 `output_path`。

## Validation / 校验

Before rendering, FigStudio checks common failures:

渲染前，FigStudio 会检查常见错误：

- missing variables or DataFrame columns;
- layers targeting missing axes;
- X/Y/Y error dimension mismatches;
- heatmap or contour layers without 2D value data;
- non-positive data on log-scaled axes.

- 缺失变量或 DataFrame 列；
- 图层指向不存在的 axes；
- X/Y/Y error 维度不匹配；
- heatmap 或 contour 缺少二维 value 数据；
- log 坐标轴上存在非正数据。

Fix validation errors in the editor before rendering, saving, or exporting.

在渲染、保存或导出前，需要先在编辑器中修复 validation error。

## Common Errors / 常见错误

- `validation_failed`: the spec references missing data, missing axes, incompatible dimensions, invalid 2D data, or non-positive log-scale data.
- `render_failed`: generated Matplotlib code could not run after validation.
- `export_failed`: export rendering failed or an explicit output path could not be written.
- `writeback_failed`: the controlled block was missing, duplicated, nested, had unmatched markers, or used a different `block_id`.
- `writeback_io_failed`: Python could not read or write the target script path.

- `validation_failed`：spec 引用了缺失数据、缺失 axes、不兼容维度、无效二维数据，或 log 坐标轴上的非正数据。
- `render_failed`：通过校验后，生成的 Matplotlib 代码仍无法运行。
- `export_failed`：导出渲染失败，或明确指定的 output path 无法写入。
- `writeback_failed`：受控代码块缺失、重复、嵌套、marker 不匹配，或 `block_id` 不一致。
- `writeback_io_failed`：Python 无法读取或写入目标脚本路径。

## Recovery / 恢复方式

If validation or render fails, adjust the layer source mapping first. If writeback fails, verify the marker pair exactly matches the session `block_id` and that only one block uses that id. Generated code is still shown in the code panel, so script or notebook work can continue manually.

如果校验或渲染失败，先调整图层数据映射。如果写回失败，确认 marker pair 与 session `block_id` 完全匹配，并且只有一个代码块使用该 id。代码面板仍会显示生成代码，因此脚本或 Notebook 工作可以继续手动进行。
