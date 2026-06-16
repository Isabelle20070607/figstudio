# FigStudio PRD / 产品需求

## Product Definition / 产品定义

FigStudio is a public beta tool for turning data already present in a Python session into reproducible Matplotlib figures. Users install the Python package, open a local browser editor from a script or notebook, map variables to plot layers, preview authoritative Matplotlib output, export files, save generated OO code, and optionally save the GUI session as a portable `FigureSpec` JSON file.

FigStudio 是一个公开 beta 工具，用来把 Python 会话中已有的数据转换成可复现的 Matplotlib 图。用户安装 Python 包后，可从脚本或 Notebook 打开本地浏览器编辑器，映射变量、创建图层、预览真实 Matplotlib 输出、导出文件、保存生成的 OO 代码，并可把 GUI 会话保存成可移植的 `FigureSpec` JSON 文件。

## Target Users / 目标用户

- Scientific Python users who prepare data in scripts or notebooks and want faster Matplotlib figure assembly.
- Researchers who need publication-style figures with reproducible Python output.
- Cautious Matplotlib users who want GUI help without losing control of generated code.
- Package users who expect the editor UI to work from a wheel without installing frontend tooling.

- 已经在脚本或 Notebook 中准备数据、希望更快组装 Matplotlib 图的 Scientific Python 用户。
- 需要发表风格图形且要求 Python 输出可复现的研究者。
- 希望使用 GUI 辅助但仍保留生成代码控制权的谨慎 Matplotlib 用户。
- 希望 wheel 安装后无需前端工具即可使用编辑器 UI 的 package 用户。

## Beta Scope / Beta 范围

- Install from a Python package and run without Node/npm at runtime.
- Launch from Python with `figstudio.open(locals(), ...)` or from `figstudio demo`.
- Inspect safe summaries of DataFrame, Series, ndarray, list, tuple, and existing Matplotlib Figure objects.
- Create and edit common plot layers: line, scatter, bar, barh, hist, boxplot, violin, errorbar, heatmap, contour, step, and fill_between.
- Configure figure size, DPI, manuscript presets, font size/family, constrained layout, axes labels, scales, limits, grid, legend, colorbar, layer style, simple subplot grids, and text/arrow annotations.
- Render previews and exports through Matplotlib Agg, not a front-end approximation.
- Validate missing data, missing columns, missing axes, shape mismatches, 2D heatmap/contour requirements, and log-scale non-positive data before render.
- Save generated code to one unique controlled script block or return notebook replacement code.
- Import and export `.figstudio.json` session specs.

- 可通过 Python package 安装，运行时不需要 Node/npm。
- 通过 `figstudio.open(locals(), ...)` 或 `figstudio demo` 启动。
- 检查 DataFrame、Series、ndarray、list、tuple 和已有 Matplotlib Figure 的安全摘要。
- 创建和编辑常见图层：line、scatter、bar、barh、hist、boxplot、violin、errorbar、heatmap、contour、step、fill_between。
- 配置图尺寸、DPI、论文样式预设、字号/字体、constrained layout、坐标轴标签、缩放、范围、网格、图例、colorbar、图层样式、基础 subplot 网格和文本/箭头注释。
- 用 Matplotlib Agg 生成预览和导出，而不是前端近似渲染。
- 在渲染前校验缺失数据、缺失列、缺失 axes、维度不匹配、heatmap/contour 的二维数据要求，以及 log 坐标轴的非正数据。
- 将生成代码写入唯一受控脚本块，或返回 Notebook 替换代码。
- 导入和导出 `.figstudio.json` 会话 spec。

## User Stories / 用户故事

- As a scientific Python user, I want to open an editor from `locals()` so I can reuse data I already prepared.
- As a researcher, I want manuscript presets and annotation controls so I can prepare publication-style figures faster.
- As a cautious script user, I want writeback limited to a marked block so my data-processing code is not changed.
- As a notebook user, I want replacement cell code instead of automatic notebook mutation.
- As a Matplotlib user, I want generated code that runs without importing FigStudio.
- As a package user, I want `pip install figstudio` to include the editor UI without extra frontend build steps.
- As a returning user, I want FigureSpec JSON import/export so I can continue a GUI editing session later with compatible data.

