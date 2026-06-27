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
| Initiative | 增加 automatic repeated-panel layout optimization，作为初始 layout suggestion。 |
| Status | 已在 beta 中完成。 |
| Completion note | Facet 和 repeated-panel builders 现在会根据 panel 数量与当前 figure aspect 选择紧凑、无重叠的初始 rows/columns，同时仍只输出已有 `FigureSpec.rows`、`FigureSpec.cols` 和单 cell `AxesSpec` geometry。 |

| Field | Value |
| --- | --- |
| Theme | Scientific authoring primitives |
| Initiative | 探索完整 `subplot_mosaic` authoring。 |
| Why it matters | Mosaic layouts 可以表达超过 named presets 的发表图版结构。 |
| Maturity | `exploratory` |
| Horizon | `later` |
| Readiness | GridSpec、span validation 和 gallery proof 已经让可行性更清楚，但 mosaic syntax 仍会引入新的 public layout authoring surface。 |
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
| Initiative | 围绕科研问题组织 analysis recipes，例如 group comparison、paired conditions、time course comparison、distribution inspection、relationships，以及 matrix 或 heatmap review。 |
| Why it matters | 用户探索科研数据时首先是在问问题，而不是先选择 chart primitives。 |
| Status | 已在 beta 中完成。 |
| Completion note | Recipe builder 现在围绕 time-course comparison、group/condition comparison、categorical counts/composition 和 paired observations 组织已上线 recipes，同时保持现有 `RecipeLayer.kind`、dataset-role validation 和 pure Matplotlib codegen contracts。 |

| Field | Value |
| --- | --- |
| Theme | Recipe and statistical coverage |
| Initiative | 增加 categorical summary recipes，例如 grouped bars、stacked bars、count bars、bar-with-error panels，以及 point/box/violin overlays。 |
| Why it matters | 这些覆盖常见科研论文图形，同时避免扩张成泛 business dashboard。 |
| Status | 已在 beta 中完成。 |
| Completion note | Beta slices 已增加 `mean_sem_bar` 用于 mean-plus-error 分类柱状图，增加 `count_bar` 用于 ungrouped 或 grouped 频数柱状图，增加 `stacked_bar` 用于 grouped stacked 频数柱状图，增加 `boxplot_by_category` 用于 grouped value distributions，并增加 `violin_by_category` 用于 grouped violin distributions。 |

| Field | Value |
| --- | --- |
| Theme | Recipe and statistical coverage |
| Initiative | 增加 distribution 和 relationship recipes：带 fitted trend 的 regression scatter、confidence 或 percentile bands、ECDF、two-dimensional histograms、hexbin summaries，以及更强的 heatmap 或 matrix controls。 |
| Why it matters | 这些补齐 exploratory 和 manuscript figures 中高价值的可复现 Matplotlib workflows。 |
| Maturity | `foundation-needed` |
| Horizon | `later` |
| Progress | `ecdf` 现在作为第一个完成的 distribution-recipe slice，覆盖了带可选分组的 empirical distribution inspection。 |
| Readiness | 现有 recipe dispatch、dataset-role validation 和 generated-code templates 降低了实现风险；剩余风险在 fitted trends、bands、binning、hexbin summaries 和 matrix controls 的统计语义。 |
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
| Initiative | 建立真实 example gallery、README screenshots 和短 workflow GIFs。 |
| Why it matters | 用户需要接近真实生产场景的证据，展示 plot layers、statistics recipes、existing Figure inspection、notebook-style output 和 package install flows 如何从 source data 走到可见 preview 与 export artifacts。 |
| Maturity | `ready` |
| Horizon | `near` |
| Progress | 已提交 gallery workflows 现在覆盖 DataFrame facet recipes、category boxplot 和 violin distributions、ECDF distributions、stacked categorical composition、secondary-axis overlays、GridSpec spans、reference lines、annotations、reusable specs 和 SVG preview assets。 |
| Gate/Prerequisite | 每个例子展示 input data、user intent 或 figure contract、preview screenshot、generated Matplotlib code、FigureSpec/export artifact，以及它证明的 publication workflow。 |

| Field | Value |
| --- | --- |
| Theme | Publication workflow |
| Initiative | 增加 publication-readiness export checks。 |
| Why it matters | 缺少 figure intent、final-size typography 不可读、vector text 不可编辑、panel labels 薄弱、legend 或 label overlap、statistics/source data 不可追踪、spec/code sync 过期和 recipe errors 都是常见最后一公里问题。 |
| Maturity | `ready` |
| Horizon | `near` |
| Progress | Advisory checks 现在覆盖没有 data-bearing 图层或 recipe、缺少 primary/secondary axis labels、multi-panel titles 薄弱、multi-item axes 缺少 legend labels、受限 panel 中 crowded legend 的 overlap risk，以及 PNG export 分辨率偏低。 |
| Readiness | Export-context advisory warnings 已经在 content、label、legend 和 PNG export settings 上验证；后续 final-mile checks 可以复用同一 validation contract。 |
| Gate/Prerequisite | Checks 是 advisory 且 deterministic，并有清楚的 issue definitions，不引入隐藏的 journal-specific 或 AI judgment。 |

