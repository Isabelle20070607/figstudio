# FigStudio API Reference / API 参考

This reference documents the public beta API surface. It describes current behavior only; future capabilities belong in the roadmap.

本参考文档记录公开 beta 的 API 面。这里只描述当前行为；未来能力放在路线图。

## Python API / Python API

```python
figstudio.open(
    namespace=None,
    *,
    figure=None,
    script_path=None,
    block_id="main",
    mode="auto",
    open_browser=True,
) -> FigStudioSession
```

- `namespace`: usually `locals()`. Supported public values are summarized for the UI; live objects stay server-side.
- `figure`: optional Matplotlib `Figure` for best-effort inspection.
- `script_path`: enables controlled `.py` writeback.
- `block_id`: selects `# figstudio:start <block_id>` and `# figstudio:end <block_id>`.
- `mode`: session metadata for editor mode selection.
- `open_browser`: opens the local editor URL when true.

- `namespace`：通常传入 `locals()`。受支持的公开变量会摘要给 UI；真实对象留在服务端。
- `figure`：可选 Matplotlib `Figure`，用于 best-effort inspection。
- `script_path`：启用 `.py` 文件受控写回。
- `block_id`：选择 `# figstudio:start <block_id>` 和 `# figstudio:end <block_id>`。
- `mode`：用于 editor mode selection 的 session metadata。
- `open_browser`：为 true 时打开本地 editor URL。

```python
figstudio.save_spec(spec, path) -> pathlib.Path
figstudio.load_spec(path) -> FigureSpec
```

`save_spec` accepts a `FigureSpec` or compatible dict and writes JSON with UTF-8 encoding. `load_spec` validates JSON into `FigureSpec`.

`save_spec` 接受 `FigureSpec` 或兼容 dict，并以 UTF-8 写出 JSON。`load_spec` 会把 JSON 校验为 `FigureSpec`。

## CLI / 命令行

```powershell
figstudio --version
figstudio --no-browser
figstudio --port 8765 --no-browser
figstudio demo
figstudio demo --port 8765 --no-browser
```

- `--version`: print the installed package version, falling back to `0.1.0` in editable/source contexts.
- `--no-browser`: start the local server without opening a browser.
- `--port`: bind a specific localhost port.
- `demo`: start a sample session with a DataFrame and 2D heatmap array.

- `--version`：打印已安装 package version；editable/source 场景下 fallback 到 `0.1.0`。
- `--no-browser`：启动本地 server，但不打开浏览器。
- `--port`：绑定指定 localhost 端口。
- `demo`：启动包含 DataFrame 和二维 heatmap array 的样例会话。

The CLI prints the session URL and runs until interrupted.

CLI 会打印 session URL，并持续运行直到被中断。

## FigureSpec / FigureSpec

`FigureSpec` is the JSON-serializable editor state and codegen input.

`FigureSpec` 是可 JSON 序列化的 editor state，也是 codegen 输入。

| Field / 字段 | Type / 类型 | Meaning / 含义 |
| --- | --- | --- |
| `version` | integer | Spec format marker, currently defaulting to `1`. / Spec 格式标记，当前默认 `1`。 |
| `mode` | `explore` or `publish` | Editor mode. / 编辑器模式。 |
| `width`, `height` | float | Figure size in inches. / 图尺寸，单位 inch。 |
| `dpi` | integer | Render and export DPI. / 渲染和导出 DPI。 |
| `rows`, `cols` | integer | Subplot grid size. / subplot 网格大小。 |
| `axes` | list of `AxesSpec` | Axes configuration. / 坐标轴配置。 |
| `layers` | list of `PlotLayer` | Plot layer definitions. / 图层定义。 |
| `annotations` | list of `AnnotationSpec` | Text and arrow annotations. / 文本和箭头注释。 |
| `style` | `FigureStyle` | Figure title, font, layout, and preset. / 总标题、字体、布局和预设。 |
| `show` | boolean | Whether generated code calls `plt.show()`. / 生成代码是否调用 `plt.show()`。 |

### PlotLayer / PlotLayer

Supported `kind` values:

