# 路线图 Initiatives

本页按产品主题组织未来 roadmap 工作。它不是发布计划；maturity 和 horizon 标签用来说明准备程度和大致排序。

## Scientific Authoring Primitives

| Field | Value |
| --- | --- |
| Theme | Scientific authoring primitives |
| Initiative | 把 small-multiple 或 faceted panel authoring 扩展到 mapping keys 或 sequence items。 |
| Status | 已在 beta 中完成。 |
| Completion note | 普通 plot layers 可以按 DataFrame values、literal-safe mapping keys 或 sequence indices 拆分 repeated panels；statistics recipes 仍保持 DataFrame-only。 |

| Field | Value |
| --- | --- |
| Theme | Scientific authoring primitives |
| Initiative | 增加 secondary y-axis 支持，用于 raw events 加 summary rates 这类 overlay。 |
| Status | 已在 beta 中完成。 |
| Completion note | Plot layers 可以在同一 panel 上选择 left 或 right Y axis；右侧 axis 支持 label、scale、limits、validation、Matplotlib `twinx()` codegen 和 JSON round-trip。Recipes 和 reference lines 仍保持 primary-axis scope。 |

| Field | Value |
| --- | --- |
| Theme | Scientific authoring primitives |
| Initiative | 探索完整 `subplot_mosaic` authoring。 |
| Why it matters | Mosaic layouts 可以表达超过 named presets 的发表图版结构。 |
| Maturity | `exploratory` |
| Horizon | `later` |
| Gate/Prerequisite | Preset-backed GridSpec panel layouts 在真实 workflow 中证明稳定。 |

## Recipe And Statistical Coverage

| Field | Value |
| --- | --- |
| Theme | Recipe and statistical coverage |
| Initiative | 增加 categorical summary recipes，例如 grouped bars、stacked bars、count bars、bar-with-error panels，以及 point/box/violin overlays。 |
| Why it matters | 这些覆盖常见科研论文图形，同时避免扩张成泛 business dashboard。 |
| Maturity | `foundation-needed` |
| Horizon | `near` |
| Progress | Beta slices 已增加 `mean_sem_bar` 用于 mean-plus-error 分类柱状图，并增加 `count_bar` 用于 ungrouped 或 grouped 频数柱状图；stacked bars 和 distribution overlays 仍是未来工作。 |
| Gate/Prerequisite | Shared recipe roles 和 validation errors 清楚到足以承载多个 recipe families。 |

| Field | Value |
| --- | --- |
| Theme | Recipe and statistical coverage |
| Initiative | 增加 distribution 和 relationship recipes：带 fitted trend 的 regression scatter、confidence 或 percentile bands、ECDF、two-dimensional histograms、hexbin summaries，以及更强的 heatmap 或 matrix controls。 |
| Why it matters | 这些补齐 exploratory 和 manuscript figures 中高价值的可复现 Matplotlib workflows。 |
| Maturity | `foundation-needed` |
| Horizon | `later` |
| Gate/Prerequisite | 随着 recipe 复杂度增长，generated-code templates 和 recipe validation 仍然可读。 |

| Field | Value |
| --- | --- |
| Theme | Recipe and statistical coverage |
| Initiative | 当 recoverable data 足够时，把 existing Figure inspection 扩展为 editable statistical recipes。 |
| Why it matters | 只有当 FigStudio 能保留可复现性时，用户才应继续编辑受支持的已有图形。 |
| Maturity | `exploratory` |
| Horizon | `later` |
| Gate/Prerequisite | Matplotlib 为相关 artists 暴露足够 raw 或 reproducible data。 |

## Publication Workflow

| Field | Value |
| --- | --- |
| Theme | Publication workflow |
| Initiative | 建立真实 example gallery、README screenshots 和短 workflow GIFs。 |
| Why it matters | 用户需要接近真实生产场景的证据，展示 plot layers、statistics recipes、existing Figure inspection、notebook-style output 和 package install flows 如何从 source data 走到可见 preview 与 export artifacts。 |
| Maturity | `ready` |
| Horizon | `near` |
| Gate/Prerequisite | 每个例子展示 input data、user intent 或 figure contract、preview screenshot、generated Matplotlib code、FigureSpec/export artifact，以及它证明的 publication workflow。 |