| Field | Value |
| --- | --- |
| Theme | Publication workflow |
| Initiative | 加强 notebook copy 和 cell-output ergonomics。 |
| Why it matters | Notebook 用户需要更顺滑的 handoff，同时保留对 file mutation 的控制。 |
| Status | 已在 beta 中完成。 |
| Completion note | No-script 和 notebook-style sessions 现在提供 mode-aware **Prepare cell** action；save 后 code panel 会切换为 **Notebook replacement cell**，提供 replacement cell 的 copy action，并在后续 spec edits 后回到 generated-code preview，同时仍不修改 notebook 文件。 |

## AI-Compatible Handoff And Provenance

| Field | Value |
| --- | --- |
| Theme | AI-compatible handoff and provenance |
| Initiative | 增加不内置模型调用的 deterministic AI-compatible handoff。 |
| Why it matters | 外部 agent 可以基于 figure-contract-style reasoning 提出 `FigureSpec` 或 patch changes，但 FigStudio 仍然是确定性的 validator、previewer、differ 和 applier。 |
| Maturity | `foundation-needed` |
| Horizon | `later` |
| Readiness | Headless validate、render、export 和 codegen commands 现在提供了面向外部 agents 的确定性 automation endpoints；spec diff/apply UX 和 patch acceptance 仍是前置条件。 |
| Gate/Prerequisite | 导入 `FigureSpec` 或 patch，显示 spec diff，validate，preview，并让用户 apply 或 reject 修改。 |

| Field | Value |
| --- | --- |
| Theme | AI-compatible handoff and provenance |
| Initiative | 增加 figure manifests 和 provenance records。 |
| Why it matters | 当 manifests 记录 figure intent、FigStudio version、source script、data summaries、recipe semantics、export formats、generated-code hash 和 readiness-check results 时，可复现性更强。 |
| Maturity | `foundation-needed` |
| Horizon | `later` |
| Readiness | Readiness warning codes 和导出的 `FigureSpec` artifacts 现在提供可写入 manifest 的事实；generated-code hashing 与 source/session provenance 仍是下一步前置条件。 |
| Gate/Prerequisite | `FigureSpec` versioning、generated-code hashing 和 advisory readiness-check definitions 稳定。 |

| Field | Value |
| --- | --- |
| Theme | AI-compatible handoff and provenance |
| Initiative | 增加面向 agent 的 headless `validate`、`render`、`export`、`codegen` commands。 |
| Why it matters | Interactive contract 稳定后，automation 需要确定性的 command surfaces。 |
| Status | 已在 beta 中完成。 |
| Completion note | CLI 现在支持对 `.figstudio.json` specs 执行一次性的 `codegen`、`validate`、`render` 和 `export` commands。依赖数据的 commands 会执行显式可信 `--data-script` namespace，可在可能时从 output suffix 推断格式，并返回确定性的 exit codes。Patch diff/apply 仍属于 deterministic AI handoff，而不是本 command-wrapper slice。 |

## Ecosystem And Templates

| Field | Value |
| --- | --- |
| Theme | Ecosystem and templates |
| Initiative | 准备 recipe/template pack substrate。 |
| Why it matters | Namespaced recipe IDs、reusable chart-family roles、shared role schemas、validation hooks、generated-code templates、style defaults、gallery fixtures 和 import/export compatibility 应该在外部或领域专用 packs 前存在。 |
| Maturity | `ready` |
| Horizon | `near` |
| Progress | Bundled plot layers 以及 line、categorical、distribution-inspection、distribution-summary 和 paired-observation recipes 现在共享 internal registries。这些 registries 驱动 validation capability、generated-code dispatch、UI selectors、tests、gallery-backed workflows、`GET /api/layer-catalog` 和 `GET /api/recipe-catalog` metadata，用于描述 groups、field roles、labels、legend behavior 和默认 styles。 |
| Readiness | Bundled registries 建立了内部 pack substrate，但还不承诺外部 pack files、plugin loading 或 dynamic recipe/layer kinds。 |
| Gate/Prerequisite | Bundled recipes 和 gallery fixtures 有足够共享结构，避免过早冻结脆弱 extension contract。 |

| Field | Value |
| --- | --- |
| Theme | Ecosystem and templates |
| Initiative | 增加面向 neuroscience、image panels、matrix/heatmap workflows、time series 和其他领域图形约定的 recipe/template packs。 |
| Why it matters | Domain packs 应该复用稳定 primitives，而不是变成多个独立产品。 |
| Maturity | `foundation-needed` |
| Horizon | `later` |
| Readiness | Reference lines、repeated panels、secondary axes 和 scientific-summary recipes 已是 beta primitives；剩余前置条件是 pack substrate、domain fixtures 和 loading rules。 |
| Gate/Prerequisite | Reference-line、repeated-panel、secondary-axis 和 scientific-summary primitives 能承载通用结构。 |

| Field | Value |
| --- | --- |
| Theme | Ecosystem and templates |
| Initiative | 先从 bundled experimental neuroscience pack 开始，再考虑可选 `figstudio-neuro` distribution。 |
| Why it matters | Neuroscience surface 应先验证 recipe contracts、gallery examples 和 package loading，再拆分 distribution。 |
| Maturity | `foundation-needed` |
| Horizon | `later` |
| Readiness | `neuro.core` 和 ephys-style overlays 需要的 cross-domain primitives 已经具备；在 pack loading 和 gallery evidence 出现前保持 bundled experimental。 |
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
