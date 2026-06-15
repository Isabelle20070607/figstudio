import CodeMirror from "@uiw/react-codemirror";
import { python } from "@codemirror/lang-python";
import {
  Braces,
  Check,
  Copy,
  Download,
  FileCode2,
  FlaskConical,
  Image as ImageIcon,
  Layers3,
  Play,
  Save,
  Settings2,
  Trash2
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { api } from "./api";
import { useAppStore } from "./store";
import type { AxesSpec, DatasetRef, FigureSpec, LayerStyle, PlotKind, PlotLayer, VariableSummary } from "./types";

const plotKinds: PlotKind[] = [
  "line",
  "scatter",
  "bar",
  "barh",
  "hist",
  "boxplot",
  "violin",
  "errorbar",
  "heatmap",
  "contour",
  "step",
  "fill_between"
];

const colors = ["#2563eb", "#0f766e", "#dc2626", "#9333ea", "#b45309", "#111827"];
const markers = ["", "o", "s", "^", "D", "x"];
const linestyles = ["-", "--", "-.", ":"];
const cmaps = ["viridis", "magma", "plasma", "cividis", "coolwarm", "Greys"];
const scales: AxesSpec["xscale"][] = ["linear", "log", "symlog", "logit"];
const indexSource = "__index__";
const noneSource = "__none__";

function createId(prefix: string): string {
  if ("randomUUID" in crypto) {
    return `${prefix}-${crypto.randomUUID().slice(0, 8)}`;
  }
  return `${prefix}-${Math.random().toString(16).slice(2, 10)}`;
}

function findVariable(variables: VariableSummary[], name?: string): VariableSummary | undefined {
  return variables.find((variable) => variable.name === name);
}

function firstColumn(variable?: VariableSummary): string {
  return variable?.columns[0] ?? "";
}

function secondColumn(variable?: VariableSummary): string {
  return variable?.columns[1] ?? variable?.columns[0] ?? "";
}

function createAxis(index: number, row: number, col: number, existing?: AxesSpec): AxesSpec {
  return {
    id: `ax${index}`,
    row,
    col,
    title: existing?.title ?? "",
    xlabel: existing?.xlabel ?? "",
    ylabel: existing?.ylabel ?? "",
    xscale: existing?.xscale ?? "linear",
    yscale: existing?.yscale ?? "linear",
    xlim: existing?.xlim ?? null,
    ylim: existing?.ylim ?? null,
    grid: existing?.grid ?? false,
    legend: existing?.legend ?? true,
    colorbar: existing?.colorbar ?? false
  };
}

function resizeAxes(spec: FigureSpec, rows: number, cols: number): FigureSpec {
  const nextRows = Math.max(1, Math.min(6, Math.round(rows || 1)));
  const nextCols = Math.max(1, Math.min(6, Math.round(cols || 1)));
  const axes: AxesSpec[] = [];
  for (let row = 0; row < nextRows; row += 1) {
    for (let col = 0; col < nextCols; col += 1) {
      const index = axes.length;
      axes.push(createAxis(index, row, col, spec.axes[index]));
    }
  }
  const validIds = new Set(axes.map((axis) => axis.id));
  return {
    ...spec,
    rows: nextRows,
    cols: nextCols,
    axes,
    layers: spec.layers.map((layer) => ({
      ...layer,
      axes_id: validIds.has(layer.axes_id) ? layer.axes_id : axes[0].id
    }))
  };
}

function buildDatasetRef({
  kind,
  variables,
  yVariable,
  yColumn,
  xVariable,
  xColumn,
  yerrVariable,
  yerrColumn
}: {
  kind: PlotKind;
  variables: VariableSummary[];
  yVariable: string;
  yColumn: string;
  xVariable: string;
  xColumn: string;
  yerrVariable: string;
  yerrColumn: string;
}): DatasetRef {
  const yVar = findVariable(variables, yVariable) ?? variables[0];
  if (!yVar) {
    throw new Error("Cannot create a dataset without a source variable.");
  }
  const xVar = findVariable(variables, xVariable);
  const yerrVar = findVariable(variables, yerrVariable);
  const dataset: DatasetRef = {
    variable: yVar.name
  };

  if (kind === "heatmap" || kind === "contour") {
    if (yColumn) {
      dataset.z = yColumn;
    }
  } else if (yColumn) {
    dataset.y = yColumn;
  }

  if (xVar && xVariable !== indexSource) {
    if (xVar.name === dataset.variable) {
      dataset.x = xColumn || null;
    } else {
      dataset.x_variable = xVar.name;
      dataset.x = xColumn || null;
    }
  }

  if (kind === "errorbar" && yerrVar && yerrVariable !== noneSource) {
    if (yerrVar.name === dataset.variable) {
      dataset.yerr = yerrColumn || null;
    } else {
      dataset.yerr_variable = yerrVar.name;
      dataset.yerr = yerrColumn || null;
    }
  }

  return dataset;
}

function createLayer(
  kind: PlotKind,
  variables: VariableSummary[],
  yVariable: string,
  yColumn: string,
  xVariable: string,
  xColumn: string,
  yerrVariable: string,
  yerrColumn: string
): PlotLayer {
  const yVar = findVariable(variables, yVariable) ?? variables[0];
  if (!yVar) {
    throw new Error("Cannot create a layer without a source variable.");
  }
  const label = yColumn || yVar.name;
  const dataset = buildDatasetRef({
    kind,
    variables,
    yVariable: yVar.name,
    yColumn,
    xVariable,
    xColumn,
    yerrVariable,
    yerrColumn
  });
  const style: LayerStyle = {
    label,
    color: kind === "heatmap" || kind === "contour" ? null : colors[0],
    marker: kind === "scatter" ? "o" : null,
    linestyle: kind === "line" || kind === "step" || kind === "errorbar" ? "-" : null,
    linewidth: kind === "line" || kind === "step" || kind === "errorbar" ? 1.8 : null,
    alpha: kind === "scatter" ? 0.85 : null,
    cmap: kind === "heatmap" || kind === "contour" ? "viridis" : null,
    bins: kind === "hist" ? 30 : null,
    fill_alpha: kind === "fill_between" ? 0.3 : null
  };
  return {
    id: createId("layer"),
    kind,
    axes_id: "ax0",
    dataset,
    style,
    readonly: false,
    source: "generated"
  };
}

function cloneLayer(layer: PlotLayer): PlotLayer {
  return {
    ...structuredClone(layer),
    id: createId("layer"),
    style: {
      ...layer.style,
      label: layer.style.label ? `${layer.style.label} copy` : undefined
    }
  };
}

export function App() {
  const {
    session,
    variables,
    spec,
    render,
    selectedVariable,
    selectedLayerId,
    status,
    setSession,
    setVariables,
    setSpec,
    setRender,
    setSelectedVariable,
    setSelectedLayerId,
    setStatus,
    updateSpec
  } = useAppStore();

  const [saveMessage, setSaveMessage] = useState("");

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const [sessionInfo, variableList, initialSpec] = await Promise.all([
          api.session(),
          api.variables(),
          api.spec()
        ]);
        if (cancelled) {
          return;
        }
        setSession(sessionInfo);
        setVariables(variableList);
        setSpec(initialSpec);
        setStatus("Ready");
      } catch (error) {
        setStatus(error instanceof Error ? error.message : "Failed to load session");
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [setSession, setSpec, setStatus, setVariables]);

  useEffect(() => {
    if (!spec) {
      return;
    }
    const timeout = window.setTimeout(async () => {
      try {
        const response = await api.render(spec, "svg");
        setRender(response);
        setStatus("Preview synced");
      } catch (error) {
        setStatus(error instanceof Error ? error.message : "Render failed");
      }
    }, 260);
    return () => window.clearTimeout(timeout);
  }, [spec, setRender, setStatus]);

  const selectedVar = useMemo(
    () => variables.find((variable) => variable.name === selectedVariable) ?? variables[0],
    [selectedVariable, variables]
  );
  const selectedLayer = useMemo(
    () => spec?.layers.find((layer) => layer.id === selectedLayerId),
    [selectedLayerId, spec?.layers]
  );

  async function renderNow() {
    if (!spec) {
      return;
    }
    setStatus("Rendering");
    try {
      const response = await api.render(spec, "svg");
      setRender(response);
      setStatus("Preview synced");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Render failed");
    }
  }

  async function saveCode() {
    if (!spec) {
      return;
    }
    setStatus("Saving code");
    try {
      const response = await api.saveCode(spec, render?.code);
      setSaveMessage(response.message);
      if (!response.ok) {
        setStatus("Save blocked");
      } else {
        setStatus(response.wrote_file ? "Script updated" : "Notebook cell ready");
      }
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Save failed");
    }
  }

  async function exportFigure(format: "svg" | "png" | "pdf") {
    if (!spec) {
      return;
    }
    setStatus(`Exporting ${format.toUpperCase()}`);
    try {
      const response = await api.exportFigure(spec, format);
      if (response.data) {
        const href =
          format === "svg"
            ? `data:image/svg+xml;base64,${response.data}`
            : `data:application/octet-stream;base64,${response.data}`;
        const link = document.createElement("a");
        link.href = href;
        link.download = `figstudio-export.${format}`;
        link.click();
      }
      setStatus(`${format.toUpperCase()} export ready`);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Export failed");
    }
  }

  function deleteLayer(id: string) {
    updateSpec((draft) => ({
      ...draft,
      layers: draft.layers.filter((layer) => layer.id !== id)
    }));
    setSelectedLayerId("");
  }

  function duplicateLayer(layer: PlotLayer) {
    const next = cloneLayer(layer);
    updateSpec((draft) => ({
      ...draft,
      layers: [...draft.layers, next]
    }));
    setSelectedLayerId(next.id);
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">
            <FlaskConical size={18} />
          </div>
          <div>
            <h1>FigStudio</h1>
            <p>{session?.script_path ? `Writing ${session.block_id}` : "Notebook-safe code output"}</p>
          </div>
        </div>
        <div className="mode-switch" role="group" aria-label="Mode">
          <button
            className={spec?.mode === "explore" ? "active" : ""}
            onClick={() => updateSpec((draft) => ({ ...draft, mode: "explore" }))}
          >
            Explore
          </button>
          <button
            className={spec?.mode === "publish" ? "active" : ""}
            onClick={() => updateSpec((draft) => ({ ...draft, mode: "publish" }))}
          >
            Publish
          </button>
        </div>
        <div className="toolbar">
          <button className="icon-button" title="Render now" onClick={renderNow} disabled={!spec}>
            <Play size={16} />
          </button>
          <button className="action-button" onClick={saveCode} disabled={!spec}>
            <Save size={16} />
            Save code
          </button>
          <button className="icon-button" title="Export SVG" onClick={() => exportFigure("svg")} disabled={!spec}>
            <Download size={16} />
          </button>
        </div>
      </header>

      <section className="workspace">
        <VariablePanel
          variables={variables}
          selected={selectedVar?.name}
          onSelect={setSelectedVariable}
          onAddLayer={(layer) => {
            updateSpec((draft) => ({
              ...draft,
              layers: [...draft.layers, layer]
            }));
            setSelectedLayerId(layer.id);
          }}
        />

        <section className="canvas-column">
          <div className="canvas-toolbar">
            <div className="status-line">
              <Check size={15} />
              {status}
            </div>
            <div className="export-set">
              <button onClick={() => exportFigure("png")} disabled={!spec}>
                PNG
              </button>
              <button onClick={() => exportFigure("svg")} disabled={!spec}>
                SVG
              </button>
              <button onClick={() => exportFigure("pdf")} disabled={!spec}>
                PDF
              </button>
            </div>
          </div>
          <Preview render={render} />
          <CodePanel code={render?.code ?? ""} saveMessage={saveMessage} />
        </section>

        <Inspector
          spec={spec}
          selectedLayer={selectedLayer}
          onSelectLayer={setSelectedLayerId}
          onUpdateSpec={updateSpec}
          onDeleteLayer={deleteLayer}
          onDuplicateLayer={duplicateLayer}
        />
      </section>
    </main>
  );
}

