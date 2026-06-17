# FigStudio

FigStudio is a local-first figure workflow for scientific Python users who want to turn data already present in a script or notebook into polished, reproducible Matplotlib panels.

It opens a browser editor from your Python process, lets you map live variables to plot layers or statistics recipes, previews through Matplotlib, exports publication files, and saves plain Matplotlib OO code back to a controlled script block or notebook cell.

## Install

```powershell
pip install figstudio
```

The wheel includes the React editor. End users do not need Node, npm, Vite, or the frontend source tree after installation.

## Try It

```powershell
figstudio demo
```

For a script, add FigStudio after data preparation and give generated plotting code one controlled block:

```python
import figstudio

# Prepare data first.
session = figstudio.open(locals(), script_path=__file__, block_id="main")

# figstudio:start main
# figstudio:end main
```

In the editor, choose a live variable, add a plot layer or statistics recipe, polish the figure, export PNG/SVG/PDF, then click **Save code**.

## Documentation

| Language | Start here |
| --- | --- |
| English | [docs/en/index.md](docs/en/index.md) |
| Chinese / 中文 | [docs/zh/index.md](docs/zh/index.md) |

Common entry points:

| Reader | English | 中文 |
| --- | --- | --- |
| Figure users | [Get Started](docs/en/getting-started.md) | [快速开始](docs/zh/getting-started.md) |
| Scientific workflows | [Workflows](docs/en/scientific-workflows.md) | [科研制图工作流](docs/zh/scientific-workflows.md) |
| API consumers | [API Reference](docs/en/reference/api.md) | [API 参考](docs/zh/reference/api.md) |
| Contributors | [Developer Guide](docs/en/contributing/developer-guide.md) | [开发者指南](docs/zh/contributing/developer-guide.md) |

## Development

```powershell
uv run --extra dev pytest
cd frontend
npm install
npm run build
npm run dev
```

Build a publishable package:

```powershell
uv build
```

The build hook bundles the frontend into the Python wheel. Runtime installs from a built wheel still use the packaged editor and do not require frontend tooling.