支持的 `kind` 值：

`line`, `scatter`, `bar`, `barh`, `hist`, `boxplot`, `violin`, `errorbar`, `heatmap`, `contour`, `step`, `fill_between`.

Each layer has:

每个 layer 包含：

- `id`: stable editor id.
- `axes_id`: target axes id such as `ax0`.
- `dataset`: `DatasetRef`.
- `style`: `LayerStyle`.
- `readonly`: whether the layer should be treated as read-only context.
- `source`: origin marker such as `generated`.

- `id`：稳定 editor id。
- `axes_id`：目标 axes id，例如 `ax0`。
- `dataset`：`DatasetRef`。
- `style`：`LayerStyle`。
- `readonly`：该 layer 是否应视为只读上下文。
- `source`：来源标记，例如 `generated`。

### DatasetRef / DatasetRef

`DatasetRef.variable` is the primary variable name. Channel fields can point to columns or independent variables:

`DatasetRef.variable` 是主要变量名。channel 字段可指向列或独立变量：

- `x`, `y`, `z`, `yerr`: column names on the selected channel variable.
- `x_variable`, `y_variable`, `z_variable`, `yerr_variable`: independent variable names for a channel.

- `x`、`y`、`z`、`yerr`：所选 channel variable 上的列名。
- `x_variable`、`y_variable`、`z_variable`、`yerr_variable`：channel 使用的独立变量名。

When a channel variable is omitted, the channel uses `DatasetRef.variable`.

当 channel variable 省略时，该 channel 使用 `DatasetRef.variable`。

### FigureStyle / FigureStyle

`FigureStyle.preset` supports `custom`, `journal_single`, `journal_double`, `poster`, and `slide`.

`FigureStyle.preset` 支持 `custom`、`journal_single`、`journal_double`、`poster` 和 `slide`。

## REST API / REST API

The local FastAPI server is created per session and binds to `127.0.0.1` by default.

本地 FastAPI server 按 session 创建，并默认绑定到 `127.0.0.1`。

### `GET /api/session`

Returns `SessionInfo`:

返回 `SessionInfo`：

- `id`
- `url`
- `block_id`
- `mode`
- `script_path`
- `has_script_writeback`
- `has_figure`
- `figure_tree`: best-effort inspected Figure metadata. It reports normal plot axes separately from colorbar axes, including legend labels, colorbar labels, histogram bin/count metadata, boxplot quartile boxes, and violin extents when Matplotlib exposes stable artist data.

- `figure_tree`：best-effort inspected Figure metadata。它会把普通 plot axes 与 colorbar axes 分开，并在 Matplotlib 暴露稳定 artist data 时报告 legend labels、colorbar labels、histogram bin/count metadata、boxplot quartile boxes 和 violin extents。

### `GET /api/variables`

Returns a list of `VariableSummary` objects:

返回 `VariableSummary` 列表：

- `name`
- `kind`
- `type_name`
- `shape`
- `columns`
- `dtypes`
- `sample`
- `truncated`

Supported summary kinds are `dataframe`, `series`, `ndarray`, `sequence`, and `figure`.

支持的 summary kind 为 `dataframe`、`series`、`ndarray`、`sequence` 和 `figure`。

### `GET /api/spec`

Returns the current `FigureSpec`.

返回当前 `FigureSpec`。

### `POST /api/validate`

Request:

请求：

```json
{
  "spec": {}
}
```

Response:

响应：

```json
{
  "ok": true,
  "issues": []
}
```

Issue codes currently include `missing_axes`, `missing_variable`, `missing_column`, `dimension_mismatch`, `requires_2d_data`, and `log_scale_non_positive`. `layer_id`, `axes_id`, and `field` are stable enough for the editor to select or focus the affected control when possible.

当前 issue code 包括 `missing_axes`、`missing_variable`、`missing_column`、`dimension_mismatch`、`requires_2d_data` 和 `log_scale_non_positive`。`layer_id`、`axes_id` 和 `field` 足够稳定，editor 可在可行时选中或聚焦受影响控件。

### `POST /api/spec`

