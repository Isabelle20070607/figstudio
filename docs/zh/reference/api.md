# API 参考

本文档记录当前 public beta API surface。未来能力放在 [路线图](../product/roadmap.md)。

## Python API

```python
figstudio.open(
    namespace=None,
    *,
    figure=None,
    script_path=None,
    project_path=None,
    block_id="main",
    mode="auto",
    open_browser=True,
) -> FigStudioSession
```

| 参数 | 含义 |
| --- | --- |
| `namespace` | 通常传入 `locals()`。受支持的公开变量会摘要给 UI；真实对象留在服务端。 |
| `figure` | 可选 Matplotlib `Figure`，用于 best-effort inspection。 |
| `script_path` | 启用 `.py` 文件受控写回。 |
| `project_path` | `.figstudio/styles.json` 的项目根目录；默认是 `Path(script_path).parent` 或当前工作目录。 |
| `block_id` | 选择 `# figstudio:start <block_id>` 和 `# figstudio:end <block_id>`。 |
| `mode` | 用于 editor mode selection 的 session metadata。 |
| `open_browser` | 为 true 时打开本地 editor URL。 |

```python
figstudio.save_spec(spec, path) -> pathlib.Path
figstudio.load_spec(path) -> FigureSpec
```

`save_spec` 接受 `FigureSpec` 或兼容 dict，并写出 UTF-8 JSON。`load_spec` 会把 JSON 校验为 `FigureSpec`。

## CLI

```powershell
figstudio --version
figstudio --no-browser
figstudio --port 8767 --no-browser
figstudio --project G:\workspace\figstudio --no-browser
figstudio demo
figstudio demo --project G:\workspace\figstudio --port 8767 --no-browser
figstudio codegen figure.figstudio.json --output figure.py
figstudio validate figure.figstudio.json --data-script data.py --context export --export-format svg --json
figstudio render figure.figstudio.json --data-script data.py --output preview.svg
figstudio export figure.figstudio.json --data-script data.py --output figure.pdf
```

Session commands 会打印 session URL，并持续运行直到被中断。Headless commands 会执行一次后退出：

- `codegen` 读取 `.figstudio.json` spec，并把生成的 Matplotlib code 写到 stdout 或 `--output`。
- `validate` 基于可选的可信 `--data-script` namespace 校验 spec，validation errors 返回 exit `1`。
- `render` 基于 spec 和可信 `--data-script` 写出 SVG 或 PNG preview。
- `export` 基于 spec 和可信 `--data-script` 用 export-context validation 写出 PNG、SVG 或 PDF。

`--data-script` 会在当前进程执行可信 Python code，并把它的 globals 作为 live namespace。只对自己控制的脚本使用它。`render` 和 `export` 在省略 `--format` 时会从 `--output` 推断格式；不支持或缺失 suffix 会返回 exit `2`。Exit codes：成功或仅有 warnings 为 `0`，validation errors 为 `1`，CLI usage、input 或 runtime failures 为 `2`。

## FigureSpec

`FigureSpec` 是可 JSON 序列化的 editor state，也是 codegen 输入。

| 字段 | 含义 |
| --- | --- |
| `version` | Spec 格式标记，当前默认 `1`。 |
| `mode` | `explore` 或 `publish`。 |
| `width`, `height`, `dpi` | Figure size 和 render/export DPI。 |
| `rows`, `cols`, `share_x`, `share_y`, `axes` | Panel layout grid、shared-axis flags、axes geometry，以及 primary/secondary axis metadata。 |
| `layers` | Plot layer definitions。 |
| `recipes` | Statistics recipe definitions。 |
| `reference_lines` | 用于 baselines、thresholds 和 cutoff labels 的 horizontal/vertical guide lines。 |
| `annotations` | Text 和 arrow annotations。 |
| `style` | Figure title、font、layout、built-in preset 和 project profile reference。 |
| `show` | 生成代码是否调用 `plt.show()`。 |

支持的 `PlotLayer.kind` 值为 `line`、`scatter`、`bar`、`barh`、`hist`、`boxplot`、`violin`、`errorbar`、`heatmap`、`contour`、`step` 和 `fill_between`。

`PlotLayer.y_axis` 默认是 `left`。把它设为 `right` 可在同一个 `axes_id` 上创建简单 secondary Y-axis overlay；`AxesSpec.secondary_y` 保存右侧 `ylabel`、`yscale` 和 `ylim`。当某个 panel 至少有一个 right-axis layer 时，生成代码会输出 Matplotlib `twinx()`。

支持的 `RecipeLayer.kind` 值为 `mean_sem_line`、`mean_sem_bar`、`count_bar`、`stacked_bar`、`boxplot_by_category`、`violin_by_category`、`grouped_points`、`paired_before_after` 和 `ecdf`。

`GET /api/recipe-catalog` 会暴露 editor 使用的 bundled recipe catalog。Response 包含 `version`、`groups` 和 `recipes`；每个 recipe entry 记录 `kind`、label、research-question group、role 文案、必需和可选 dataset fields、默认 error 行为、默认 label 行为，以及默认 style。Public beta 中这个 catalog 只描述内置 recipes，不是外部 plugin 或 pack-loading contract。

`ReferenceLineSpec.orientation` 为 `horizontal` 或 `vertical`。`value` 是 numeric value，`style` 复用 plot layer 的 label、color、line style、linewidth 和 alpha 字段。生成代码会输出 Matplotlib `axhline` 或 `axvline`。

