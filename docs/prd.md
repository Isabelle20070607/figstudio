# FigStudio PRD / 产品需求

## Product Definition / 产品定义

FigStudio is a local beta tool for turning data already present in a Python session into reproducible Matplotlib figures. The user stays in their normal script or notebook workflow, opens a browser editor, maps variables to plot layers, previews authoritative Matplotlib output, exports files, and saves generated OO code.

FigStudio 是一个本地 beta 工具，用来把 Python 会话中已有的数据转换成可复现的 Matplotlib 图。用户继续使用原本的脚本或 Notebook 流程，在浏览器编辑器里映射变量、创建图层、预览真实 Matplotlib 输出、导出文件，并保存生成的 OO 代码。

## Beta Scope / Beta 范围

- Launch from Python with `figstudio.open(locals(), ...)`.
- Inspect safe summaries of DataFrame, Series, ndarray, list, tuple, and existing Matplotlib Figure objects.
- Create and edit common plot layers: line, scatter, bar, barh, hist, boxplot, violin, errorbar, heatmap, contour, step, and fill_between.
- Configure figure size, DPI, font size/family, constrained layout, axes labels, scales, limits, grid, legend, colorbar, layer style, and simple subplot grids.
- Render previews and exports through Matplotlib Agg, not a front-end approximation.
- Save generated code to one unique controlled script block or return notebook replacement code.

- 通过 `figstudio.open(locals(), ...)` 从 Python 启动。
- 检查 DataFrame、Series、ndarray、list、tuple 和已有 Matplotlib Figure 的安全摘要。
- 创建和编辑常见图层：line、scatter、bar、barh、hist、boxplot、violin、errorbar、heatmap、contour、step、fill_between。
- 配置图尺寸、DPI、字体大小/字体族、constrained layout、坐标轴标签、缩放、范围、网格、图例、colorbar、图层样式和基础 subplot 网格。
- 用 Matplotlib Agg 生成预览和导出，而不是前端近似渲染。
- 将生成代码写入唯一受控脚本块，或返回 Notebook 替换代码。

## User Stories / 用户故事

- As a scientific Python user, I want to open an editor from `locals()` so I can reuse data I already prepared.
- As a researcher, I want GUI controls for data mapping and styling so I can iterate without memorizing every Matplotlib call.
- As a cautious script user, I want writeback limited to a marked block so my data-processing code is not changed.
- As a notebook user, I want replacement cell code instead of automatic notebook mutation.
- As a Matplotlib user, I want generated code that runs without importing FigStudio.

- 作为科研 Python 用户，我希望从 `locals()` 打开编辑器，以复用已经处理好的数据。
- 作为研究者，我希望用 GUI 映射数据和调整样式，而不必记住所有 Matplotlib API。
- 作为谨慎的脚本用户，我希望写回只发生在标记代码块里，不影响数据处理代码。
- 作为 Notebook 用户，我希望得到替换 cell 代码，而不是自动修改 notebook 文件。
- 作为 Matplotlib 用户，我希望生成代码不依赖 FigStudio 运行。

## Acceptance Criteria / 验收标准

- A script can launch FigStudio, create a DataFrame line plot, render a preview, and save code back into `# figstudio:start main` to `# figstudio:end main`.
- A notebook-style session without `script_path` returns complete replacement code.
- Generated code imports Matplotlib only and can run with the same user variables.
- Export downloads PNG, SVG, and PDF produced by Matplotlib.
- Render, export, and writeback failures return readable structured errors.
- Existing Figure inspection preserves line x/y data for editable generated layers.

- 脚本能启动 FigStudio，基于 DataFrame 创建折线图，渲染预览，并把代码写回 `# figstudio:start main` 到 `# figstudio:end main`。
- 不提供 `script_path` 的 Notebook 风格会话能返回完整替换代码。
- 生成代码只导入 Matplotlib，并能在相同用户变量下运行。
- PNG、SVG、PDF 导出来自 Matplotlib。
- 渲染、导出和写回失败会返回可读的结构化错误。
- existing Figure inspection 能保留线条的 x/y 数据，并生成可编辑图层。

## Out Of Scope / 非目标

- Cloud accounts, collaboration, or hosted dashboards.
- Automatic rewriting of arbitrary user Matplotlib source code.
- Direct notebook file mutation.
- Full support for every Matplotlib artist, 3D, polar plots, animation, or interactive web publishing.
- Public PyPI release for the local beta milestone.

- 云账号、协作或托管 dashboard。
- 自动重写任意用户手写 Matplotlib 源码。
- 直接修改 Notebook 文件。
- 完整支持所有 Matplotlib artist、3D、polar、动画或交互式 Web 发布。
- 本地 beta 里程碑不做公开 PyPI 发布。
