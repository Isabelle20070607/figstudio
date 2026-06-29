# 发布说明 / What's New

本页面向用户总结已经发布的 FigStudio 版本。完整时间线和发布证据见
[CHANGELOG.md](../../../CHANGELOG.md)。

## 0.4.0 - 2026-06-29

重点：更完整的科研图 authoring、更多内置 recipes、gallery 证据和 headless
automation。

新增内容：

- Repeated panels 现在可以来自 DataFrame facets、mapping keys 或 sequence
  items，同时 generated code 仍保持纯 Matplotlib。
- Plot layers 可以使用右侧 secondary Y axis，用于 raw traces 加 summary
  rates 这类 overlay。
- 新增内置 recipes 覆盖 categorical bars、count bars、stacked bars、grouped
  boxplots、grouped violins、ECDF distribution inspection，以及第一个实验性
  `neuro.ephys.event_rate_timecourse` workflow。
- Recipe 和 layer catalogs 现在为 editor、validation、generated code 和 API
  clients 暴露结构化 metadata。
- CLI 现在支持对 `.figstudio.json` specs 执行确定性的 `validate`、`render`、
  `export` 和 `codegen` commands。
- Gallery 现在包含 repeated panels、secondary axes、category distributions、
  ECDF、stacked composition、GridSpec spans 和 neuro ephys event rates 的
  source scripts、portable specs 与 SVG 证据。
- Publication-readiness advisories 会在 export 前捕捉更多最后一公里问题，
  包括缺少 data-bearing content、labels 薄弱、legend 拥挤和低分辨率 PNG
  settings。
- Notebook-style sessions 的 prepare-cell handoff 更顺滑，同时仍不会静默修改
  notebook 文件。

升级说明：

- 现有 `.figstudio.json` specs 继续兼容。
- Active roadmap docs 现在只保留未来工作；已发布的 0.4.0 内容记录在本页和
  `CHANGELOG.md`。
- 使用 `pip install --upgrade figstudio` 安装最新已发布 wheel。

## 0.3.1 - 2026-06-18

重点：validation repair suggestions 和桌面 workspace 适配。

新增内容：

- Validation issue cards 现在会优先显示后端推断出的 `Suggested fix: ...`
  修复建议。
- 缺失变量、缺失 DataFrame columns、缺失 axes、无效 panel layout spans、
  缺失 style profile 和 log-scale 非正数据现在会给出更可执行的修复说明。
- Validation payloads 可以携带有限上下文，例如 available variables、
  DataFrame columns、axes ids、profile ids 和 suggested replacement value。
- 桌面全屏会把 editor shell 限制在 viewport 内，滚动留在 preview 区域，
  不再让整个页面下滚才能看到 code panel。
- Browser smoke tests 现在会防止 desktop code panel 掉到 viewport 外。

升级说明：

- 现有 `.figstudio.json` specs 继续兼容。
- 使用 `pip install --upgrade figstudio` 安装最新已发布 wheel。

## 0.3.0 - 2026-06-18

重点：style governance、panel layouts、双语文档和发布稳定性。

新增内容：

- 项目可以在 `.figstudio/styles.json` 中定义共享样式默认值。
- `figstudio.open(..., project_path=...)`、CLI `--project` 和
  `GET /api/style-profiles` 可以暴露当前项目 style profile 根目录。
- Spec 可以引用 `style.profile_id`，并用 `style.profile_overrides` 记录
  手动覆盖字段，而不是把所有默认值复制进 spec。
- Render、export 和 generated code 会解析 project profile 中的 figure、
  layer 和 recipe 样式默认值。
- Panel layout presets 支持通过 `rowspan` 和 `colspan` 跨行/跨列；
  generated code 只在需要时使用 `GridSpec`。
- 文档拆分成结构成对的 English 和 Chinese 文档树。
- Browser smoke 覆盖了真实 project style profile fixture。

升级说明：

- 不使用 profiles 的旧 specs 继续可用。
- 如果 spec 引用了不存在的 profile，FigStudio 会给出 warning，并回退到
  spec 显式值和默认值。
- 使用 `pip install --upgrade figstudio` 安装最新已发布 wheel。

## 0.2.0 - 2026-06-17

重点：面向 pandas DataFrame 的 general statistics recipes。

新增内容：

- 增加三个内置 recipe kinds：`mean_sem_line`、`grouped_points` 和
  `paired_before_after`。
- Editor 增加 recipe builder，用于选择 DataFrame、columns、grouping、
  subject identifiers、error style 和 target axes。
- Generated recipe code 仍然是纯 Matplotlib，并从用户已有 DataFrame 变量
  中计算统计量。
- Recipe validation 会在 render/export 前报告 non-DataFrame source 和
  missing columns。
- 增加 `examples/general_stats_recipe.py` 和 recipe smoke coverage。

升级说明：

- Recipes 需要 pandas DataFrame 输入。
- Recipe specs 保存 variable names、column mappings、style、target axes 和
  recipe kind，不保存原始 DataFrame data。

## 0.1.0 - 2026-06-16

重点：首次发布 public beta 到 PyPI。

新增内容：

- 可安装 package，包含 `figstudio.open(...)`、`figstudio demo` 和
  `figstudio --version`。
- 本地浏览器 editor 从 Python wheel 提供；用户运行时不需要 Node/npm。
- 支持常见 Scientific Python 数据对象的 variable summaries，并支持
  best-effort existing Matplotlib figure inspection。
- Public beta plot layers、Matplotlib preview、generated code panel、PNG/SVG/PDF
  export，以及 FigureSpec JSON import/export。
- 安全 script writeback，只替换一个受控 marker block。
- Notebook 风格 session 返回 replacement cell code，不直接修改 notebook 文件。
- CI 和 release workflows 覆盖 PyPI/TestPyPI 发布、bundle check、clean
  install smoke 和 browser smoke。

升级说明：

- 首次公开安装方式：`pip install figstudio`。
- Generated plotting code 运行时不需要 import FigStudio。
