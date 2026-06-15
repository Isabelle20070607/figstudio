# FigStudio

FigStudio is a local graphical editor for Matplotlib figures. It is built for scientific Python users who already have data in a script or notebook and want a faster way to create, style, preview, export, and save reproducible Matplotlib OO code.

FigStudio 是一个本地 Matplotlib 图形编辑器。它面向已经在脚本或 Notebook 中完成数据处理的科研 Python 用户，用 GUI 快速创建、调整、预览、导出并保存可复现的 Matplotlib OO 代码。

## Quick Start / 快速开始

```python
import figstudio

# Finish data processing first.
session = figstudio.open(locals(), script_path=__file__, block_id="main")

# figstudio:start main
# figstudio:end main
```

Run the example:

```powershell
uv run python examples\basic_script.py
```

The browser editor runs on `127.0.0.1`, reads safe summaries of local variables, renders previews with Matplotlib, and writes only inside the selected controlled block.

浏览器编辑器绑定到 `127.0.0.1`，只读取本地变量摘要，用 Matplotlib 生成真实预览，并且只写回指定的受控代码块。

## Development / 开发

```powershell
uv run pytest
```

```powershell
cd frontend
npm install
npm run build
npm run dev
```

## Documentation / 文档

- [Product Requirements](docs/prd.md)
- [Technical Design](docs/technical-design.md)
- [User Guide](docs/user-guide.md)
- [Roadmap](docs/roadmap.md)

Current target: local beta. Public package publishing is intentionally out of scope for this milestone.

当前目标：本地 beta。公开包发布不属于当前里程碑范围。