- 作为科研 Python 用户，我希望从 `locals()` 打开编辑器，以复用已经处理好的数据。
- 作为研究者，我希望使用论文样式预设和注释控件，更快准备发表风格图形。
- 作为谨慎的脚本用户，我希望写回只发生在标记代码块里，不影响数据处理代码。
- 作为 Notebook 用户，我希望得到替换 cell 代码，而不是自动修改 notebook 文件。
- 作为 Matplotlib 用户，我希望生成代码不依赖 FigStudio 运行。
- 作为 package 用户，我希望 `pip install figstudio` 后就包含编辑器 UI，不需要额外构建前端。
- 作为回访用户，我希望通过 FigureSpec JSON 导入导出，在兼容数据下继续 GUI 编辑会话。

## Acceptance Criteria / 验收标准

- A script can launch FigStudio, create a DataFrame line plot, render a preview, and save code back into `# figstudio:start main` to `# figstudio:end main`.
- A notebook-style session without `script_path` returns complete replacement code.
- Generated code imports Matplotlib only and can run with the same user variables.
- Export downloads PNG, SVG, and PDF produced by Matplotlib.
- Render, export, validation, and writeback failures return readable structured errors.
- Existing Figure inspection preserves supported line, scatter, image, and bar data as editable generated layers.
- A built wheel includes the React editor and serves it from `127.0.0.1` after clean install.
- `figstudio.load_spec()` and `figstudio.save_spec()` round-trip a `.figstudio.json` file.
- Development docs explain how to add plot kinds, update API contracts, run tests, and verify package assets.

- 脚本能启动 FigStudio，基于 DataFrame 创建折线图，渲染预览，并把代码写回 `# figstudio:start main` 到 `# figstudio:end main`。
- 不提供 `script_path` 的 Notebook 风格会话能返回完整替换代码。
- 生成代码只 import Matplotlib，并能在相同用户变量下运行。
- PNG、SVG、PDF 导出来自 Matplotlib。
- render、export、validation 和 writeback 失败会返回可读的结构化错误。
- existing Figure inspection 能把受支持的 line、scatter、image、bar 数据保留为可编辑图层。
- 构建后的 wheel 包含 React 编辑器，干净安装后可从 `127.0.0.1` 提供完整 UI。
- `figstudio.load_spec()` 和 `figstudio.save_spec()` 能往返保存 `.figstudio.json` 文件。
- 开发文档说明如何新增图层类型、更新 API 契约、运行测试并验证 package assets。

## Out Of Scope / 非目标

- Cloud accounts, collaboration, or hosted dashboards.
- Automatic rewriting of arbitrary user Matplotlib source code.
- Direct notebook file mutation.
- Full support for every Matplotlib artist, 3D, polar plots, animation, or interactive web publishing.
- Domain-specific recipe plugins beyond stable extension points.
- Desktop installers for the public beta.

- 云账号、协作或托管 dashboard。
- 自动重写任意用户手写 Matplotlib 源码。
- 直接修改 Notebook 文件。
- 完整支持所有 Matplotlib artist、3D、polar、动画或交互式 Web 发布。
- 稳定扩展点之外的领域 recipe 插件。
- 公开 beta 阶段的桌面安装器。

## Product Quality Bar / 产品质量门槛

- The editor must stay local-first and bind the server to `127.0.0.1` by default.
- Generated plotting code must stay understandable Matplotlib OO code.
- Writeback must fail closed when the controlled block cannot be identified safely.
- Docs must separate current beta behavior from future roadmap items.

- 编辑器必须保持 local-first，并默认把 server 绑定到 `127.0.0.1`。
- 生成绘图代码必须保持为易读的 Matplotlib OO code。
- 当无法安全识别受控代码块时，写回必须失败而不是猜测修改。
- 文档必须区分当前 beta 行为和未来路线图事项。