interface VariablePanelProps {
  variables: VariableSummary[];
  selected?: string;
  onSelect: (name: string) => void;
  onAddLayer: (layer: PlotLayer) => void;
}

function VariablePanel({ variables, selected, onSelect, onAddLayer }: VariablePanelProps) {
  const variable = variables.find((item) => item.name === selected) ?? variables[0];
  const [kind, setKind] = useState<PlotKind>("line");
  const [xVariable, setXVariable] = useState(indexSource);
  const [xColumn, setXColumn] = useState("");
  const [yVariable, setYVariable] = useState("");
  const [yColumn, setYColumn] = useState("");
  const [yerrVariable, setYerrVariable] = useState(noneSource);
  const [yerrColumn, setYerrColumn] = useState("");

  const xVar = findVariable(variables, xVariable);
  const yVar = findVariable(variables, yVariable) ?? variable;
  const yerrVar = findVariable(variables, yerrVariable);
  const compatibility = compatibilityText(kind, yVar, xVar);

  useEffect(() => {
    if (!variable) {
      return;
    }
    setYVariable(variable.name);
    setYColumn(kind === "heatmap" || kind === "contour" ? firstColumn(variable) : secondColumn(variable));
    setXVariable(variable.columns.length ? variable.name : indexSource);
    setXColumn(firstColumn(variable));
    setYerrVariable(noneSource);
    setYerrColumn("");
  }, [variable?.name, kind]);

  return (
    <aside className="side-panel variables-panel">
      <PanelTitle icon={<Braces size={16} />} title="Variables" />
      <div className="variable-list">
        {variables.map((item) => (
          <button
            key={item.name}
            className={`variable-row ${item.name === variable?.name ? "selected" : ""}`}
            onClick={() => onSelect(item.name)}
          >
            <span>{item.name}</span>
            <small>
              {item.kind} {item.shape.length ? `(${item.shape.join(" x ")})` : ""}
            </small>
          </button>
        ))}
      </div>

      <div className="builder">
        <h2>Create layer</h2>
        <label>
          Plot type
          <select value={kind} onChange={(event) => setKind(event.target.value as PlotKind)}>
            {plotKinds.map((plotKind) => (
              <option key={plotKind} value={plotKind}>
                {plotKind}
              </option>
            ))}
          </select>
        </label>

        <div className="source-grid">
          <label>
            Y / value source
            <select value={yVar?.name ?? ""} onChange={(event) => setYVariable(event.target.value)}>
              {variables.map((item) => (
                <option key={item.name} value={item.name}>
                  {item.name}
                </option>
              ))}
            </select>
          </label>
          {yVar?.columns.length ? (
            <label>
              Y / value column
              <select value={yColumn} onChange={(event) => setYColumn(event.target.value)}>
                <option value="">variable</option>
                {yVar.columns.map((column) => (
                  <option key={column} value={column}>
                    {column}
                  </option>
                ))}
              </select>
            </label>
          ) : null}
        </div>

        <div className="source-grid">
          <label>
            X source
            <select value={xVariable} onChange={(event) => setXVariable(event.target.value)}>
              <option value={indexSource}>index</option>
              {variables.map((item) => (
                <option key={item.name} value={item.name}>
                  {item.name}
                </option>
              ))}
            </select>
          </label>
          {xVar?.columns.length ? (
            <label>
              X column
              <select value={xColumn} onChange={(event) => setXColumn(event.target.value)}>
                <option value="">variable</option>
                {xVar.columns.map((column) => (
                  <option key={column} value={column}>
                    {column}
                  </option>
                ))}
              </select>
            </label>
          ) : null}
        </div>

        {kind === "errorbar" ? (
          <div className="source-grid">
            <label>
              Error source
              <select value={yerrVariable} onChange={(event) => setYerrVariable(event.target.value)}>
                <option value={noneSource}>none</option>
                {variables.map((item) => (
                  <option key={item.name} value={item.name}>
                    {item.name}
                  </option>
                ))}
              </select>
            </label>
            {yerrVar?.columns.length ? (
              <label>
                Error column
                <select value={yerrColumn} onChange={(event) => setYerrColumn(event.target.value)}>
                  <option value="">variable</option>
                  {yerrVar.columns.map((column) => (
                    <option key={column} value={column}>
                      {column}
                    </option>
                  ))}
                </select>
              </label>
            ) : null}
          </div>
        ) : null}

        {compatibility ? <p className="compatibility-note">{compatibility}</p> : null}

        <button
          className="primary-button"
          disabled={!variable || !yVar}
          onClick={() =>
            yVar &&
            onAddLayer(createLayer(kind, variables, yVar.name, yColumn, xVariable, xColumn, yerrVariable, yerrColumn))
          }
        >
          <Layers3 size={16} />
          Add layer
        </button>
      </div>
    </aside>
  );
}