Request body is a `FigureSpec`. The server stores it as the current spec, validates it, and returns an SVG `RenderResponse`.

请求体是 `FigureSpec`。server 会把它存为当前 spec，校验后返回 SVG `RenderResponse`。

```json
{
  "image": "<svg ...>",
  "format": "svg",
  "code": "import matplotlib.pyplot as plt\n..."
}
```

### `POST /api/render`

Request:

请求：

```json
{
  "spec": {},
  "format": "svg"
}
```

`format` may be `svg` or `png`. SVG responses contain decoded SVG text in `image`; PNG responses contain base64 data in `image`.

`format` 可为 `svg` 或 `png`。SVG response 的 `image` 是解码后的 SVG 文本；PNG response 的 `image` 是 base64 data。

### `POST /api/save-code`

Request:

请求：

```json
{
  "spec": {},
  "code": null
}
```

If `code` is omitted, the server generates code from `spec`. With `script_path`, the server attempts controlled block writeback. Without `script_path`, it returns notebook replacement code.

如果省略 `code`，server 会基于 `spec` 生成代码。有 `script_path` 时，server 会尝试受控代码块写回；没有 `script_path` 时，返回 Notebook replacement code。

Response:

响应：

```json
{
  "ok": true,
  "code": "...",
  "notebook_cell": "...",
  "wrote_file": false,
  "script_path": null,
  "message": "No script_path was provided. Use notebook_cell as replacement code.",
  "error": null
}
```

Writeback failures return HTTP 200 with `ok: false`, generated code, and an `error` object so the user can recover manually.

写回失败会返回 HTTP 200、`ok: false`、生成代码和 `error` object，便于用户手动恢复。

### `POST /api/export`

Request:

请求：

```json
{
  "spec": {},
  "format": "svg",
  "output_path": null,
  "dpi": null
}
```

`format` may be `png`, `svg`, or `pdf`. If `output_path` is omitted, `data` contains base64 export data. If `output_path` is provided, the file is written and `data` is null.

`format` 可为 `png`、`svg` 或 `pdf`。如果省略 `output_path`，`data` 包含 base64 export data。如果提供 `output_path`，server 会写入文件且 `data` 为 null。

### `WS /api/events`

Accepts a websocket connection, sends a `connected` message, and acknowledges received JSON messages. It is reserved for lightweight editor events.

接受 websocket 连接，发送 `connected` message，并 ack 收到的 JSON message。该端点预留给轻量 editor events。

## Error Payloads / 错误 Payload

HTTP errors use:

HTTP error 使用：

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

Error codes currently include:

当前 error code 包括：

- `validation_failed`
- `render_failed`
- `export_failed`
- `writeback_failed`
- `writeback_io_failed`

`writeback_failed` and `writeback_io_failed` are returned inside `SaveCodeResponse.error`; render, export, and validation failures are HTTP errors.

`writeback_failed` 和 `writeback_io_failed` 会出现在 `SaveCodeResponse.error` 中；render、export 和 validation failure 是 HTTP error。

## Compatibility Notes / 兼容性说明

- Generated plotting code must run without importing FigStudio.
- Saved FigureSpec files depend on compatible variable names and data shapes in the next session.
- Runtime wheel installs should not require Node/npm.
- Notebook workflows return code and do not directly edit notebook files.
- Existing Figure inspection is best-effort and should not be treated as source-code recovery. Line, scatter, image, and bar artists may become editable layers when data can be extracted. Histograms, boxplots, violins, legends, and colorbars are exposed as metadata unless the current model can reproduce them honestly.

- 生成绘图代码必须能在不 import FigStudio 的情况下运行。
- 保存的 FigureSpec 文件依赖下一次 session 中兼容的变量名和数据形状。
- 运行时 wheel 安装不应要求 Node/npm。
- Notebook 工作流返回代码，不直接编辑 notebook 文件。
- Existing Figure inspection 是 best-effort，不应视为源码恢复。line、scatter、image 和 bar artist 在数据可提取时可变成可编辑 layer。histogram、boxplot、violin、legend 和 colorbar 会作为 metadata 暴露，除非当前模型能诚实复现它们。
