# FigStudio Roadmap / 路线图

## Now: Local Beta / 当前：本地 Beta

- Keep the script and notebook loop stable: launch, map data, render preview, generate code, save or copy, export.
- Expand tests around codegen, render/export failures, writeback safety, existing Figure inspection, and UI build health.
- Keep generated code plain Matplotlib OO code with no FigStudio runtime dependency.
- Treat bundle size warning as non-blocking for beta, but monitor it.

- 保持脚本和 Notebook 闭环稳定：启动、映射数据、渲染预览、生成代码、保存或复制、导出。
- 扩展 codegen、渲染/导出失败、写回安全、existing Figure inspection 和 UI 构建测试。
- 保持生成代码为纯 Matplotlib OO 代码，不依赖 FigStudio 运行时。
- 大 bundle 警告不阻断 beta，但需要持续关注。

## Next: Usability and Scientific Styling / 下一步：可用性和科研样式

- Add style presets for common manuscript workflows: journal-like single column, double column, poster, and slide figures.
- Add annotation UI for text, arrows, and simple point labels.
- Improve existing Figure inspection beyond line artists, especially scatter collections, image artists, bars, and legends.
- Add richer data validation before render so dimension mismatches are caught in the editor.
- Consider code splitting for CodeMirror and editor-heavy dependencies if bundle size affects startup.

- 增加常见论文流程的样式预设：期刊单栏、双栏、poster 和 slide 图。
- 增加注释 UI：文本、箭头和简单点标签。
- 扩展 existing Figure inspection，不只支持 line artist，重点覆盖 scatter collection、image artist、bar 和 legend。
- 在渲染前加入更丰富的数据校验，让维度不匹配尽早在编辑器里暴露。
- 如果 bundle 大小影响启动，再考虑拆分 CodeMirror 和编辑器重依赖。

## Later: Packaging and Ecosystem / 以后：打包和生态

- Prepare public package publishing only after beta workflows are stable.
- Add notebook integration that can replace cells through an explicit user-approved extension flow.
- Add plot recipe plugins for domain-specific workflows such as spectroscopy, time series, and image panels.
- Add optional project-level templates for figure style governance.
- Explore import/export of `FigureSpec` files for reproducible GUI sessions.

- 只有在 beta 工作流稳定后再准备公开包发布。
- 增加 Notebook 集成，但必须通过用户明确批准的扩展流程替换 cell。
- 增加领域 plot recipe 插件，例如光谱、时间序列和图像面板。
- 增加可选项目级模板，用于统一 figure 样式治理。
- 探索 `FigureSpec` 文件导入/导出，让 GUI 会话可复现。

## Non-Goals Until Revisited / 暂不做

- Cloud accounts or collaboration.
- Hosted dashboard publishing.
- Automatic rewriting of arbitrary user Matplotlib source code.
- Direct mutation of notebook files by the local beta.

- 云账号或协作。
- 托管 dashboard 发布。
- 自动重写任意用户 Matplotlib 源码。
- 本地 beta 直接修改 notebook 文件。
