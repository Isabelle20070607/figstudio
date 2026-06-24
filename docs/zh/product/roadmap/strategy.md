# 路线图策略

本页说明 FigStudio 如何选择 roadmap 工作。当前 beta 承诺放在 [产品需求](../prd.md)，主题化 backlog 放在 [initiatives](initiatives.md)。

## 产品方向

- 保持 FigStudio 是 local-first、AI-compatible 的 figure editor 和 compiler，而不是 AI figure-generator 聊天入口。
- 把 FigStudio 定位为 explore-first 的科研可视化工作台：帮助 Python 用户快速比较数据视角，并在结果值得保留时导出可复现的 Matplotlib 图。
- 模型调用留在核心 app 之外。外部 agent 可以提出 `FigureSpec` 或 `FigureSpec` patch 修改，但 FigStudio 负责确定性地 validate、preview、diff、apply、export 和 generate code。
- 把 `FigureSpec` 作为 editing、validation、generated Matplotlib OO code、provenance 和未来 agent tooling 的持久 contract。
- 保持 generated code 为纯 Matplotlib OO code，不依赖 FigStudio runtime。
- 保持 runtime wheel 自包含：打包后的 React editor 必须由 Python package 提供，安装后不要求 Node/npm。

## 排序原则

- 先稳定跨领域 plotting primitives，再做 domain-specific recipe packs。
- 优先推进能减少 exploration 阶段重复代码、方便比较分析变体、或揭示对象层面异质性的功能，再增加最后一公里 polish 控件。
- 优先覆盖科研论文图，而不是泛商业图表。
- 保持 recipe specs data-light：保存 variable names、column mappings、style、target axes、filters 和 recipe kind，不保存原始 DataFrame contents。
- Repeated-panel 和 layout 工作在没有充分理由引入更强 layout contract 前，应继续兼容现有 `FigureSpec.rows`、`FigureSpec.cols` 和 `AxesSpec` geometry。
- 在外部分发 recipe/template 之前，先建立可复用的 package、gallery 和 validation substrate。
- 加强 Notebook 体验，但不 silent mutation notebook files。
- AI-compatible handoff 只通过确定性的 import、diff、validate、preview、apply/reject 流程进入核心产品。
- 只有在 `FigureSpec`、generated-code、package 和 patch contracts 稳定后，再推进更丰富的生态能力。

## 路线图标签

Initiatives 使用两个标签，让规划保持可读，同时避免把所有条目强行塞进单一时间桶。

| 标签 | 取值 | 含义 |
| --- | --- | --- |
| Maturity | `ready`、`foundation-needed`、`exploratory` | 还需要多少产品或技术基础。 |
| Horizon | `near`、`later`、`deferred` | 预期规划距离，是指导信号，不是 release promise。 |
