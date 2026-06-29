# 路线图 Initiatives

本页按产品主题组织未来 roadmap 工作。它不是发布计划；maturity 和 horizon 标签用来说明准备程度和大致排序。

## Scientific Authoring Primitives

| Field | Value |
| --- | --- |
| Theme | Scientific authoring primitives |
| Initiative | 探索完整 `subplot_mosaic` authoring。 |
| Why it matters | Mosaic layouts 可以表达超过 named presets 的发表图版结构。 |
| Maturity | `exploratory` |
| Horizon | `later` |
| Readiness | Mosaic syntax 会引入新的 public layout authoring surface，需要先确定足够简洁的用户模型。 |
| Gate/Prerequisite | Preset-backed GridSpec panel layouts 在真实 workflow 中证明稳定。 |

| Field | Value |
| --- | --- |
| Theme | Scientific authoring primitives |
| Initiative | 只以有边界的科研 exploration views 重新评估 limited polar plots、animation-lite 和 static 3D。 |
| Why it matters | Circular data、parameter sliders、frame sequences 和简单 state-space views 对探索有价值，但不应把 FigStudio 变成完整 artist 或 animation editor。 |
| Maturity | `exploratory` |
| Horizon | `later` |
| Gate/Prerequisite | 核心 2D recipes、repeated-panel workflows、validation、export 和 generated-code contracts 保持稳定。 |

## Recipe And Statistical Coverage

| Field | Value |
| --- | --- |
| Theme | Recipe and statistical coverage |
| Initiative | 增加剩余 distribution 和 relationship recipes，例如带 fitted trend 的 regression scatter、confidence 或 percentile bands、two-dimensional histograms、hexbin summaries，以及更强的 heatmap 或 matrix controls。 |
| Why it matters | 这些补齐 exploratory 和 manuscript figures 中高价值的可复现 Matplotlib workflows。 |
| Maturity | `foundation-needed` |
| Horizon | `later` |
| Readiness | 主要风险在 fitted trends、bands、binning、hexbin summaries 和 matrix controls 的统计语义。 |
| Gate/Prerequisite | 随着 recipe 复杂度增长，generated-code templates 和 recipe validation 仍然可读。 |

| Field | Value |
| --- | --- |
| Theme | Recipe and statistical coverage |
| Initiative | 当 recoverable data 足够时，把 existing Figure inspection 扩展为 editable statistical recipes。 |
| Why it matters | 只有当 FigStudio 能保留可复现性时，用户才应继续编辑受支持的已有图形。 |
| Maturity | `exploratory` |
| Horizon | `later` |
| Gate/Prerequisite | Matplotlib 为相关 artists 暴露足够 raw 或 reproducible data。 |

## Exploration Workspace

| Field | Value |
| --- | --- |
| Theme | Exploration workspace |
| Initiative | 增加 exploration result board，包含 result cards、pinned findings、spec snapshots、notes，以及 restore 或 duplicate 操作。 |
| Why it matters | Exploration 是分支式、迭代式流程；用户需要记住哪个 data view、mapping、filter、recipe 和 style 产生了有价值的结果。 |
| Maturity | `foundation-needed` |
| Horizon | `later` |
| Gate/Prerequisite | Saved specs、generated-code hashes 和 provenance records 稳定到可以保存轻量 session history，且不保存原始数据。 |

| Field | Value |
| --- | --- |
| Theme | Exploration workspace |
| Initiative | 增加 parameter sweeps，用于 bin size、smoothing、normalization、aggregation level、filter、time window、scale 和 error style 等常见分析选择。 |
| Why it matters | 研究者需要先判断结论是否经得起合理参数变化，再投入 publication polish。 |
| Maturity | `exploratory` |
| Horizon | `later` |
| Gate/Prerequisite | Sweep results 可以表示为可复现 specs、result cards 或 generated Matplotlib code，而不是隐藏在 browser-only state 中。 |

| Field | Value |
| --- | --- |
| Theme | Exploration workspace |
| Initiative | 增加 object drill-down、from-plot data selection、selected-vs-rest comparison 和基础 data hierarchy warnings。 |
| Why it matters | 用户应该能从点、曲线或 panel 反查对象，并发现 outliers、scale traps、imbalance 或 pseudoreplication risks。 |
| Maturity | `exploratory` |
| Horizon | `later` |
| Gate/Prerequisite | Data previews 和 warnings 保持 advisory、deterministic 且 non-mutating。 |

## Publication Workflow

| Field | Value |
| --- | --- |
| Theme | Publication workflow |
| Initiative | 用 README screenshots 和短 workflow GIFs 扩展 gallery discoverability。 |
| Why it matters | 用户需要在打开完整文档前，快速看到 source data 如何走到可见 preview、generated code 和 export artifacts。 |
| Maturity | `ready` |
| Horizon | `near` |
| Gate/Prerequisite | Gallery assets 继续可以由 source scripts 和 portable specs 复现。 |

