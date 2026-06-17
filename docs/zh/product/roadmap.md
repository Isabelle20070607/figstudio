# 路线图

本路线图区分当前 public beta 承诺和可能的后续工作。用户操作说明放在用户文档，API contracts 放在 API reference。

## 当前：Public Beta

- 保持脚本和 Notebook 闭环稳定：launch、map data、validate、render preview、generate code、save or copy、export。
- 保持 generated code 为纯 Matplotlib OO code，不依赖 FigStudio runtime。
- 从 Python wheel 服务打包后的 React editor，运行时不需要 Node/npm。
- 支持 manuscript presets、project style profiles、text/arrow annotations、FigureSpec JSON import/export、preset-backed panel layouts 和 public beta plot kinds。
- 支持第一批面向 pandas DataFrame 的 general statistics recipes：`mean_sem_line`、`grouped_points` 和 `paired_before_after`。
- 保持 recipe specs data-light：保存 variable names、column mappings、style、target axes 和 recipe kind，不保存原始 DataFrame contents。
- 保持 codegen、validation、layout geometry、render/export failures、writeback safety、existing Figure inspection、API smoke behavior、spec import/export、API/type drift、bundle size 和 browser smoke behavior 的测试。
- 保持英文和中文文档与当前 behavior 对齐。

## 下一步：Beta Hardening

- 在 pending Trusted Publishers 配置完成后，运行并监控首次 TestPyPI 和 PyPI releases。
- 在 UI 有足够上下文时，把 validation guidance 从 selection/focus 扩展到 field-level repair suggestions。
- 在 preset-backed GridSpec panel layouts 稳定后，再探索完整 `subplot_mosaic` authoring。
- 加强 Notebook workflow，改善 copy/cell output ergonomics，同时避免 silent notebook file mutation。
- 建立真实 example gallery，覆盖 plot layers、statistics recipes、existing Figure inspection、notebook-style output 和 package install flows。
- 只有当 Matplotlib 暴露足够 raw 或 reproducible data 时，才把 existing Figure inspection 扩展为 editable statistical recipes。
- 随依赖变化监控 startup 和 bundle size trends。

## 以后：Ecosystem

- 增加面向 neuroscience、image panels、matrix/heatmap workflows、time series 和其他领域图形约定的 recipe packs。
- 在 style profiles 被验证后，增加可选 project-level templates，用于 figure style governance。
- 只有在当前 generated-code contract 稳定后，再探索更丰富的 style systems。
- 只有在 Python package workflow 稳定后，再探索 desktop installers。
- 只有在内置 recipe 和 gallery patterns 清晰后，再探索 plugin 或 template distribution。

## 暂不做

- Cloud accounts 或 collaboration。
- Hosted dashboard publishing。
- 自动重写任意用户 Matplotlib source code。
- 本地 public beta 直接修改 Notebook files。
- 完整 Matplotlib artist coverage，包括所有 custom artist、3D、polar plots、animation 或 browser-native interactive publishing。
- 自动把任意 seaborn、statannotations 或 custom statistical artists 恢复为 editable recipes。
- 首个 public beta 的 desktop installers。
