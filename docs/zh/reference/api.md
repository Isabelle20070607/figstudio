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
```

CLI 会打印 session URL，并持续运行直到被中断。

## FigureSpec

`FigureSpec` 是可 JSON 序列化的 editor state，也是 codegen 输入。

| 字段 | 含义 |
| --- | --- |
| `version` | Spec 格式标记，当前默认 `1`。 |
| `mode` | `explore` 或 `publish`。 |
| `width`, `height`, `dpi` | Figure size 和 render/export DPI。 |
| `rows`, `cols`, `axes` | Panel layout grid 和 axes geometry。 |
| `layers` | Plot layer definitions。 |
| `recipes` | Statistics recipe definitions。 |
| `annotations` | Text 和 arrow annotations。 |
| `style` | Figure title、font、layout、built-in preset 和 project profile reference。 |
| `show` | 生成代码是否调用 `plt.show()`。 |

支持的 `PlotLayer.kind` 值为 `line`、`scatter`、`bar`、`barh`、`hist`、`boxplot`、`violin`、`errorbar`、`heatmap`、`contour`、`step` 和 `fill_between`。

支持的 `RecipeLayer.kind` 值为 `mean_sem_line`、`grouped_points` 和 `paired_before_after`。

`DatasetRef` 字段可通过 `x_variable`、`y_variable`、`z_variable` 和 `yerr_variable` 指向 DataFrame 列或独立变量。`RecipeDatasetRef.variable` 必须指向 pandas DataFrame，且只保存列名。

`FigureStyle.profile_id` 引用项目 style profile。`FigureStyle.profile_overrides` 列出应使用 spec 显式值而不是 profile 默认值的 figure 字段：`width`、`height`、`dpi`、`font_family`、`font_size` 和 `constrained_layout`。

## REST API

本地 FastAPI server 按 session 创建，并默认绑定到 `127.0.0.1`。

| Endpoint | 用途 |
| --- | --- |
| `GET /api/session` | Session metadata、写回能力、可选 inspected figure tree。 |
| `GET /api/variables` | 安全变量摘要。 |
| `GET /api/style-profiles` | 已加载 project style profiles、source path 和非致命 load warnings。 |
| `GET /api/spec` | 当前 `FigureSpec`。 |
| `POST /api/validate` | 基于 live namespace 校验 `FigureSpec`。 |
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

当前 error codes 为 `validation_failed`、`render_failed`、`export_failed`、`writeback_failed` 和 `writeback_io_failed`。Writeback errors 出现在 `SaveCodeResponse.error` 中；render、export 和 validation failures 是 HTTP errors。

Validation issue codes 包括 `missing_style_profile`、`invalid_grid_size`、`duplicate_axes_id`、`invalid_axes_span`、`axes_out_of_bounds`、`axes_overlap`、`missing_axes`、`missing_variable`、`missing_column`、`unsupported_recipe_source`、`dimension_mismatch`、`requires_2d_data` 和 `log_scale_non_positive`。

## Compatibility Notes

- 生成绘图代码必须能在不 import FigStudio 的情况下运行。
- 生成 recipe code 可以调用现有 pandas DataFrame 变量的方法，但 imports 仍限于 Matplotlib。
- 保存的 FigureSpec 文件依赖下一次 session 中兼容的变量名、DataFrame 列和数据形状。
- 保存的 recipe specs 只存列映射和 recipe intent，不保存原始数据。
- Runtime wheel 安装不应要求 Node/npm。
- Notebook workflows 返回代码，不直接编辑 Notebook 文件。
