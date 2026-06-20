# 产品需求

## 产品定义

FigStudio 是一个 public beta 的本地 figure workflow，用来把 Python 会话中已有的数据转换成可复现、适合发表的 Matplotlib 图版。

用户安装 Python package 后，可从脚本或 Notebook 打开本地浏览器编辑器，应用可选 project style profiles，映射变量、创建 plot layers 或受支持的 statistics recipes、预览真实 Matplotlib 输出、导出文件、保存生成的 OO code，并可把 GUI 会话保存成可移植的 `FigureSpec` JSON 文件。

未来产品方向和候选工作放在 [路线图](roadmap.md)。

## 目标用户

- 已经在脚本或 Notebook 中准备数据、希望更快组装 Matplotlib 图的 Scientific Python 用户。
- 需要发表风格图形且要求 Python 输出可复现的研究者。
- 希望使用 GUI 辅助但仍保留 generated code 控制权的谨慎 Matplotlib 用户。
- 希望共享 figure defaults 但仍允许单图微调的项目团队。
- 希望 wheel 安装后无需 frontend tooling 即可使用 editor UI 的 package 用户。

## Beta 范围

- 可通过 Python package 安装，运行时不需要 Node/npm。
- 通过 `figstudio.open(locals(), ...)` 或 `figstudio demo` 启动。
- 检查 DataFrame、Series、ndarray、mapping、list、tuple 和已有 Matplotlib Figure 的安全 summaries。
- 创建和编辑 public beta plot kinds 和内置 statistics recipes。
- 基于 DataFrame 列首次出现的取值创建 faceted panels，并为普通 plot layers 支持 mapping-key 和 sequence-index repeated panels。
- 配置 manuscript presets、project style profiles、panel layouts、axes settings、layer styles、reference lines 和 text/arrow annotations。
- 加载 `.figstudio/styles.json` project style profiles，并在 `FigureSpec` 中保存 profile references 和 explicit override fields。
- 用 Matplotlib Agg 生成 previews 和 exports。
- 将 generated code 写入唯一受控脚本块，或返回 notebook replacement code。
- 导入和导出 `.figstudio.json` session specs。
- Specs 保存 recipe intent、column mappings、facet equality filters 和 repeated-panel selections，不保存原始数据。
- 当 live session 提供足够上下文时，validation issue cards 会显示 field-level repair suggestions。

## 用户故事

- 作为 Scientific Python 用户，我希望从 `locals()` 打开 editor，以复用已经准备好的数据。
- 作为研究者，我希望使用 manuscript presets 和 annotation controls，更快准备发表风格图形。
- 作为研究者，我希望添加 baseline 和 threshold reference lines，让常见科学 cutoffs 可见，而不需要把它们伪装成 data layers。
- 作为研究者，我希望按 condition 列把 DataFrame plot 或 recipe 拆成 small multiples，而不需要手动创建每个 axes。
- 作为研究者，我希望在准备好的数据已经按 mapping 或 sequence 分组时，也能按 keys 或 items 拆分普通 plot layers。
- 作为项目维护者，我希望共享 style profiles，让图形继承项目 defaults，同时记录 explicit overrides。
- 作为谨慎的脚本用户，我希望 writeback 只发生在 marker block 里，不影响数据处理代码。
- 作为 Notebook 用户，我希望得到 replacement cell code，而不是自动修改 Notebook。
- 作为 Matplotlib 用户，我希望 generated code 不需要 import FigStudio 就能运行。
- 作为回访用户，我希望通过 FigureSpec JSON import/export，在兼容数据下继续 GUI editing session。

## 验收标准

- 脚本能启动 FigStudio，创建 DataFrame plot 或 statistics recipe，渲染 preview，并把代码写回 controlled block。
- 不提供 `script_path` 的 Notebook 风格会话能返回完整 replacement code。
- Generated code 只 import Matplotlib，并能在相同用户变量下运行。
- PNG、SVG、PDF 导出来自 Matplotlib。
- Reference lines 会生成 Matplotlib `axhline` 或 `axvline` 代码，并能通过 `.figstudio.json` 往返保存。
- DataFrame facet panels 会生成带过滤的 Matplotlib code，保留 shared-axis flags，并能通过 `.figstudio.json` 往返保存。
- Mapping-key 和 sequence-index repeated panels 会生成 selected-item Matplotlib code，并能通过 `.figstudio.json` 往返保存。
- Validation、render、export 和 writeback failures 返回可读 structured errors，并为常见 validation issues 提供 repair suggestions。
- Existing Figure inspection 能把受支持的 line、scatter、image 和 bar data 保留为 editable generated layers。
- 构建后的 wheel 包含 React editor，clean install 后可从 `127.0.0.1` 提供完整 UI。
- `figstudio.load_spec()` 和 `figstudio.save_spec()` 能往返保存 `.figstudio.json` 文件。

## 非目标

- Cloud accounts、collaboration 或 hosted dashboards。
- 自动重写任意用户 Matplotlib source code。
- 直接修改 Notebook 文件。
- 完整支持所有 Matplotlib artist、3D、polar plots、animation 或 interactive web publishing。
- 内置 general statistics recipes 之外的 domain-specific recipe packs。
- Public beta 阶段的 desktop installers。

## 产品质量门槛

- Editor 必须保持 local-first，并默认绑定到 `127.0.0.1`。
- Generated plotting code 必须保持为易读 Matplotlib OO code。
- Project style governance 必须保持 reference-based。
- 当无法安全识别 controlled block 时，writeback 必须 fail closed。
- 文档必须区分当前 beta behavior 和 roadmap items。