function compatibilityText(kind: PlotKind, yVar?: VariableSummary, xVar?: VariableSummary): string {
  if (!yVar) {
    return "";
  }
  if ((kind === "heatmap" || kind === "contour") && yVar.shape.length < 2 && !yVar.columns.length) {
    return "Heatmap and contour previews work best with a 2D ndarray or gridded value column.";
  }
  if ((kind === "hist" || kind === "boxplot" || kind === "violin") && xVar) {
    return "This plot type uses the Y / value source; X source is ignored by generated code.";
  }
  if (xVar && yVar.shape.length && xVar.shape.length && xVar.shape[0] !== yVar.shape[0]) {
    return "X and Y appear to have different first dimensions; Matplotlib may reject the render.";
  }
  return "";
}

function Preview({ render }: { render?: { image: string; format: string } }) {
  const src =
    render?.format === "svg"
      ? `data:image/svg+xml;charset=utf-8,${encodeURIComponent(render.image)}`
      : render?.image
        ? `data:image/png;base64,${render.image}`
        : "";

  return (
    <section className="preview-surface">
      {src ? (
        <div className="figure-frame">
          <img src={src} alt="Matplotlib preview" />
          <div className="overlay-handle top-left" />
          <div className="overlay-handle top-right" />
          <div className="overlay-handle bottom-left" />
          <div className="overlay-handle bottom-right" />
        </div>
      ) : (
        <div className="empty-preview">
          <ImageIcon size={32} />
          <span>Add a layer to render a Matplotlib preview</span>
        </div>
      )}
    </section>
  );
}

