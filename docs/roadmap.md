# FigStudio Roadmap / 路线图

This roadmap separates current public beta commitments from likely future work. User instructions belong in the user guide, and API contracts belong in the API reference.

本路线图区分当前公开 beta 承诺和可能的后续工作。用户操作说明放在用户指南，API 契约放在 API reference。

## Now: Public Beta / 当前：公开 Beta

- Keep the script and notebook loop stable: launch, map data, validate, render preview, generate code, save or copy, export.
- Keep generated code plain Matplotlib OO code with no FigStudio runtime dependency.
- Serve the bundled React editor from the Python wheel without requiring Node/npm at runtime.
- Support manuscript presets, text/arrow annotations, FigureSpec JSON import/export, simple subplot grids, and the public beta plot kinds.
- Keep browser-level UI smoke coverage for preset, annotation, export, import/export, subplot, validation focus, and save-code flows.
- Keep existing Figure inspection best-effort for line, scatter, image, and bar artists, plus metadata for legends, colorbars, histograms, boxplots, and violin plots.
- Maintain tests around codegen, validation, render/export failures, writeback safety, existing Figure inspection, API smoke behavior, spec import/export, API/type drift, bundle size, and browser smoke behavior.
- Keep GitHub Actions workflows for CI, TestPyPI Trusted Publishing, and PyPI Trusted Publishing release gates.
- Keep user, API, technical, developer, PRD, and roadmap docs aligned with current behavior.

- 保持脚本和 Notebook 闭环稳定：启动、映射数据、校验、渲染预览、生成代码、保存或复制、导出。
- 保持生成代码为纯 Matplotlib OO code，不依赖 FigStudio 运行时。
- 从 Python wheel 服务打包后的 React 编辑器，运行时不需要 Node/npm。
- 支持论文样式预设、文本/箭头注释、FigureSpec JSON 导入导出、基础 subplot 网格和公开 beta 图层类型。
- 为 preset、annotation、export、import/export、subplot、validation focus 和 save-code flow 保持浏览器级 UI 冒烟覆盖。
- 对 line、scatter、image 和 bar artist 保持 best-effort existing Figure inspection，并为 legend、colorbar、histogram、boxplot 和 violin plot 提供 metadata。
- 保持 codegen、validation、render/export 失败、写回安全、existing Figure inspection、API 冒烟行为、spec import/export、API/type drift、bundle size 和 browser smoke behavior 的测试。
- 保持 GitHub Actions workflows，用于 CI、TestPyPI Trusted Publishing 和 PyPI Trusted Publishing release gates。
- 保持用户、API、技术、开发者、PRD 和路线图文档与当前行为一致。

## Next: Beta Hardening / 下一步：Beta 加固

- Run and monitor the first TestPyPI and PyPI releases after pending Trusted Publishers are configured on both package indexes.
- Improve validation guidance beyond selection/focus with field-level repair suggestions where the UI has enough context.
- Expand existing Figure inspection into editable statistical layers only when Matplotlib exposes enough raw or reproducible data.
- Monitor startup and bundle size trends as dependencies change; keep editor-heavy dependencies code-split.
- Consider generated TypeScript contracts if the lightweight drift test becomes too limited.

- 在两个 package index 配置 pending Trusted Publisher 后，运行并监控首次 TestPyPI 和 PyPI 发布。
- 在 UI 有足够上下文时，把 validation guidance 从 selection/focus 扩展到 field-level repair suggestion。
- 只有当 Matplotlib 暴露足够 raw 或可复现数据时，才把 existing Figure inspection 扩展为可编辑 statistical layers。
- 随依赖变化持续监控启动速度和 bundle size，保持 editor-heavy dependencies code-split。
- 如果轻量 drift test 不再够用，再考虑生成 TypeScript contracts。

## Later: Ecosystem / 以后：生态

- Add notebook integration that can replace cells through an explicit user-approved extension flow.
- Add plot recipe plugins for domain-specific workflows such as spectroscopy, time series, and image panels.
- Add optional project-level templates for figure style governance.
- Explore richer style systems only after the current generated-code contract stays stable.
- Explore desktop installers only after the Python package workflow is stable.

- 增加 Notebook 集成，但必须通过用户明确批准的扩展流程替换 cell。
- 增加领域 plot recipe plugins，例如光谱、时间序列和图像面板。
- 增加可选项目级模板，用于统一 figure 样式治理。
- 只有在当前 generated-code contract 稳定后再探索更丰富的样式系统。
- 只有在 Python package 工作流稳定后再探索桌面安装器。

## Non-Goals Until Revisited / 暂不做

- Cloud accounts or collaboration.
- Hosted dashboard publishing.
- Automatic rewriting of arbitrary user Matplotlib source code.
- Direct mutation of notebook files by the local public beta.
- Full support for every Matplotlib artist, 3D, polar plots, animation, or browser-native interactive publishing.
- Desktop installers in the first public beta.

- 云账号或协作。
- 托管 dashboard 发布。
- 自动重写任意用户 Matplotlib 源码。
- 本地公开 beta 直接修改 notebook 文件。
- 完整支持所有 Matplotlib artist、3D、polar、动画或浏览器原生交互式发布。
- 首个公开 beta 的桌面安装器。