| Field | Value |
| --- | --- |
| Theme | Publication workflow |
| Initiative | 扩展 publication-readiness export checks。 |
| Why it matters | 缺少 figure intent、final-size typography 不可读、vector text 不可编辑、panel labels 薄弱、legend 或 label overlap、statistics/source data 不可追踪、spec/code sync 过期和 recipe errors 都是常见最后一公里问题。 |
| Maturity | `ready` |
| Horizon | `near` |
| Gate/Prerequisite | Checks 是 advisory 且 deterministic，并有清楚的 issue definitions，不引入隐藏的 journal-specific 或 AI judgment。 |

## AI-Compatible Handoff And Provenance

| Field | Value |
| --- | --- |
| Theme | AI-compatible handoff and provenance |
| Initiative | 增加不内置模型调用的 deterministic AI-compatible handoff。 |
| Why it matters | 外部 agent 可以基于 figure-contract-style reasoning 提出 `FigureSpec` 或 patch changes，但 FigStudio 仍然是确定性的 validator、previewer、differ 和 applier。 |
| Maturity | `foundation-needed` |
| Horizon | `later` |
| Readiness | Spec diff/apply UX 和 patch acceptance 规则仍是前置条件。 |
| Gate/Prerequisite | 导入 `FigureSpec` 或 patch，显示 spec diff，validate，preview，并让用户 apply 或 reject 修改。 |

| Field | Value |
| --- | --- |
| Theme | AI-compatible handoff and provenance |
| Initiative | 增加 figure manifests 和 provenance records。 |
| Why it matters | 当 manifests 记录 figure intent、FigStudio version、source script、data summaries、recipe semantics、export formats、generated-code hash 和 readiness-check results 时，可复现性更强。 |
| Maturity | `foundation-needed` |
| Horizon | `later` |
| Readiness | Generated-code hashing 与 source/session provenance 仍是下一步前置条件。 |
| Gate/Prerequisite | `FigureSpec` versioning、generated-code hashing 和 advisory readiness-check definitions 稳定。 |

## Ecosystem And Templates

| Field | Value |
| --- | --- |
| Theme | Ecosystem and templates |
| Initiative | 增加面向 neuroscience、image panels、matrix/heatmap workflows、time series 和其他领域图形约定的 recipe/template packs。 |
| Why it matters | Domain packs 应该复用稳定 primitives，而不是变成多个独立产品。 |
| Maturity | `foundation-needed` |
| Horizon | `later` |
| Readiness | 更广的 domain packs 仍需要更多 fixtures、loading rules 和 compatibility expectations。 |
| Gate/Prerequisite | Domain packs 复用稳定的跨领域 primitives，且不变成多个独立产品。 |

| Field | Value |
| --- | --- |
| Theme | Ecosystem and templates |
| Initiative | 扩展 bundled experimental neuroscience 覆盖范围，再考虑可选 `figstudio-neuro` distribution。 |
| Why it matters | Neuroscience surface 应先验证 recipe contracts、gallery examples 和 package loading，再拆分 distribution。 |
| Maturity | `exploratory` |
| Horizon | `later` |
| Readiness | 在 broader pack loading 和更多 gallery evidence 出现前保持 bundled experimental。 |
| Gate/Prerequisite | Neuroscience 保持子领域组织：`neuro.core`、`neuro.ephys` 和 `neuro.neuroimaging`。 |

## Product Ergonomics And Operations

| Field | Value |
| --- | --- |
| Theme | Product ergonomics and operations |
| Initiative | 增加更深入的 editing ergonomics，例如 undo/redo history、scoped command-palette actions 和 selected-object operations。 |
| Why it matters | Richer editing 应该等常见 workflow 保持确定性之后再推进。 |
| Maturity | `exploratory` |
| Horizon | `later` |
| Gate/Prerequisite | Core editing 和 generated-code flows 保持可预测。 |

| Field | Value |
| --- | --- |
| Theme | Product ergonomics and operations |
| Initiative | 增加可选 project-level templates，用于 figure style governance。 |
| Why it matters | Style profiles 被验证后，团队可能需要共享 figure conventions。 |
| Maturity | `exploratory` |
| Horizon | `later` |
| Gate/Prerequisite | 当前 style profiles 在 project workflows 中证明稳定。 |

| Field | Value |
| --- | --- |
| Theme | Product ergonomics and operations |
| Initiative | 随依赖变化监控 startup 和 bundle size trends。 |
| Why it matters | Runtime installs 必须继续使用 packaged editor，不能要求 frontend tooling 或引入明显 startup cost。 |
| Maturity | `ready` |
| Horizon | `near` |
| Gate/Prerequisite | Bundle 和 smoke checks 仍然属于 release evidence。 |