function Inspector({
  spec,
  selectedLayer,
  onSelectLayer,
  onUpdateSpec,
  onDeleteLayer,
  onDuplicateLayer
}: {
  spec?: FigureSpec;
  selectedLayer?: PlotLayer;
  onSelectLayer: (id: string) => void;
  onUpdateSpec: (updater: (spec: FigureSpec) => FigureSpec) => void;
  onDeleteLayer: (id: string) => void;
  onDuplicateLayer: (layer: PlotLayer) => void;
}) {
  const [selectedAxisId, setSelectedAxisId] = useState("ax0");
  const selectedAxis = spec?.axes.find((axis) => axis.id === selectedAxisId) ?? spec?.axes[0];

  useEffect(() => {
    if (!spec?.axes.length) {
      return;
    }
    if (!spec.axes.some((axis) => axis.id === selectedAxisId)) {
      setSelectedAxisId(spec.axes[0].id);
    }
  }, [selectedAxisId, spec?.axes]);

  return (
    <aside className="side-panel inspector-panel">
      <PanelTitle icon={<Settings2 size={16} />} title="Inspector" />
      {!spec || !selectedAxis ? (
        <p className="muted">Waiting for session</p>
      ) : (
        <>
          <section className="control-group">
            <h2>Figure</h2>
            <div className="split-row">
              <NumberField label="Width" value={spec.width} onChange={(value) => onUpdateSpec((draft) => ({ ...draft, width: value }))} />
              <NumberField label="Height" value={spec.height} onChange={(value) => onUpdateSpec((draft) => ({ ...draft, height: value }))} />
            </div>
            <div className="split-row">
              <NumberField label="DPI" value={spec.dpi} step={1} min={24} onChange={(value) => onUpdateSpec((draft) => ({ ...draft, dpi: value }))} />
              <NumberField
                label="Font size"
                value={spec.style.font_size}
                onChange={(value) =>
                  onUpdateSpec((draft) => ({
                    ...draft,
                    style: { ...draft.style, font_size: value }
                  }))
                }
              />
            </div>
            <div className="split-row">
              <NumberField label="Rows" value={spec.rows} step={1} min={1} max={6} onChange={(value) => onUpdateSpec((draft) => resizeAxes(draft, value, draft.cols))} />
              <NumberField label="Cols" value={spec.cols} step={1} min={1} max={6} onChange={(value) => onUpdateSpec((draft) => resizeAxes(draft, draft.rows, value))} />
            </div>
            <TextField
              label="Suptitle"
              value={spec.style.title}
              onChange={(value) =>
                onUpdateSpec((draft) => ({
                  ...draft,
                  style: { ...draft.style, title: value }
                }))
              }
            />
            {spec.mode === "publish" ? (
              <>
                <TextField
                  label="Font family"
                  value={spec.style.font_family ?? ""}
                  onChange={(value) =>
                    onUpdateSpec((draft) => ({
                      ...draft,
                      style: { ...draft.style, font_family: value || null }
                    }))
                  }
                />
                <ToggleField
                  label="Constrained layout"
                  value={spec.style.constrained_layout}
                  onChange={(value) =>
                    onUpdateSpec((draft) => ({
                      ...draft,
                      style: { ...draft.style, constrained_layout: value }
                    }))
                  }
                />
              </>
            ) : null}
          </section>

          <section className="control-group">
            <h2>Axes</h2>
            <label>
              Active axes
              <select value={selectedAxis.id} onChange={(event) => setSelectedAxisId(event.target.value)}>
                {spec.axes.map((axis, index) => (
                  <option key={axis.id} value={axis.id}>
                    {axis.id} ({axis.row + 1}, {axis.col + 1}) {index === 0 ? "primary" : ""}
                  </option>
                ))}
              </select>
            </label>
            <TextField label="Title" value={selectedAxis.title} onChange={(value) => updateAxis(onUpdateSpec, selectedAxis.id, { title: value })} />
            <TextField label="X label" value={selectedAxis.xlabel} onChange={(value) => updateAxis(onUpdateSpec, selectedAxis.id, { xlabel: value })} />
            <TextField label="Y label" value={selectedAxis.ylabel} onChange={(value) => updateAxis(onUpdateSpec, selectedAxis.id, { ylabel: value })} />
            <div className="split-row">
              <SelectField label="X scale" value={selectedAxis.xscale} options={scales} onChange={(value) => updateAxis(onUpdateSpec, selectedAxis.id, { xscale: value as AxesSpec["xscale"] })} />
              <SelectField label="Y scale" value={selectedAxis.yscale} options={scales} onChange={(value) => updateAxis(onUpdateSpec, selectedAxis.id, { yscale: value as AxesSpec["yscale"] })} />
            </div>
            <LimitField label="X limits" value={selectedAxis.xlim ?? null} onChange={(value) => updateAxis(onUpdateSpec, selectedAxis.id, { xlim: value })} />
            <LimitField label="Y limits" value={selectedAxis.ylim ?? null} onChange={(value) => updateAxis(onUpdateSpec, selectedAxis.id, { ylim: value })} />
            <ToggleField label="Grid" value={selectedAxis.grid} onChange={(value) => updateAxis(onUpdateSpec, selectedAxis.id, { grid: value })} />
            <ToggleField label="Legend" value={selectedAxis.legend} onChange={(value) => updateAxis(onUpdateSpec, selectedAxis.id, { legend: value })} />
            <ToggleField label="Contour colorbar" value={selectedAxis.colorbar} onChange={(value) => updateAxis(onUpdateSpec, selectedAxis.id, { colorbar: value })} />
          </section>

          <section className="control-group">
            <h2>Layers</h2>
            <div className="layer-list">
              {spec.layers.map((layer) => (
                <button
                  key={layer.id}
                  className={layer.id === selectedLayer?.id ? "selected" : ""}
                  onClick={() => onSelectLayer(layer.id)}
                >
                  <span>{layer.style.label || layer.dataset.variable}</span>
                  <small>
                    {layer.kind} · {layer.axes_id}
                  </small>
                </button>
              ))}
            </div>
            {selectedLayer ? (
              <>
                <div className="layer-actions">
                  <button className="mini-button" onClick={() => onDuplicateLayer(selectedLayer)}>
                    <Copy size={14} />
                    Duplicate
                  </button>
                  <button className="mini-button danger-button" onClick={() => onDeleteLayer(selectedLayer.id)}>
                    <Trash2 size={14} />
                    Delete
                  </button>
                </div>
                <LayerControls
                  layer={selectedLayer}
                  axes={spec.axes}
                  onChange={(next) =>
                    onUpdateSpec((draft) => ({
                      ...draft,
                      layers: draft.layers.map((layer) => (layer.id === next.id ? next : layer))
                    }))
                  }
                />
              </>
            ) : (
              <p className="muted">Select or add a layer to edit style.</p>
            )}
          </section>
        </>
      )}
    </aside>
  );
}