`DatasetRef` 字段可通过 `x_variable`、`y_variable`、`z_variable` 和 `yerr_variable` 指向 DataFrame 列或独立变量。普通 plot layer 也可以设置 `DatasetRef.selection`，使用 `kind: "mapping_key"` 或 `kind: "sequence_index"` 在 repeated panels 绘图前选出一个 item。`RecipeDatasetRef.variable` 必须指向 pandas DataFrame，且只保存列名。`boxplot_by_category` 和 `violin_by_category` 要求 `x` 和 `y`，接受可选 `group`，并忽略 `subject` 和 `error`；`ecdf` 要求 `x`，接受可选 `group`，并忽略 `y`、`subject` 和 `error`；`count_bar` 要求 `x`，接受可选 `group`，并忽略 `y`、`subject` 和 `error`；`stacked_bar` 要求 `x` 和 `group`，同样忽略 `y`、`subject` 和 `error`。两种 dataset ref 都可以包含 `filters`；每个 `DataFilterSpec` 保存 `column`、`op: "eq"`、`value` 和可选 `label`，用于 DataFrame-backed facet panels。

`FigureStyle.profile_id` 引用项目 style profile。`FigureStyle.profile_overrides` 列出应使用 spec 显式值而不是 profile 默认值的 figure 字段：`width`、`height`、`dpi`、`font_family`、`font_size` 和 `constrained_layout`。

## REST API

本地 FastAPI server 按 session 创建，并默认绑定到 `127.0.0.1`。

| Endpoint | 用途 |
| --- | --- |
| `GET /api/session` | Session metadata、写回能力、可选 inspected figure tree。 |
| `GET /api/variables` | 安全变量摘要。 |
| `GET /api/style-profiles` | 已加载 project style profiles、source path 和非致命 load warnings。 |
| `GET /api/recipe-catalog` | Bundled recipe groups、字段需求、labels 和默认 recipe style metadata。 |
| `GET /api/spec` | 当前 `FigureSpec`。 |
| `POST /api/validate` | 基于 live namespace 校验 `FigureSpec`；可接受 `context: "edit" \| "export"` 和 `export_format`，用于发表准备度预检。 |
| `POST /api/facet-values` | 为 small-multiple panel authoring 返回 DataFrame 中按出现顺序去重的取值。 |
| `POST /api/repeated-panel-candidates` | 为 repeated-panel authoring 返回 DataFrame values、mapping keys 或 sequence indices，以及有界 item summaries。 |
| `POST /api/spec` | 保存当前 spec、校验，并返回 SVG render response。 |
| `POST /api/render` | 渲染 SVG 或 PNG preview。 |
| `POST /api/save-code` | 写入受控脚本块，或返回 notebook replacement code。 |
| `POST /api/export` | 返回 base64 PNG/SVG/PDF export data，或写入明确 output path。 |
| `WS /api/events` | 预留轻量 connected/ack editor events。 |

`POST /api/save-code` 即使 writeback 失败也返回 HTTP 200，以便 response 包含生成代码和 error object。

## Error Payloads

HTTP errors 使用：

```json
{
  "detail": {
    "error": {
      "code": "validation_failed",
      "message": "FigureSpec has validation errors.",
      "details": {}
    }
  }
}
```

当前 error codes 为 `validation_failed`、`render_failed`、`export_failed`、`writeback_failed`、`writeback_io_failed`、`missing_variable`、`missing_column`、`unsupported_facet_source` 和 `unsupported_repeated_panel_source`。Writeback errors 出现在 `SaveCodeResponse.error` 中；render、export、validation、facet-value 和 repeated-panel candidate failures 是 HTTP errors。

Validation issue codes 包括 `missing_style_profile`、`invalid_grid_size`、`duplicate_axes_id`、`invalid_axes_span`、`axes_out_of_bounds`、`axes_overlap`、`missing_axes`、`missing_variable`、`missing_column`、`unsupported_recipe_source`、`unsupported_filter_source`、`empty_filter_result`、`unsupported_selection_source`、`unsupported_selection_key`、`missing_selection_key`、`selection_index_out_of_range`、`unsupported_selected_channel`、`unplottable_selection_value`、`dimension_mismatch`、`requires_2d_data`、`log_scale_non_positive`、`unsupported_secondary_y_layer` 和 `invalid_reference_line_value`。

Export context validation 还可能返回 advisory readiness warnings：`readiness_empty_figure`、`readiness_missing_axis_label`、`readiness_missing_secondary_y_label`、`readiness_weak_panel_label`、`readiness_missing_legend_labels`、`readiness_legend_overlap_risk` 和 `readiness_low_png_resolution`。这些 warning 不会让 `ValidationResponse.ok` 变成 false；除非同时存在普通 validation errors，否则不会阻止 export。

每个 validation issue 可能包含用于 UI repair guidance 的 `suggestion`。`details` 可以包含有界上下文，例如 `available_variables`、`available_columns`、`available_axes`、`available_profiles` 和 `suggested_value`；不会包含原始 DataFrame contents。

## Compatibility Notes

- 生成绘图代码必须能在不 import FigStudio 的情况下运行。
- 生成 recipe code 可以调用现有 pandas DataFrame 变量的方法，但 imports 仍限于 Matplotlib。
- 保存的 FigureSpec 文件依赖下一次 session 中兼容的变量名、mapping keys、sequence indices、DataFrame 列和数据形状。
- 保存的 recipe、facet、repeated-panel 和 secondary-axis specs 只存列映射、等值 filters、selections、labels、axis settings 和 recipe intent，不保存原始数据。
- 保存的 reference line specs 只存 numeric constants 和 style，不保存派生数据。
- Runtime wheel 安装不应要求 Node/npm。
- Notebook workflows 返回代码，不直接编辑 Notebook 文件。
