# 暂缓事项

本页记录当前 roadmap 形态中刻意暂缓的工作。有些条目可以在产品 contracts 稳定后重新评估。

| 暂缓领域 | 暂缓原因 | 重新评估条件 |
| --- | --- | --- |
| Cloud accounts 或 collaboration | 产品是 local-first，不需要 hosted identity 或 collaboration 也能完成 beta workflow。 | Local workflow、package distribution 和 reproducibility contracts 稳定，且用户明确需要 hosted collaboration。 |
| 在核心 app 中内置 AI model calls、API-key management 或 cloud inference | FigStudio 应保持确定性的 editor/compiler；模型调用属于核心 app 外部。 | 确定性的 `FigureSpec` patch import、diff、validation 和 apply/reject flows 已稳定。 |
| 把 AI 直接生成或重写 Matplotlib code 作为主要 workflow | Generated code 应来自 validated specs，而不是 opaque rewrites。 | AI handoff 可以通过可审阅 spec patches 运行，并且不削弱 codegen determinism。 |
| Hosted dashboard publishing | 发布 dashboard 不属于可复现 manuscript-figure workflow。 | 项目有意扩展到 local scientific figure authoring 之外。 |
| 自动重写任意用户 Matplotlib source code | Safe writeback 限于 controlled marker blocks。 | 单独的、明确的 source-transformation design 存在，并具备强 safety boundaries。 |
| 直接修改 Notebook files | Notebook writeback 是 semi-automatic，返回 replacement code。 | 用户批准的 notebook file mutation workflow 有清楚 rollback 和 review model。 |
| 完整 Matplotlib artist coverage，包括所有 custom artist、完整 3D editing、完整 animation timeline editing 或 browser-native interactive publishing | Full artist coverage 会稀释对可复现 exploration 和 publication panels 的支持。 | 高需求 artist families 可以通过清楚、可测试的 contracts 支持；limited polar、animation-lite 或 static 3D views 可以先作为有边界的 roadmap initiatives 处理。 |
| 自动把任意 seaborn、statannotations 或 custom statistical artists 恢复为 editable recipes | 只有能保留 raw 或 reproducible data 时，恢复才有价值。 | Source artist 暴露足够 data 和 semantics，可生成可复现 code。 |
| Desktop installers | Public beta 以 Python package 为第一安装路径。 | Python package workflow 稳定，且 installer demand 足以证明 distribution 工作值得做。 |
| 更丰富的 style systems | 当前 generated-code 和 style-profile contracts 应先证明稳定。 | Style profiles 被广泛使用，且用户需要更强表达力的 governance model。 |
| Plugin 或 template distribution | 外部分发会过早冻结 extension contracts。 | Bundled recipe 和 gallery patterns 清楚到可以提供 compatibility promises。 |