function updateAxis(
  onUpdateSpec: (updater: (spec: FigureSpec) => FigureSpec) => void,
  axisId: string,
  patch: Partial<AxesSpec>
) {
  onUpdateSpec((draft) => ({
    ...draft,
    axes: draft.axes.map((axis) => (axis.id === axisId ? { ...axis, ...patch } : axis))
  }));
}

function LayerControls({
  layer,
  axes,
  onChange
}: {
  layer: PlotLayer;
  axes: AxesSpec[];
  onChange: (layer: PlotLayer) => void;
}) {
  const isFieldLayer = layer.kind === "heatmap" || layer.kind === "contour";
  return (
    <div className="layer-controls">
      <SelectField
        label="Axes"
        value={layer.axes_id}
        options={axes.map((axis) => axis.id)}
        onChange={(value) => onChange({ ...layer, axes_id: value })}
      />
      <SelectField
        label="Plot type"
        value={layer.kind}
        options={plotKinds}
        onChange={(value) => onChange({ ...layer, kind: value as PlotKind })}
      />
      <TextField
        label="Label"
        value={layer.style.label ?? ""}
        onChange={(value) => onChange({ ...layer, style: { ...layer.style, label: value || null } })}
      />
      {isFieldLayer ? (
        <SelectField
          label="Colormap"
          value={layer.style.cmap ?? "viridis"}
          options={cmaps}
          onChange={(value) => onChange({ ...layer, style: { ...layer.style, cmap: value } })}
        />
      ) : (
        <label>
          Color
          <div className="swatches">
            {colors.map((color) => (
              <button
                key={color}
                className={layer.style.color === color ? "selected" : ""}
                style={{ background: color }}
                aria-label={color}
                onClick={() => onChange({ ...layer, style: { ...layer.style, color } })}
              />
            ))}
          </div>
        </label>
      )}
      <div className="split-row">
        <SelectField
          label="Marker"
          value={layer.style.marker ?? ""}
          options={markers}
          optionLabel={(value) => value || "none"}
          onChange={(value) => onChange({ ...layer, style: { ...layer.style, marker: value || null } })}
        />
        <SelectField
          label="Line style"
          value={layer.style.linestyle ?? ""}
          options={linestyles}
          onChange={(value) => onChange({ ...layer, style: { ...layer.style, linestyle: value || null } })}
        />
      </div>
      <div className="split-row">
        <NumberField
          label="Line width"
          value={layer.style.linewidth ?? 1.8}
          step={0.1}
          min={0}
          onChange={(value) => onChange({ ...layer, style: { ...layer.style, linewidth: value } })}
        />
        <NumberField
          label="Alpha"
          value={layer.style.alpha ?? 1}
          step={0.05}
          min={0}
          max={1}
          onChange={(value) => onChange({ ...layer, style: { ...layer.style, alpha: value } })}
        />
      </div>
      {layer.kind === "hist" ? (
        <NumberField
          label="Bins"
          value={layer.style.bins ?? 30}
          step={1}
          min={1}
          onChange={(value) => onChange({ ...layer, style: { ...layer.style, bins: Math.max(1, Math.round(value)) } })}
        />
      ) : null}
      {layer.kind === "fill_between" ? (
        <NumberField
          label="Fill alpha"
          value={layer.style.fill_alpha ?? 0.3}
          step={0.05}
          min={0}
          max={1}
          onChange={(value) => onChange({ ...layer, style: { ...layer.style, fill_alpha: value } })}
        />
      ) : null}
    </div>
  );
}

