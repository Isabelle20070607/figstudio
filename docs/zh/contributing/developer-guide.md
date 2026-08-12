# 开发者指南

本指南面向继续开发 FigStudio 的人，说明本地工作流、改动面和检查。

## 本地环境

Python 任务使用 `uv`，React editor 任务在 `frontend/` 中使用 `npm`。

```powershell
uv run --extra dev pytest
```

```powershell
cd frontend
npm install
npm run build
npm run check:bundle
npm run test:e2e
npm run dev
```

开发服务器绑定到 `127.0.0.1`。Python app 默认也绑定到 `127.0.0.1`。

## 仓库地图

- `src/figstudio/session.py`：public `open()` lifecycle、local port、browser launch、optional Figure inspection。
- `src/figstudio/models.py`：后端行为和 API 文档共享的 Pydantic models。
- `src/figstudio/registry.py`：变量过滤和 summaries。
- `src/figstudio/style_profiles.py`：项目 `.figstudio/styles.json` loading 和 effective style resolution。
- `src/figstudio/validation.py`：pre-render validation。
- `src/figstudio/codegen.py`：Matplotlib OO code generation。
- `src/figstudio/render.py`：Agg rendering 和 export。
- `src/figstudio/sync.py`：controlled script writeback。
- `src/figstudio/server.py`：FastAPI routes 和 static editor serving。
- `src/figstudio/spec_io.py`：`.figstudio.json` helpers。
- `frontend/src/App.tsx`：editor shell、controls、import/export、preview、validation display。
- `frontend/src/types.ts`：public data contracts 的 TypeScript mirror。
- `tests/`：behavior 和 smoke coverage。

## Feature Change Rules

新增 plot kind 时，一次性更新完整 contract：Pydantic literal、TypeScript type、UI creation 和 controls、codegen、必要 validation、tests 和 docs。

新增 recipe 时，保持 generated imports 限于 Matplotlib，使用现有用户 DataFrame 变量的方法而不是序列化数据进代码，并更新 recipe validation 和 smoke coverage。

修改 request、response 或 FigureSpec fields 时，把 `src/figstudio/models.py` 视为后端 source of truth，并更新 `frontend/src/types.ts`、request construction、serialization tests 和 API reference。

在合理范围内保持旧字段兼容，因为用户可能已有保存的 `.figstudio.json` 文件。

## Writeback Rules

脚本写回只能替换唯一受控块：

```python
# figstudio:start main
# generated code lives here
# figstudio:end main
```

`CodeSyncEngine` 会拒绝缺失 blocks、同一 id 的重复 blocks、嵌套 markers、不匹配 start/end markers 和 IO failures。不要添加会编辑受控块之外代码的备用逻辑。

从 Notebook 启动时返回 replacement cell code，不得直接修改 Notebook files。

## 文档归属

每类内容只放在一个主文档，其他地方用链接引用：

- `README.md` 负责项目定位、首次运行命令和文档索引；`CHANGELOG.md` 是按时间记录版本变化的主记录。
- 用户流程分别放在 `getting-started.md`、`scientific-workflows.md`、`styles-and-layouts.md`、`save-export-reuse.md` 和 `troubleshooting.md`。
- `reference/api.md` 负责公开接口，`architecture/technical-design.md` 负责内部设计，本指南负责开发流程。
- `product/prd.md` 负责当前 beta 范围，`product/roadmap*.md` 负责未来工作，`product/release-notes.md` 提供本地化版本摘要。

旧的顶层文档只保留简短兼容入口。

## 文档同步

- `docs/en` 下每篇长文都应在 `docs/zh` 下有相同相对路径，两边同等维护。
- 行为变化时更新主文档及其另一语言版本；范围变化时同步两份 PRD 和相关路线图。
- 发布前根据上一个公开标签以来的完整差异更新 `CHANGELOG.md` 和两份版本说明。
- 完成文档工作前，清理过时的规划和阶段措辞。用 `Get-ChildItem README.md,docs -Recurse -File -Filter *.md | Select-String -Pattern '^#+ .*?(Quick Start|快速开始)'` 检查入门标题；这类标题只应出现在 README 和两份入门文档中。
- 检查双语路径、链接和 `git diff --check -- AGENTS.md README.md docs`。

## Release Checks

面向 package 的改动：

- 运行 `uv run --extra dev pytest`；
- 运行 `cd frontend`; `npm run build`；
- 运行 `cd frontend`; `npm run check:bundle`；
- 运行 `cd frontend`; `npm run test:e2e`；
- 运行 `uv build`；
- 在干净 virtual environment 中安装构建出的 wheel；
- 运行 `figstudio demo --no-browser`，并确认 `/` 和 `/api/session` 可从 `127.0.0.1` 访问。
