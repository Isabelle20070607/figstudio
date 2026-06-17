# FigStudio Developer Guide / 开发者指南

This guide is for people continuing FigStudio development. It covers local workflows, where to make changes, how to add features safely, and which checks to run.

本指南面向继续开发 FigStudio 的人，说明本地工作流、改动位置、安全添加功能的方式，以及需要运行的检查。

## Local Environment / 本地环境

Use `uv` for Python tasks and `npm` inside `frontend/` for the React editor.

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

The development server binds to `127.0.0.1`. The Python app also binds to `127.0.0.1` by default.

开发服务器绑定到 `127.0.0.1`。Python app 默认也绑定到 `127.0.0.1`。

## Repository Map / 仓库地图

- `src/figstudio/session.py`: public `open()` lifecycle, local port, browser launch, optional Figure inspection.
- `src/figstudio/models.py`: Pydantic models shared by backend behavior and API documentation.
- `src/figstudio/registry.py`: variable filtering and summaries.
- `src/figstudio/validation.py`: pre-render validation.
- `src/figstudio/codegen.py`: Matplotlib OO code generation.
- `src/figstudio/render.py`: Agg rendering and export.
- `src/figstudio/sync.py`: controlled script writeback.
- `src/figstudio/server.py`: FastAPI routes and static editor serving.
- `src/figstudio/spec_io.py`: `.figstudio.json` helpers.
- `frontend/src/App.tsx`: editor shell, controls, import/export, preview, validation display.
- `frontend/src/types.ts`: TypeScript mirror of the public data contracts.
- `tests/`: behavior and smoke coverage.

- `src/figstudio/session.py`：public `open()` 生命周期、本地端口、浏览器启动、可选 Figure inspection。
- `src/figstudio/models.py`：后端行为和 API 文档共享的 Pydantic models。
- `src/figstudio/registry.py`：变量过滤和摘要。
- `src/figstudio/validation.py`：渲染前校验。
- `src/figstudio/codegen.py`：Matplotlib OO code generation。
- `src/figstudio/render.py`：Agg 渲染和导出。
- `src/figstudio/sync.py`：受控脚本写回。
- `src/figstudio/server.py`：FastAPI routes 和静态 editor 服务。
- `src/figstudio/spec_io.py`：`.figstudio.json` helper。
- `frontend/src/App.tsx`：editor shell、控件、导入导出、预览、validation display。
- `frontend/src/types.ts`：public data contracts 的 TypeScript mirror。
- `tests/`：行为和冒烟覆盖。

## Development Loops / 开发循环

Backend behavior:

后端行为：

```powershell
uv run --extra dev pytest
```

Run the local app without opening a browser:

启动本地 app 但不打开浏览器：

```powershell
uv run python -m figstudio --no-browser
```

Run the sample data session:

启动样例数据会话：

```powershell
uv run python -m figstudio demo --no-browser
```

Build frontend assets:

构建前端 assets：

```powershell
cd frontend
npm run build
npm run check:bundle
```

Run browser-level UI smoke coverage against the deterministic sample server:

对确定性的 sample server 运行浏览器级 UI 冒烟覆盖：

```powershell
cd frontend
npm run test:e2e
```

The Playwright config starts `examples/smoke_server.py` on `127.0.0.1:8765` and covers add-layer, add-recipe, preset, annotation, export, import/export, subplot, validation focus, and save-code flows.

Playwright 配置会在 `127.0.0.1:8765` 启动 `examples/smoke_server.py`，覆盖 add-layer、add-recipe、preset、annotation、export、import/export、subplot、validation focus 和 save-code 流程。

Build the package:

构建 package：

```powershell
uv build
```

The Hatch build hook runs `npm ci` in clean checkouts, reuses an existing local `frontend/node_modules` when present, builds the frontend, and copies `frontend/dist` into `src/figstudio/static` for wheel packaging.

Hatch build hook 会在 clean checkout 中运行 `npm ci`；如果本地已有 `frontend/node_modules`，则复用现有依赖；随后构建前端，并把 `frontend/dist` 复制到 `src/figstudio/static` 以打进 wheel。

If a locked-down Windows shell blocks Vite child-process spawning after `npm run build` has already succeeded, set `FIGSTUDIO_SKIP_FRONTEND_BUILD=1` for `uv build`; the hook will copy the existing `frontend/dist` into package static assets.

如果受限 Windows shell 在 `npm run build` 已经成功后仍阻止 Vite child-process spawning，可在 `uv build` 时设置 `FIGSTUDIO_SKIP_FRONTEND_BUILD=1`；hook 会把现有 `frontend/dist` 复制进 package static assets。

## Adding a Plot Kind / 新增图层类型

When adding a new plot kind, update the full contract in one pass:

新增图层类型时，一次性更新完整 contract：

