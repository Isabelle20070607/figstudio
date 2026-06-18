# 路线图

本路线图区分当前 public beta 承诺和可能的后续工作。用户操作说明放在用户文档，API contracts 放在 API reference。

## 方向

- 保持 FigStudio 是 local-first、AI-compatible 的 figure editor 和 compiler，而不是 AI figure-generator 聊天入口。
- 模型调用留在核心 app 之外。外部 agent 可以提出 `FigureSpec` 或 `FigureSpec` patch 修改，但 FigStudio 负责确定性地 validate、preview、diff、apply、export 和 generate code。
- 把 `FigureSpec` 作为 editing、validation、generated Matplotlib OO code、provenance 和未来 agent tooling 的持久 contract。

## 当前：Public Beta

- 保持脚本和 Notebook 闭环稳定：launch、map data、validate、render preview、generate code、save or copy、export。
- 保持 generated code 为纯 Matplotlib OO code，不依赖 FigStudio runtime。
- 从 Python wheel 服务打包后的 React editor，运行时不需要 Node/npm。
- 支持 manuscript presets、project style profiles、text/arrow annotations、FigureSpec JSON import/export、preset-backed panel layouts 和 public beta plot kinds。
- 支持第一批面向 pandas DataFrame 的 general statistics recipes：`mean_sem_line`、`grouped_points` 和 `paired_before_after`。
- 保持 recipe specs data-light：保存 variable names、column mappings、style、target axes 和 recipe kind，不保存原始 DataFrame contents。
- 当 live namespace、DataFrame columns、axes 或 profile context 能识别可能修复方式时，显示 field-level validation repair suggestions。
- 保持 codegen、validation、layout geometry、render/export failures、writeback safety、existing Figure inspection、API smoke behavior、spec import/export、API/type drift、bundle size 和 browser smoke behavior 的测试。
- 保持英文和中文文档与当前 behavior 对齐。

## 下一步：Beta Hardening

- 每个 public tag 都保持 release notes、changelog 以及 PyPI/GitHub workflow evidence 最新。
- 在 domain-specific recipes 之前补齐跨领域 reference 或 guide lines：vertical/horizontal constants、baselines、thresholds、cutoff labels 和样式控制。
- 在 domain-specific recipes 之前补齐 small-multiple 或 faceted panel authoring：从 DataFrame groups、mapping keys 或 sequence items 自动重复 axes，并支持 shared-axis options 和 panel title templates。
- 在 reference lines 和 repeated panels 稳定后，增加 secondary y-axis 支持，用于 raw events 加 summary rates 这类 overlay。
- 在 preset-backed GridSpec panel layouts 稳定后，再探索完整 `subplot_mosaic` authoring。
- 加强 Notebook workflow，改善 copy/cell output ergonomics，同时避免 silent notebook file mutation。
- 建立真实 example gallery、README screenshots 和短 workflow GIFs，覆盖 plot layers、statistics recipes、existing Figure inspection、notebook-style output 和 package install flows。每个例子应展示 input data、user intent、preview、generated code 和 export result。
- 增加 publication-readiness export checks：readable font size、DPI/export format、缺失 axes 或 colorbar labels、legend overlap、panel labels、已保存 `FigureSpec`、generated code sync，以及清楚的 recipe error definitions。
- 增加不内置模型调用的 deterministic AI-compatible handoff：复制当前 figure context，导入 `FigureSpec` 或 patch，显示 spec diff，validate，preview，并让用户 apply 或 reject 修改。
- 只有当 Matplotlib 暴露足够 raw 或 reproducible data 时，才把 existing Figure inspection 扩展为 editable statistical recipes。
- 随依赖变化监控 startup 和 bundle size trends。

## 以后：Ecosystem

- 在共享 reference-line、repeated-panel 和 secondary-axis primitives 能承载通用结构之后，再增加面向 neuroscience、image panels、matrix/heatmap workflows、time series 和其他领域图形约定的 recipe packs。
- 在常见 workflow 保持确定性后，增加更深入的 editing ergonomics，例如 undo/redo history、scoped command-palette actions 和 selected-object operations。
- 增加 figure manifest 和 provenance records，记录 `FigureSpec` version、FigStudio version、source script、data variable summaries、recipe semantics、export format 和 generated-code hash。
- 只有在 `FigureSpec` 和 patch contracts 稳定后，再增加面向 agent 的 headless `validate`、`render`、`export`、`codegen` commands。
- 在 style profiles 被验证后，增加可选 project-level templates，用于 figure style governance。
- 只有在当前 generated-code contract 稳定后，再探索更丰富的 style systems。
- 只有在 Python package workflow 稳定后，再探索 desktop installers。
- 只有在内置 recipe 和 gallery patterns 清晰后，再探索 plugin 或 template distribution。

## 暂不做

- Cloud accounts 或 collaboration。
- 在核心 app 中内置 AI model calls、API-key management 或 cloud inference。
- 把 AI 直接生成或重写 Matplotlib code 作为主要 workflow。
- Hosted dashboard publishing。
- 自动重写任意用户 Matplotlib source code。
- 本地 public beta 直接修改 Notebook files。
- 完整 Matplotlib artist coverage，包括所有 custom artist、3D、polar plots、animation 或 browser-native interactive publishing。
- 自动把任意 seaborn、statannotations 或 custom statistical artists 恢复为 editable recipes。
- 首个 public beta 的 desktop installers。