| Field | Value |
| --- | --- |
| Theme | Publication workflow |
| Initiative | 增加 publication-readiness export checks。 |
| Why it matters | 缺少 figure intent、final-size typography 不可读、vector text 不可编辑、panel labels 薄弱、legend 或 label overlap、statistics/source data 不可追踪、spec/code sync 过期和 recipe errors 都是常见最后一公里问题。 |
| Maturity | `foundation-needed` |
| Horizon | `near` |
| Progress | 第一个 advisory slice 覆盖没有 data-bearing 图层或 recipe、缺少 primary/secondary axis labels、multi-item axes 缺少 legend labels，以及 PNG export 分辨率偏低。 |
| Gate/Prerequisite | Checks 是 advisory 且 deterministic，并有清楚的 issue definitions，不引入隐藏的 journal-specific 或 AI judgment。 |

| Field | Value |
| --- | --- |
| Theme | Publication workflow |
| Initiative | 加强 notebook copy 和 cell-output ergonomics。 |
| Why it matters | Notebook 用户需要更顺滑的 handoff，同时保留对 file mutation 的控制。 |
| Maturity | `foundation-needed` |
| Horizon | `near` |
| Gate/Prerequisite | Notebook workflow 继续返回 replacement code，而不是 silent edit notebook files。 |

## AI-Compatible Handoff And Provenance

| Field | Value |
| --- | --- |
| Theme | AI-compatible handoff and provenance |
| Initiative | 增加不内置模型调用的 deterministic AI-compatible handoff。 |
| Why it matters | 外部 agent 可以基于 figure-contract-style reasoning 提出 `FigureSpec` 或 patch changes，但 FigStudio 仍然是确定性的 validator、previewer、differ 和 applier。 |
| Maturity | `foundation-needed` |
| Horizon | `later` |
| Gate/Prerequisite | 导入 `FigureSpec` 或 patch，显示 spec diff，validate，preview，并让用户 apply 或 reject 修改。 |

| Field | Value |
| --- | --- |
| Theme | AI-compatible handoff and provenance |
| Initiative | 增加 figure manifests 和 provenance records。 |
| Why it matters | 当 manifests 记录 figure intent、FigStudio version、source script、data summaries、recipe semantics、export formats、generated-code hash 和 readiness-check results 时，可复现性更强。 |
| Maturity | `foundation-needed` |
| Horizon | `later` |
| Gate/Prerequisite | `FigureSpec` versioning、generated-code hashing 和 advisory readiness-check definitions 稳定。 |

| Field | Value |
| --- | --- |
| Theme | AI-compatible handoff and provenance |
| Initiative | 增加面向 agent 的 headless `validate`、`render`、`export`、`codegen` commands。 |
| Why it matters | Interactive contract 稳定后，automation 需要确定性的 command surfaces。 |
| Maturity | `foundation-needed` |
| Horizon | `later` |
| Gate/Prerequisite | `FigureSpec` 和 patch contracts 保持稳定。 |

## Ecosystem And Templates

| Field | Value |
| --- | --- |
| Theme | Ecosystem and templates |
| Initiative | 准备 recipe/template pack substrate。 |
| Why it matters | Namespaced recipe IDs、reusable chart-family roles、shared role schemas、validation hooks、generated-code templates、style defaults、gallery fixtures 和 import/export compatibility 应该在外部或领域专用 packs 前存在。 |
| Maturity | `foundation-needed` |
| Horizon | `near` |
| Gate/Prerequisite | Bundled recipes 和 gallery fixtures 有足够共享结构，避免过早冻结脆弱 extension contract。 |

| Field | Value |
| --- | --- |
| Theme | Ecosystem and templates |
| Initiative | 增加面向 neuroscience、image panels、matrix/heatmap workflows、time series 和其他领域图形约定的 recipe/template packs。 |
| Why it matters | Domain packs 应该复用稳定 primitives，而不是变成多个独立产品。 |
| Maturity | `exploratory` |
| Horizon | `later` |
| Gate/Prerequisite | Reference-line、repeated-panel、secondary-axis 和 scientific-summary primitives 能承载通用结构。 |

| Field | Value |
| --- | --- |
| Theme | Ecosystem and templates |
| Initiative | 先从 bundled experimental neuroscience pack 开始，再考虑可选 `figstudio-neuro` distribution。 |
| Why it matters | Neuroscience surface 应先验证 recipe contracts、gallery examples 和 package loading，再拆分 distribution。 |
| Maturity | `exploratory` |
| Horizon | `later` |
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
