import {
  Braces,
  Check,
  Copy,
  Download,
  FileJson,
  FlaskConical,
  Image as ImageIcon,
  Layers3,
  Play,
  Save,
  Settings2,
  Trash2,
  Upload
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import type { ReactNode } from "react";
import { api } from "./api";
import { CodePanel } from "./CodePanel";
import { useAppStore } from "./store";
import type {
  AnnotationSpec,
  AxesSpec,
  DatasetRef,
  FigurePreset,
  FigureSpec,
  LayerStyle,
  PlotKind,
  PlotLayer,
  ValidationIssue,
  VariableSummary
} from "./types";

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

const stylePresets: Record<
  FigurePreset,
  {
    label: string;
    width?: number;
    height?: number;
    dpi?: number;
    font_family?: string | null;
    font_size?: number;
    constrained_layout?: boolean;
  }
> = {
  custom: { label: "Custom" },
  journal_single: {
    label: "Journal single column",
    width: 3.35,
    height: 2.45,
    dpi: 300,
    font_family: "Arial",
    font_size: 8,
    constrained_layout: true
  },
  journal_double: {
    label: "Journal double column",
    width: 7.0,
    height: 3.8,
    dpi: 300,
    font_family: "Arial",
    font_size: 9,
    constrained_layout: true
  },
  poster: {
    label: "Poster figure",
    width: 11.0,
    height: 7.0,
    dpi: 200,
    font_family: "DejaVu Sans",
    font_size: 16,
    constrained_layout: true
  },
  slide: {
    label: "Slide figure",
    width: 10.0,
    height: 5.625,
    dpi: 160,
    font_family: "DejaVu Sans",
    font_size: 13,
    constrained_layout: true
  }
};

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
    })),
    annotations: spec.annotations.map((annotation) => ({
      ...annotation,
      axes_id: validIds.has(annotation.axes_id) ? annotation.axes_id : axes[0].id
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

function applyPreset(spec: FigureSpec, preset: FigurePreset): FigureSpec {
  const selected = stylePresets[preset];
  return {
    ...spec,
    mode: preset === "custom" ? spec.mode : "publish",
    width: selected.width ?? spec.width,
    height: selected.height ?? spec.height,
    dpi: selected.dpi ?? spec.dpi,
    style: {
      ...spec.style,
      preset,
      font_family: selected.font_family === undefined ? spec.style.font_family : selected.font_family,
      font_size: selected.font_size ?? spec.style.font_size,
      constrained_layout: selected.constrained_layout ?? spec.style.constrained_layout
    }
  };
}

function createAnnotation(axesId: string, withArrow: boolean): AnnotationSpec {
  return {
    id: createId("annotation"),
    axes_id: axesId,
    text: withArrow ? "Callout" : "Label",
    x: 0,
    y: 0,
    xytext: withArrow ? [0.2, 0.2] : null
  };
}

function escapeAttributeValue(value: string): string {
  return value.replace(/\\/g, "\\\\").replace(/"/g, '\\"');
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
  const [validationIssues, setValidationIssues] = useState<ValidationIssue[]>([]);
  const [selectedAxisId, setSelectedAxisId] = useState("ax0");
  const [layerFocusRequest, setLayerFocusRequest] = useState<{ layerId: string; nonce: number } | null>(null);
  const manualStatusUntilRef = useRef(0);
  const pendingIssueFocusRef = useRef<ValidationIssue | null>(null);
  const specFileInputRef = useRef<HTMLInputElement>(null);

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
        const validation = await api.validate(spec);
        setValidationIssues(validation.issues);
        if (!validation.ok) {
          const count = validation.issues.filter((issue) => issue.severity === "error").length;
          setStatus(`${count} validation error${count === 1 ? "" : "s"}`);
          return;
        }
        const response = await api.render(spec, "svg");
        setRender(response);
        if (Date.now() >= manualStatusUntilRef.current) {
          setStatus("Preview synced");
        }
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

  useEffect(() => {
    if (!spec?.axes.length) {
      return;
    }
    if (!spec.axes.some((axis) => axis.id === selectedAxisId)) {
      setSelectedAxisId(spec.axes[0].id);
    }
  }, [selectedAxisId, spec?.axes]);

  function setManualStatus(message: string) {
    manualStatusUntilRef.current = Date.now() + 2000;
    setStatus(message);
  }

  function findValidationFocusTarget(issue: ValidationIssue): HTMLElement | null {
    const fieldSelector = issue.field
      ? `[data-field="${escapeAttributeValue(issue.field)}"] input, [data-field="${escapeAttributeValue(issue.field)}"] select, [data-field="${escapeAttributeValue(issue.field)}"] button`
      : "";
    const layerSelector = issue.layer_id
      ? `[data-testid="layer-row"][data-layer-id="${escapeAttributeValue(issue.layer_id)}"]`
      : "";
    const axesSelector = issue.axes_id ? `[data-axes-id="${escapeAttributeValue(issue.axes_id)}"]` : "";
    return document.querySelector<HTMLElement>(
      [fieldSelector, layerSelector, axesSelector].filter(Boolean).join(", ")
    );
  }

  function focusValidationIssue(issue: ValidationIssue) {
    pendingIssueFocusRef.current = issue;
    if (issue.axes_id) {
      setSelectedAxisId(issue.axes_id);
    }
    if (issue.layer_id) {
      setSelectedLayerId(issue.layer_id);
      setLayerFocusRequest({ layerId: issue.layer_id, nonce: Date.now() });
    }
  }

  useEffect(() => {
    const issue = pendingIssueFocusRef.current;
    if (!issue) {
      return;
    }
    if (issue.axes_id && selectedAxisId !== issue.axes_id) {
      return;
    }
    if (issue.layer_id && selectedLayerId !== issue.layer_id) {
      return;
    }
    const focusTarget = () => {
      const target = findValidationFocusTarget(issue);
      target?.scrollIntoView({ block: "center", behavior: "smooth" });
      target?.focus({ preventScroll: true });
    };
    window.requestAnimationFrame(focusTarget);
    const timeout = window.setTimeout(focusTarget, 80);
    pendingIssueFocusRef.current = null;
    return () => window.clearTimeout(timeout);
  }, [selectedAxisId, selectedLayerId, spec?.axes, spec?.layers]);

  async function renderNow() {
    if (!spec) {
      return;
    }
    setStatus("Rendering");
    try {
      const validation = await api.validate(spec);
      setValidationIssues(validation.issues);
      if (!validation.ok) {
        setStatus("Fix validation errors");
        return;
      }
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
      const validation = await api.validate(spec);
      setValidationIssues(validation.issues);
      if (!validation.ok) {
        setStatus("Fix validation errors before export");
        return;
      }
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
      setManualStatus(`${format.toUpperCase()} export ready`);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Export failed");
    }
  }

  function exportSpec() {
    if (!spec) {
      return;
    }
    const blob = new Blob([JSON.stringify(spec, null, 2)], { type: "application/json" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "figure.figstudio.json";
    link.click();
    URL.revokeObjectURL(link.href);
    setStatus("FigureSpec exported");
  }

  async function importSpec(file?: File) {
    if (!file) {
      return;
    }
    try {
      const raw = JSON.parse(await file.text()) as Partial<FigureSpec>;
      const imported = {
        ...raw,
        axes: raw.axes ?? [createAxis(0, 0, 0)],
        layers: raw.layers ?? [],
        annotations: raw.annotations ?? [],
        style: {
          preset: "custom",
          title: "",
          font_size: 10,
          constrained_layout: true,
          ...(raw.style ?? {})
        }
      } as FigureSpec;
      setSpec(imported);
      setSelectedLayerId(imported.layers[0]?.id ?? "");
      setStatus("FigureSpec imported");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Spec import failed");
    } finally {
      if (specFileInputRef.current) {
        specFileInputRef.current.value = "";
      }
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
    <main className="app-shell" data-testid="app-shell">
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
        <div className="mode-switch" role="group" aria-label="Mode" data-testid="mode-switch">
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
          <input
            ref={specFileInputRef}
            className="hidden-file-input"
            data-testid="import-spec-input"
            type="file"
            accept=".json,.figstudio.json,application/json"
            onChange={(event) => importSpec(event.target.files?.[0])}
          />
          <button
            className="icon-button"
            data-testid="import-spec-button"
            title="Import FigureSpec"
            onClick={() => specFileInputRef.current?.click()}
          >
            <Upload size={16} />
          </button>
          <button
            className="icon-button"
            data-testid="export-spec-button"
            title="Export FigureSpec"
            onClick={exportSpec}
            disabled={!spec}
          >
            <FileJson size={16} />
          </button>
          <button
            className="icon-button"
            data-testid="render-button"
            title="Render now"
            onClick={renderNow}
            disabled={!spec}
          >
            <Play size={16} />
          </button>
          <button className="action-button" data-testid="save-code-button" onClick={saveCode} disabled={!spec}>
            <Save size={16} />
            Save code
          </button>
          <button
            className="icon-button"
            data-testid="export-svg-toolbar-button"
            title="Export SVG"
            onClick={() => exportFigure("svg")}
            disabled={!spec}
          >
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
            <div className="status-line" data-testid="status-line">
              <Check size={15} />
              {status}
            </div>
            <div className="export-set">
              <button data-testid="export-png-button" onClick={() => exportFigure("png")} disabled={!spec}>
                PNG
              </button>
              <button data-testid="export-svg-button" onClick={() => exportFigure("svg")} disabled={!spec}>
                SVG
              </button>
              <button data-testid="export-pdf-button" onClick={() => exportFigure("pdf")} disabled={!spec}>
                PDF
              </button>
            </div>
          </div>
          <Preview render={render} issues={validationIssues} onIssueSelect={focusValidationIssue} />
          <CodePanel code={render?.code ?? ""} saveMessage={saveMessage} />
        </section>

        <Inspector
          spec={spec}
          selectedLayer={selectedLayer}
          selectedAxisId={selectedAxisId}
          layerFocusRequest={layerFocusRequest}
          onSelectLayer={setSelectedLayerId}
          onSelectAxis={setSelectedAxisId}
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
    <aside className="side-panel variables-panel" data-testid="variable-panel">
      <PanelTitle icon={<Braces size={16} />} title="Variables" />
      <div className="variable-list">
        {variables.map((item) => (
          <button
            key={item.name}
            className={`variable-row ${item.name === variable?.name ? "selected" : ""}`}
            data-testid="variable-row"
            data-variable-name={item.name}
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
          <select
            data-testid="plot-kind-select"
            value={kind}
            onChange={(event) => setKind(event.target.value as PlotKind)}
          >
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
            <select
              data-testid="y-source-select"
              value={yVar?.name ?? ""}
              onChange={(event) => setYVariable(event.target.value)}
            >
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
              <select
                data-testid="y-column-select"
                value={yColumn}
                onChange={(event) => setYColumn(event.target.value)}
              >
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
            <select
              data-testid="x-source-select"
              value={xVariable}
              onChange={(event) => setXVariable(event.target.value)}
            >
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
              <select
                data-testid="x-column-select"
                value={xColumn}
                onChange={(event) => setXColumn(event.target.value)}
              >
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
              <select
                data-testid="error-source-select"
                value={yerrVariable}
                onChange={(event) => setYerrVariable(event.target.value)}
              >
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
                <select
                  data-testid="error-column-select"
                  value={yerrColumn}
                  onChange={(event) => setYerrColumn(event.target.value)}
                >
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
          data-testid="add-layer-button"
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

function Preview({
  render,
  issues,
  onIssueSelect
}: {
  render?: { image: string; format: string };
  issues: ValidationIssue[];
  onIssueSelect: (issue: ValidationIssue) => void;
}) {
  const src =
    render?.format === "svg"
      ? `data:image/svg+xml;charset=utf-8,${encodeURIComponent(render.image)}`
      : render?.image
        ? `data:image/png;base64,${render.image}`
        : "";

  return (
    <section className="preview-surface" data-testid="preview-surface">
      {issues.length ? <ValidationList issues={issues} onIssueSelect={onIssueSelect} /> : null}
      {src ? (
        <div className="figure-frame" data-testid="figure-frame">
          <img data-testid="figure-preview" src={src} alt="Matplotlib preview" />
          <div className="overlay-handle top-left" />
          <div className="overlay-handle top-right" />
          <div className="overlay-handle bottom-left" />
          <div className="overlay-handle bottom-right" />
        </div>
      ) : (
        <div className="empty-preview" data-testid="empty-preview">
          <ImageIcon size={32} />
          <span>Add a layer to render a Matplotlib preview</span>
        </div>
      )}
    </section>
  );
}

function ValidationList({
  issues,
  onIssueSelect
}: {
  issues: ValidationIssue[];
  onIssueSelect: (issue: ValidationIssue) => void;
}) {
  return (
    <div className="validation-list" data-testid="validation-list">
      {issues.map((issue, index) => (
        <button
          type="button"
          key={`${issue.code}-${issue.layer_id ?? "figure"}-${index}`}
          className={`validation-item ${issue.severity}`}
          data-testid="validation-issue"
          data-layer-id={issue.layer_id ?? undefined}
          data-axes-id={issue.axes_id ?? undefined}
          onClick={() => onIssueSelect(issue)}
        >
          <strong>{issue.code}</strong>
          <span>{issue.message}</span>
        </button>
      ))}
    </div>
  );
}

function AnnotationControls({
  annotations,
  selectedAxisId,
  onUpdateSpec
}: {
  annotations: AnnotationSpec[];
  selectedAxisId: string;
  onUpdateSpec: (updater: (spec: FigureSpec) => FigureSpec) => void;
}) {
  function addAnnotation(withArrow: boolean) {
    const annotation = createAnnotation(selectedAxisId, withArrow);
    onUpdateSpec((draft) => ({
      ...draft,
      annotations: [...draft.annotations, annotation]
    }));
  }

  function updateAnnotation(id: string, patch: Partial<AnnotationSpec>) {
    onUpdateSpec((draft) => ({
      ...draft,
      annotations: draft.annotations.map((annotation) =>
        annotation.id === id ? { ...annotation, ...patch } : annotation
      )
    }));
  }

  function deleteAnnotation(id: string) {
    onUpdateSpec((draft) => ({
      ...draft,
      annotations: draft.annotations.filter((annotation) => annotation.id !== id)
    }));
  }

  return (
    <section className="control-group" data-testid="annotation-controls">
      <h2>Annotations</h2>
      <div className="layer-actions">
        <button className="mini-button" data-testid="add-text-annotation-button" onClick={() => addAnnotation(false)}>
          Text
        </button>
        <button className="mini-button" data-testid="add-arrow-annotation-button" onClick={() => addAnnotation(true)}>
          Arrow
        </button>
      </div>
      {annotations.length ? (
        <div className="annotation-list" data-testid="annotation-list">
          {annotations.map((annotation) => {
            const xytext = annotation.xytext ?? [annotation.x, annotation.y];
            return (
              <div key={annotation.id} className="annotation-card" data-testid="annotation-card">
                <TextField
                  label="Text"
                  value={annotation.text}
                  testId="annotation-text-field"
                  onChange={(value) => updateAnnotation(annotation.id, { text: value })}
                />
                <div className="split-row">
                  <NumberField
                    label="X"
                    value={annotation.x}
                    testId="annotation-x-field"
                    onChange={(value) => updateAnnotation(annotation.id, { x: value })}
                  />
                  <NumberField
                    label="Y"
                    value={annotation.y}
                    testId="annotation-y-field"
                    onChange={(value) => updateAnnotation(annotation.id, { y: value })}
                  />
                </div>
                <ToggleField
                  label="Arrow"
                  value={annotation.xytext !== null && annotation.xytext !== undefined}
                  testId="annotation-arrow-toggle"
                  onChange={(value) =>
                    updateAnnotation(annotation.id, {
                      xytext: value ? [annotation.x + 0.2, annotation.y + 0.2] : null
                    })
                  }
                />
                {annotation.xytext ? (
                  <div className="split-row">
                    <NumberField
                      label="Text X"
                      value={xytext[0]}
                      testId="annotation-text-x-field"
                      onChange={(value) => updateAnnotation(annotation.id, { xytext: [value, xytext[1]] })}
                    />
                    <NumberField
                      label="Text Y"
                      value={xytext[1]}
                      testId="annotation-text-y-field"
                      onChange={(value) => updateAnnotation(annotation.id, { xytext: [xytext[0], value] })}
                    />
                  </div>
                ) : null}
                <button
                  className="mini-button danger-button"
                  data-testid="delete-annotation-button"
                  onClick={() => deleteAnnotation(annotation.id)}
                >
                  <Trash2 size={14} />
                  Delete
                </button>
              </div>
            );
          })}
        </div>
      ) : (
        <p className="muted">No annotations on this axes.</p>
      )}
    </section>
  );
}

function Inspector({
  spec,
  selectedLayer,
  selectedAxisId,
  layerFocusRequest,
  onSelectLayer,
  onSelectAxis,
  onUpdateSpec,
  onDeleteLayer,
  onDuplicateLayer
}: {
  spec?: FigureSpec;
  selectedLayer?: PlotLayer;
  selectedAxisId: string;
  layerFocusRequest: { layerId: string; nonce: number } | null;
  onSelectLayer: (id: string) => void;
  onSelectAxis: (id: string) => void;
  onUpdateSpec: (updater: (spec: FigureSpec) => FigureSpec) => void;
  onDeleteLayer: (id: string) => void;
  onDuplicateLayer: (layer: PlotLayer) => void;
}) {
  const selectedAxis = spec?.axes.find((axis) => axis.id === selectedAxisId) ?? spec?.axes[0];

  return (
    <aside className="side-panel inspector-panel" data-testid="inspector-panel">
      <PanelTitle icon={<Settings2 size={16} />} title="Inspector" />
      {!spec || !selectedAxis ? (
        <p className="muted">Waiting for session</p>
      ) : (
        <>
          <section className="control-group">
            <h2>Figure</h2>
            <SelectField
              label="Style preset"
              value={spec.style.preset ?? "custom"}
              options={Object.keys(stylePresets)}
              testId="style-preset-field"
              field="style.preset"
              optionLabel={(value) => stylePresets[value as FigurePreset].label}
              onChange={(value) => onUpdateSpec((draft) => applyPreset(draft, value as FigurePreset))}
            />
            <div className="split-row">
              <NumberField
                label="Width"
                value={spec.width}
                testId="figure-width-field"
                field="width"
                onChange={(value) => onUpdateSpec((draft) => ({ ...draft, width: value }))}
              />
              <NumberField
                label="Height"
                value={spec.height}
                testId="figure-height-field"
                field="height"
                onChange={(value) => onUpdateSpec((draft) => ({ ...draft, height: value }))}
              />
            </div>
            <div className="split-row">
              <NumberField
                label="DPI"
                value={spec.dpi}
                step={1}
                min={24}
                testId="figure-dpi-field"
                field="dpi"
                onChange={(value) => onUpdateSpec((draft) => ({ ...draft, dpi: value }))}
              />
              <NumberField
                label="Font size"
                value={spec.style.font_size}
                testId="font-size-field"
                field="style.font_size"
                onChange={(value) =>
                  onUpdateSpec((draft) => ({
                    ...draft,
                    style: { ...draft.style, font_size: value }
                  }))
                }
              />
            </div>
            <div className="split-row">
              <NumberField
                label="Rows"
                value={spec.rows}
                step={1}
                min={1}
                max={6}
                testId="rows-field"
                field="rows"
                onChange={(value) => onUpdateSpec((draft) => resizeAxes(draft, value, draft.cols))}
              />
              <NumberField
                label="Cols"
                value={spec.cols}
                step={1}
                min={1}
                max={6}
                testId="cols-field"
                field="cols"
                onChange={(value) => onUpdateSpec((draft) => resizeAxes(draft, draft.rows, value))}
              />
            </div>
            <TextField
              label="Suptitle"
              value={spec.style.title}
              testId="suptitle-field"
              field="style.title"
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
                  testId="font-family-field"
                  field="style.font_family"
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
                  testId="constrained-layout-field"
                  field="style.constrained_layout"
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
              <select
                data-testid="active-axes-select"
                data-field="axes_id"
                value={selectedAxis.id}
                onChange={(event) => onSelectAxis(event.target.value)}
              >
                {spec.axes.map((axis, index) => (
                  <option key={axis.id} value={axis.id}>
                    {axis.id} ({axis.row + 1}, {axis.col + 1}) {index === 0 ? "primary" : ""}
                  </option>
                ))}
              </select>
            </label>
            <TextField
              label="Title"
              value={selectedAxis.title}
              testId="axis-title-field"
              field="axes.title"
              onChange={(value) => updateAxis(onUpdateSpec, selectedAxis.id, { title: value })}
            />
            <TextField
              label="X label"
              value={selectedAxis.xlabel}
              testId="axis-xlabel-field"
              field="axes.xlabel"
              onChange={(value) => updateAxis(onUpdateSpec, selectedAxis.id, { xlabel: value })}
            />
            <TextField
              label="Y label"
              value={selectedAxis.ylabel}
              testId="axis-ylabel-field"
              field="axes.ylabel"
              onChange={(value) => updateAxis(onUpdateSpec, selectedAxis.id, { ylabel: value })}
            />
            <div className="split-row">
              <SelectField
                label="X scale"
                value={selectedAxis.xscale}
                options={scales}
                testId="axis-xscale-field"
                field="axes.xscale"
                onChange={(value) => updateAxis(onUpdateSpec, selectedAxis.id, { xscale: value as AxesSpec["xscale"] })}
              />
              <SelectField
                label="Y scale"
                value={selectedAxis.yscale}
                options={scales}
                testId="axis-yscale-field"
                field="axes.yscale"
                onChange={(value) => updateAxis(onUpdateSpec, selectedAxis.id, { yscale: value as AxesSpec["yscale"] })}
              />
            </div>
            <LimitField
              label="X limits"
              value={selectedAxis.xlim ?? null}
              testId="axis-xlim-field"
              field="axes.xlim"
              onChange={(value) => updateAxis(onUpdateSpec, selectedAxis.id, { xlim: value })}
            />
            <LimitField
              label="Y limits"
              value={selectedAxis.ylim ?? null}
              testId="axis-ylim-field"
              field="axes.ylim"
              onChange={(value) => updateAxis(onUpdateSpec, selectedAxis.id, { ylim: value })}
            />
            <ToggleField
              label="Grid"
              value={selectedAxis.grid}
              testId="axis-grid-field"
              field="axes.grid"
              onChange={(value) => updateAxis(onUpdateSpec, selectedAxis.id, { grid: value })}
            />
            <ToggleField
              label="Legend"
              value={selectedAxis.legend}
              testId="axis-legend-field"
              field="axes.legend"
              onChange={(value) => updateAxis(onUpdateSpec, selectedAxis.id, { legend: value })}
            />
            <ToggleField
              label="Contour colorbar"
              value={selectedAxis.colorbar}
              testId="axis-colorbar-field"
              field="axes.colorbar"
              onChange={(value) => updateAxis(onUpdateSpec, selectedAxis.id, { colorbar: value })}
            />
          </section>

          <AnnotationControls
            annotations={spec.annotations.filter((annotation) => annotation.axes_id === selectedAxis.id)}
            selectedAxisId={selectedAxis.id}
            onUpdateSpec={onUpdateSpec}
          />

          <section className="control-group">
            <h2>Layers</h2>
            <div className="layer-list">
              {spec.layers.map((layer) => (
                <button
                  key={layer.id}
                  className={layer.id === selectedLayer?.id ? "selected" : ""}
                  data-testid="layer-row"
                  data-layer-id={layer.id}
                  data-axes-id={layer.axes_id}
                  ref={(node) => {
                    if (node && layerFocusRequest?.layerId === layer.id) {
                      window.setTimeout(() => node.focus({ preventScroll: true }), 0);
                    }
                  }}
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
                  <button className="mini-button" data-testid="duplicate-layer-button" onClick={() => onDuplicateLayer(selectedLayer)}>
                    <Copy size={14} />
                    Duplicate
                  </button>
                  <button
                    className="mini-button danger-button"
                    data-testid="delete-layer-button"
                    onClick={() => onDeleteLayer(selectedLayer.id)}
                  >
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
        testId="layer-axes-field"
        field="axes_id"
        onChange={(value) => onChange({ ...layer, axes_id: value })}
      />
      <SelectField
        label="Plot type"
        value={layer.kind}
        options={plotKinds}
        testId="layer-kind-field"
        field="kind"
        onChange={(value) => onChange({ ...layer, kind: value as PlotKind })}
      />
      <TextField
        label="Label"
        value={layer.style.label ?? ""}
        testId="layer-label-field"
        field="style.label"
        onChange={(value) => onChange({ ...layer, style: { ...layer.style, label: value || null } })}
      />
      {isFieldLayer ? (
        <SelectField
          label="Colormap"
          value={layer.style.cmap ?? "viridis"}
          options={cmaps}
          testId="layer-cmap-field"
          field="style.cmap"
          onChange={(value) => onChange({ ...layer, style: { ...layer.style, cmap: value } })}
        />
      ) : (
        <label data-testid="layer-color-field" data-field="style.color">
          Color
          <div className="swatches">
            {colors.map((color) => (
              <button
                key={color}
                className={layer.style.color === color ? "selected" : ""}
                style={{ background: color }}
                aria-label={color}
                data-testid="color-swatch"
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
          testId="layer-marker-field"
          field="style.marker"
          optionLabel={(value) => value || "none"}
          onChange={(value) => onChange({ ...layer, style: { ...layer.style, marker: value || null } })}
        />
        <SelectField
          label="Line style"
          value={layer.style.linestyle ?? ""}
          options={linestyles}
          testId="layer-linestyle-field"
          field="style.linestyle"
          onChange={(value) => onChange({ ...layer, style: { ...layer.style, linestyle: value || null } })}
        />
      </div>
      <div className="split-row">
        <NumberField
          label="Line width"
          value={layer.style.linewidth ?? 1.8}
          step={0.1}
          min={0}
          testId="layer-linewidth-field"
          field="style.linewidth"
          onChange={(value) => onChange({ ...layer, style: { ...layer.style, linewidth: value } })}
        />
        <NumberField
          label="Alpha"
          value={layer.style.alpha ?? 1}
          step={0.05}
          min={0}
          max={1}
          testId="layer-alpha-field"
          field="style.alpha"
          onChange={(value) => onChange({ ...layer, style: { ...layer.style, alpha: value } })}
        />
      </div>
      {layer.kind === "hist" ? (
        <NumberField
          label="Bins"
          value={layer.style.bins ?? 30}
          step={1}
          min={1}
          testId="layer-bins-field"
          field="style.bins"
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
          testId="layer-fill-alpha-field"
          field="style.fill_alpha"
          onChange={(value) => onChange({ ...layer, style: { ...layer.style, fill_alpha: value } })}
        />
      ) : null}
    </div>
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
  testId,
  field,
  onChange
}: {
  label: string;
  value: string;
  testId?: string;
  field?: string;
  onChange: (value: string) => void;
}) {
  return (
    <label data-testid={testId} data-field={field}>
      {label}
      <input
        data-testid={testId ? `${testId}-input` : undefined}
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

function SelectField({
  label,
  value,
  options,
  optionLabel,
  testId,
  field,
  onChange
}: {
  label: string;
  value: string;
  options: string[];
  optionLabel?: (value: string) => string;
  testId?: string;
  field?: string;
  onChange: (value: string) => void;
}) {
  return (
    <label data-testid={testId} data-field={field}>
      {label}
      <select
        data-testid={testId ? `${testId}-select` : undefined}
        value={value}
        onChange={(event) => onChange(event.target.value)}
      >
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
  max,
  testId,
  field
}: {
  label: string;
  value: number;
  onChange: (value: number) => void;
  step?: number;
  min?: number;
  max?: number;
  testId?: string;
  field?: string;
}) {
  return (
    <label data-testid={testId} data-field={field}>
      {label}
      <input
        type="number"
        data-testid={testId ? `${testId}-input` : undefined}
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
  testId,
  field,
  onChange
}: {
  label: string;
  value: [number | null, number | null] | null;
  testId?: string;
  field?: string;
  onChange: (value: [number | null, number | null] | null) => void;
}) {
  const current: [number | null, number | null] = value ?? [null, null];
  function update(index: 0 | 1, raw: string) {
    const next: [number | null, number | null] = [current[0], current[1]];
    next[index] = raw === "" ? null : Number(raw);
    onChange(next[0] === null && next[1] === null ? null : next);
  }
  return (
    <label data-testid={testId} data-field={field}>
      {label}
      <div className="limit-row">
        <input
          type="number"
          data-testid={testId ? `${testId}-min-input` : undefined}
          placeholder="auto"
          value={current[0] ?? ""}
          onChange={(event) => update(0, event.target.value)}
        />
        <input
          type="number"
          data-testid={testId ? `${testId}-max-input` : undefined}
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
  testId,
  field,
  onChange
}: {
  label: string;
  value: boolean;
  testId?: string;
  field?: string;
  onChange: (value: boolean) => void;
}) {
  return (
    <label className="toggle-row" data-testid={testId} data-field={field}>
      <span>{label}</span>
      <input
        type="checkbox"
        data-testid={testId ? `${testId}-input` : undefined}
        checked={value}
        onChange={(event) => onChange(event.target.checked)}
      />
    </label>
  );
}