- Add the literal to `PlotKind` in `src/figstudio/models.py`.
- Add matching TypeScript support in `frontend/src/types.ts`.
- Add UI creation and layer controls in `frontend/src/App.tsx`.
- Add code generation in `src/figstudio/codegen.py`.
- Add validation in `src/figstudio/validation.py` when the plot has data shape or scale constraints.
- Add render/codegen tests and at least one validation test when applicable.
- Keep `tests/test_contract_types.py` passing so TypeScript mirrors do not drift from Pydantic models.
- Update `docs/user-guide.md`, `docs/api-reference.md`, `docs/prd.md`, and `docs/roadmap.md` if scope changes.

- 在 `src/figstudio/models.py` 的 `PlotKind` 中加入 literal。
- 在 `frontend/src/types.ts` 中加入匹配的 TypeScript 支持。
- 在 `frontend/src/App.tsx` 中加入 UI 创建逻辑和图层控件。
- 在 `src/figstudio/codegen.py` 中加入代码生成。
- 如果该图对数据形状或坐标轴 scale 有约束，在 `src/figstudio/validation.py` 中加入校验。
- 增加 render/codegen 测试；适用时至少增加一个 validation 测试。
- 保持 `tests/test_contract_types.py` 通过，避免 TypeScript mirror 偏离 Pydantic models。
- 如果范围变化，同步更新 `docs/user-guide.md`、`docs/api-reference.md`、`docs/prd.md` 和 `docs/roadmap.md`。

Generated plotting code must remain plain Matplotlib OO code and must not require `figstudio` at runtime.

生成绘图代码必须保持为纯 Matplotlib OO code，运行时不得依赖 `figstudio`。

## Adding a Recipe / 新增 Recipe

Recipes sit beside plot layers instead of replacing them. They should capture reusable scientific plotting intent while preserving the core generated-code contract.

Recipe 与 plot layer 并列存在，而不是替代 plot layer。它们应表达可复用的科研绘图意图，同时保持核心 generated-code contract。

When adding a new recipe, update the full contract in one pass:

新增 recipe 时，一次性更新完整 contract：

- Add the literal to `RecipeKind` and any required fields to `RecipeDatasetRef` or `RecipeLayer` in `src/figstudio/models.py`.
- Add matching TypeScript support in `frontend/src/types.ts`.
- Add UI creation and recipe controls in `frontend/src/App.tsx`.
- Add readable Matplotlib OO code generation in `src/figstudio/codegen.py`.
- Keep generated recipe imports limited to Matplotlib. Use methods on existing user DataFrame variables instead of serializing data into code.
- Add validation in `src/figstudio/validation.py`, including required columns and allowed source variable kinds.
- Add codegen tests, validation tests, render/API smoke coverage, and contract drift coverage.
- Extend e2e smoke when the new recipe changes the user workflow.
- Update `docs/user-guide.md`, `docs/api-reference.md`, `docs/technical-design.md`, `docs/prd.md`, and `docs/roadmap.md`.

- 在 `src/figstudio/models.py` 的 `RecipeKind` 中加入 literal，并按需更新 `RecipeDatasetRef` 或 `RecipeLayer` 字段。
- 在 `frontend/src/types.ts` 中加入匹配的 TypeScript 支持。
- 在 `frontend/src/App.tsx` 中加入 UI 创建逻辑和 recipe 控件。
- 在 `src/figstudio/codegen.py` 中加入可读的 Matplotlib OO 代码生成。
- 生成 recipe 代码的 import 必须限于 Matplotlib。使用现有用户 DataFrame 变量的方法，不要把数据序列化进代码。
- 在 `src/figstudio/validation.py` 中加入校验，包括必需列和允许的 source variable kind。
- 增加 codegen 测试、validation 测试、render/API 冒烟覆盖和 contract drift 覆盖。
- 如果新 recipe 改变用户工作流，扩展 e2e smoke。
- 更新 `docs/user-guide.md`、`docs/api-reference.md`、`docs/technical-design.md`、`docs/prd.md` 和 `docs/roadmap.md`。

## Changing Data Contracts / 修改数据契约

Treat `src/figstudio/models.py` as the source of truth for backend contracts. When changing request, response, or FigureSpec fields:

把 `src/figstudio/models.py` 视为后端契约的来源。修改 request、response 或 FigureSpec 字段时：

- Update `frontend/src/types.ts`.
- Update any request construction in `frontend/src/api.ts` and `frontend/src/App.tsx`.
- Update tests that serialize `model_dump()` payloads.
- Update `docs/api-reference.md`.
- Keep old fields compatible when reasonable because saved `.figstudio.json` files may exist.

- 更新 `frontend/src/types.ts`。
- 更新 `frontend/src/api.ts` 和 `frontend/src/App.tsx` 中构造请求的逻辑。
- 更新序列化 `model_dump()` payload 的测试。
- 更新 `docs/api-reference.md`。
- 在合理范围内保持旧字段兼容，因为用户可能已有保存的 `.figstudio.json` 文件。

## Writeback Rules / 写回规则

Script writeback may only replace a unique controlled block:

脚本写回只能替换唯一受控块：

```python
# figstudio:start main
# generated code lives here
# figstudio:end main
```

`CodeSyncEngine` rejects missing blocks, duplicate blocks for the same id, nested markers, unmatched start/end markers, and IO failures. Do not add fallback behavior that edits outside the controlled block.

