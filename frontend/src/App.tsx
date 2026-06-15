import CodeMirror from "@uiw/react-codemirror";
import { python } from "@codemirror/lang-python";
import {
  Braces,
  Check,
  Download,
  FileCode2,
  FlaskConical,
  Grid3X3,
  Image as ImageIcon,
  Layers3,
  Play,
  Save,
  Settings2
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
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

function createId(prefix: string): string {
  if ("randomUUID" in crypto) {
    return `${prefix}-${crypto.randomUUID().slice(0, 8)}`;
  }
  return `${prefix}-${Math.random().toString(16).slice(2, 10)}`;
}

function createLayer(kind: PlotKind, variable: VariableSummary, x?: string, y?: string): PlotLayer {
  const dataset: DatasetRef = {
    variable: variable.name,
    x: x || null,
    y: y || null
  };
  if (kind === "heatmap" || kind === "contour") {
    dataset.z = y || x || null;
    dataset.x = null;
    dataset.y = null;
  }
  const style: LayerStyle = {
    label: variable.name,
    color: kind === "heatmap" || kind === "contour" ? null : colors[0],
    marker: kind === "scatter" ? "o" : null,
    linestyle: kind === "line" || kind === "step" ? "-" : null,
    linewidth: kind === "line" || kind === "step" ? 1.8 : null,
    alpha: kind === "scatter" ? 0.85 : null,
    cmap: kind === "heatmap" || kind === "contour" ? "viridis" : null,
    bins: kind === "hist" ? 30 : null
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

  async function saveCode() {
    if (!spec || !render) {
      return;
    }
    setStatus("Saving code");
    const response = await api.saveCode(spec, render.code);
    setSaveMessage(response.message);
    setStatus(response.wrote_file ? "Script updated" : "Notebook cell ready");
  }

  async function exportFigure(format: "svg" | "png" | "pdf") {
    if (!spec) {
      return;
    }
    setStatus(`Exporting ${format.toUpperCase()}`);
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
          <button className="icon-button" title="Render now" onClick={() => spec && api.render(spec)}>
            <Play size={16} />
          </button>
          <button className="action-button" onClick={saveCode} disabled={!spec || !render}>
            <Save size={16} />
            Save code
          </button>
          <button className="icon-button" title="Export SVG" onClick={() => exportFigure("svg")}>
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
              <button onClick={() => exportFigure("png")}>PNG</button>
              <button onClick={() => exportFigure("svg")}>SVG</button>
              <button onClick={() => exportFigure("pdf")}>PDF</button>
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
  const [x, setX] = useState("");
  const [y, setY] = useState("");

  useEffect(() => {
    if (!variable) {
      return;
    }
    setX(variable.columns[0] ?? "");
    setY(variable.columns[1] ?? variable.columns[0] ?? "");
  }, [variable?.name]);

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
        <label>
          X
          <select value={x} onChange={(event) => setX(event.target.value)}>
            <option value="">index</option>
            {variable?.columns.map((column) => (
              <option key={column} value={column}>
                {column}
              </option>
            ))}
          </select>
        </label>
        <label>
          Y / value
          <select value={y} onChange={(event) => setY(event.target.value)}>
            <option value="">variable</option>
            {variable?.columns.map((column) => (
              <option key={column} value={column}>
                {column}
              </option>
            ))}
          </select>
        </label>
        <button
          className="primary-button"
          disabled={!variable}
          onClick={() => variable && onAddLayer(createLayer(kind, variable, x, y))}
        >
          <Layers3 size={16} />
          Add layer
        </button>
      </div>
    </aside>
  );
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
  onUpdateSpec
}: {
  spec?: FigureSpec;
  selectedLayer?: PlotLayer;
  onSelectLayer: (id: string) => void;
  onUpdateSpec: (updater: (spec: FigureSpec) => FigureSpec) => void;
}) {
  const axis = spec?.axes[0];
  return (
    <aside className="side-panel inspector-panel">
      <PanelTitle icon={<Settings2 size={16} />} title="Inspector" />
      {!spec || !axis ? (
        <p className="muted">Waiting for session</p>
      ) : (
        <>
          <section className="control-group">
            <h2>Figure</h2>
            <NumberField label="Width" value={spec.width} onChange={(value) => onUpdateSpec((draft) => ({ ...draft, width: value }))} />
            <NumberField label="Height" value={spec.height} onChange={(value) => onUpdateSpec((draft) => ({ ...draft, height: value }))} />
            <NumberField label="DPI" value={spec.dpi} onChange={(value) => onUpdateSpec((draft) => ({ ...draft, dpi: value }))} />
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
          </section>

          <section className="control-group">
            <h2>Axes</h2>
            <TextField label="Title" value={axis.title} onChange={(value) => updateAxis(onUpdateSpec, { title: value })} />
            <TextField label="X label" value={axis.xlabel} onChange={(value) => updateAxis(onUpdateSpec, { xlabel: value })} />
            <TextField label="Y label" value={axis.ylabel} onChange={(value) => updateAxis(onUpdateSpec, { ylabel: value })} />
            <ToggleField label="Grid" value={axis.grid} onChange={(value) => updateAxis(onUpdateSpec, { grid: value })} />
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
                  <small>{layer.kind}</small>
                </button>
              ))}
            </div>
            {selectedLayer && (
              <LayerControls
                layer={selectedLayer}
                onChange={(next) =>
                  onUpdateSpec((draft) => ({
                    ...draft,
                    layers: draft.layers.map((layer) => (layer.id === next.id ? next : layer))
                  }))
                }
              />
            )}
          </section>
        </>
      )}
    </aside>
  );
}

function updateAxis(
  onUpdateSpec: (updater: (spec: FigureSpec) => FigureSpec) => void,
  patch: Partial<AxesSpec>
) {
  onUpdateSpec((draft) => ({
    ...draft,
    axes: draft.axes.map((axis, index) => (index === 0 ? { ...axis, ...patch } : axis))
  }));
}

function LayerControls({ layer, onChange }: { layer: PlotLayer; onChange: (layer: PlotLayer) => void }) {
  return (
    <div className="layer-controls">
      <TextField
        label="Label"
        value={layer.style.label ?? ""}
        onChange={(value) => onChange({ ...layer, style: { ...layer.style, label: value } })}
      />
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
      <label>
        Marker
        <select
          value={layer.style.marker ?? ""}
          onChange={(event) => onChange({ ...layer, style: { ...layer.style, marker: event.target.value || null } })}
        >
          {markers.map((marker) => (
            <option key={marker || "none"} value={marker}>
              {marker || "none"}
            </option>
          ))}
        </select>
      </label>
      <label>
        Line style
        <select
          value={layer.style.linestyle ?? ""}
          onChange={(event) => onChange({ ...layer, style: { ...layer.style, linestyle: event.target.value || null } })}
        >
          {linestyles.map((linestyle) => (
            <option key={linestyle} value={linestyle}>
              {linestyle}
            </option>
          ))}
        </select>
      </label>
      <NumberField
        label="Alpha"
        value={layer.style.alpha ?? 1}
        step={0.05}
        min={0}
        max={1}
        onChange={(value) => onChange({ ...layer, style: { ...layer.style, alpha: value } })}
      />
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

function PanelTitle({ icon, title }: { icon: React.ReactNode; title: string }) {
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
