# FigStudio

FigStudio is a local figure-workflow tool for reproducible, publication-ready Matplotlib figure panels. It is built for scientific Python users who already have data in a script or notebook and want a faster way to create plot layers, add common statistics recipes, style panels, preview, export, and save readable Matplotlib OO code.

FigStudio 是一个本地 figure-workflow 工具，用于制作可复现、适合发表的 Matplotlib 图版。它面向已经在脚本或 Notebook 中完成数据处理的科研 Python 用户，用 GUI 快速创建图层、添加常见统计 recipe、调整图版、预览、导出并保存可读的 Matplotlib OO 代码。

## Install / 安装

```powershell
pip install figstudio
```

The package wheel includes the built React editor. End users do not need Node, npm, Vite, or the frontend source tree after installation.

wheel 包含构建后的 React 编辑器。普通用户安装后不需要 Node、npm、Vite，也不需要前端源码目录。

## Quick Start / 快速开始

Add FigStudio after data preparation and give it one controlled code block:

在数据处理完成后调用 FigStudio，并提供一个受控代码块：

```python
import figstudio

# Finish data processing first.
session = figstudio.open(locals(), script_path=__file__, block_id="main")

# figstudio:start main
# figstudio:end main
```

Open the editor, create or edit layers, then click **Save code**. FigStudio replaces only the code between the matching markers.

打开编辑器，创建或调整图层，然后点击 **Save code**。FigStudio 只替换匹配 marker 中间的代码。

Run the demo:

运行 demo：

```powershell
figstudio demo
```

For notebook-style use, omit `script_path`; **Save code** returns replacement cell code instead of editing notebook files.

Notebook 风格使用时不要传 `script_path`；点击 **Save code** 会返回替换 cell 代码，不会直接修改 Notebook 文件。

## Development / 开发

Backend tests:

后端测试：

```powershell
uv run --extra dev pytest
```

Frontend development:

前端开发：

```powershell
cd frontend
npm install
npm run build
npm run dev
```

Build a publishable package:

构建可发布包：

```powershell
uv build
```

The build hook runs `npm ci`, builds the frontend, and bundles the output into the Python wheel. See the developer guide for feature work and release checks.

构建 hook 会运行 `npm ci`，构建前端，并把产物打进 Python wheel。功能开发和发布检查见开发者指南。

## Documentation / 文档

| Reader / 读者 | Start here / 从这里开始 |
| --- | --- |
| Users creating figures / 制图用户 | [User Guide](docs/user-guide.md) |
| Product planning / 产品规划 | [Product Requirements](docs/prd.md) and [Roadmap](docs/roadmap.md) |
| API consumers / API 使用者 | [API Reference](docs/api-reference.md) |
| Contributors / 继续开发者 | [Developer Guide](docs/developer-guide.md) and [Technical Design](docs/technical-design.md) |

The README stays intentionally short. Long troubleshooting, API contracts, architecture details, and backlog items live in `docs/`.

README 有意保持简短。较长的排错、API 契约、架构细节和后续计划都放在 `docs/` 中。