function CodePanel({ code, saveMessage }: { code: string; saveMessage: string }) {
  return (
    <section className="code-panel">
      <div className="panel-heading">
        <span>
          <FileCode2 size={16} />
          Generated code
        </span>
        {saveMessage && <small>{saveMessage}</small>}
      </div>
      <CodeMirror value={code} height="220px" extensions={[python()]} basicSetup={{ lineNumbers: true }} editable={false} />
    </section>
  );
}

function PanelTitle({ icon, title }: { icon: ReactNode; title: string }) {
  return (
    <div className="panel-title">
      {icon}
      <span>{title}</span>
    </div>
  );
}

function TextField({
  label,
  value,
  onChange
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label>
      {label}
      <input value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

function SelectField({
  label,
  value,
  options,
  optionLabel,
  onChange
}: {
  label: string;
  value: string;
  options: string[];
  optionLabel?: (value: string) => string;
  onChange: (value: string) => void;
}) {
  return (
    <label>
      {label}
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        {options.map((option) => (
          <option key={option || "none"} value={option}>
            {optionLabel ? optionLabel(option) : option}
          </option>
        ))}
      </select>
    </label>
  );
}

function NumberField({
  label,
  value,
  onChange,
  step = 0.1,
  min,
  max
}: {
  label: string;
  value: number;
  onChange: (value: number) => void;
  step?: number;
  min?: number;
  max?: number;
}) {
  return (
    <label>
      {label}
      <input
        type="number"
        value={value}
        min={min}
        max={max}
        step={step}
        onChange={(event) => onChange(Number(event.target.value))}
      />
    </label>
  );
}

function LimitField({
  label,
  value,
  onChange
}: {
  label: string;
  value: [number | null, number | null] | null;
  onChange: (value: [number | null, number | null] | null) => void;
}) {
  const current: [number | null, number | null] = value ?? [null, null];
  function update(index: 0 | 1, raw: string) {
    const next: [number | null, number | null] = [current[0], current[1]];
    next[index] = raw === "" ? null : Number(raw);
    onChange(next[0] === null && next[1] === null ? null : next);
  }
  return (
    <label>
      {label}
      <div className="limit-row">
        <input
          type="number"
          placeholder="auto"
          value={current[0] ?? ""}
          onChange={(event) => update(0, event.target.value)}
        />
        <input
          type="number"
          placeholder="auto"
          value={current[1] ?? ""}
          onChange={(event) => update(1, event.target.value)}
        />
      </div>
    </label>
  );
}

function ToggleField({
  label,
  value,
  onChange
}: {
  label: string;
  value: boolean;
  onChange: (value: boolean) => void;
}) {
  return (
    <label className="toggle-row">
      <span>{label}</span>
      <input type="checkbox" checked={value} onChange={(event) => onChange(event.target.checked)} />
    </label>
  );
}