`CodeSyncEngine` 会拒绝缺失代码块、同一 id 的重复代码块、嵌套 marker、不匹配的 start/end marker 和 IO 失败。不要添加会编辑受控块之外代码的 fallback 行为。

Notebook-style sessions return replacement cell code and must not mutate notebook files directly.

Notebook 风格会话返回替换 cell code，不得直接修改 notebook 文件。

## Existing Figure Inspection / 已有 Figure 检查

Existing Figure support is best-effort inspection, not source-code recovery. Supported artists become generated editable layers when enough data can be extracted. Legends, colorbars, histograms, boxplots, violins, and unsupported artists should remain metadata or read-only context unless the current `FigureSpec` model can reproduce them honestly.

Existing Figure 支持是 best-effort inspection，不是源码恢复。能提取足够数据的受支持 artist 会变成 generated editable layer。legend、colorbar、histogram、boxplot、violin 和不支持的 artist 应保留为 metadata 或只读上下文，除非当前 `FigureSpec` 模型能诚实复现它们。

When expanding inspection, add tests for the inspected artist, the extracted namespace, and the generated FigureSpec.

扩展 inspection 时，需要为被检查的 artist、提取出的 namespace 和生成的 FigureSpec 增加测试。

## Documentation Sync / 文档同步

Keep documentation ownership clear:

保持文档职责清晰：

- `README.md`: positioning, install, entry workflow, development commands, docs index.
- `docs/user-guide.md`: current user workflows and recovery.
- `docs/api-reference.md`: public Python, CLI, REST, model, and error contracts.
- `docs/technical-design.md`: architecture, data flow, safety decisions, packaging, verification.
- `docs/prd.md`: current beta product definition, stories, scope, acceptance criteria, non-goals.
- `docs/roadmap.md`: future planning and non-goals.
- `docs/developer-guide.md`: local development, feature work, tests, release checks, and doc sync.

- `README.md`：定位、安装、入口流程、开发命令、文档索引。
- `docs/user-guide.md`：当前用户工作流和恢复方式。
- `docs/api-reference.md`：public Python、CLI、REST、model 和 error contracts。
- `docs/technical-design.md`：架构、数据流、安全决策、打包、验证。
- `docs/prd.md`：当前 beta 产品定义、用户故事、范围、验收标准、非目标。
- `docs/roadmap.md`：未来规划和非目标。
- `docs/developer-guide.md`：本地开发、功能工作、测试、发布检查和文档同步。

Before finishing docs work, run the stale planning-language scan and onboarding-heading duplication scan listed in `AGENTS.md`. The onboarding-heading scan should only find the README heading.

完成文档工作前，运行 `AGENTS.md` 中列出的 stale planning-language scan 和 onboarding-heading duplication scan。onboarding-heading scan 应只命中 README 标题。

## Release Checks / 发布检查

For package-oriented changes:

面向 package 的改动：

- Run `uv run --extra dev pytest`.
- Run `cd frontend`; `npm run build`.
- Run `cd frontend`; `npm run check:bundle`.
- Run `cd frontend`; `npm run test:e2e`.
- Run `uv build`.
- Install the built wheel in a clean virtual environment.
- Run `figstudio demo --no-browser` and confirm `/` and `/api/session` are served from `127.0.0.1`.

- 运行 `uv run --extra dev pytest`。
- 运行 `cd frontend`; `npm run build`。
- 运行 `cd frontend`; `npm run check:bundle`。
- 运行 `cd frontend`; `npm run test:e2e`。
- 运行 `uv build`。
- 在干净 virtual environment 中安装构建出的 wheel。
- 运行 `figstudio demo --no-browser`，并确认 `/` 和 `/api/session` 可从 `127.0.0.1` 访问。

## Release Automation / 发布自动化

GitHub Actions owns automated checks and publishing:

GitHub Actions 负责自动检查和发布：

- `.github/workflows/ci.yml`: Python tests, frontend build, bundle check, browser smoke, and package build.
- `.github/workflows/publish-testpypi.yml`: manual TestPyPI publish using Trusted Publishing.
- `.github/workflows/publish-pypi.yml`: tag-triggered PyPI publish for `v*` tags using Trusted Publishing.

- `.github/workflows/ci.yml`：Python tests、frontend build、bundle check、browser smoke 和 package build。
- `.github/workflows/publish-testpypi.yml`：使用 Trusted Publishing 手动发布 TestPyPI。
- `.github/workflows/publish-pypi.yml`：对 `v*` tag 使用 Trusted Publishing 发布 PyPI。

Before the first publish, configure pending trusted publishers on TestPyPI and PyPI with project `figstudio`, owner `Isabelle20070607`, repository `figstudio`, the matching workflow filename, and environments `testpypi` or `pypi`.

首次发布前，需要在 TestPyPI 和 PyPI 配置 pending trusted publisher：project 为 `figstudio`，owner 为 `Isabelle20070607`，repository 为 `figstudio`，workflow filename 与对应 workflow 一致，environment 分别为 `testpypi` 或 `pypi`。
