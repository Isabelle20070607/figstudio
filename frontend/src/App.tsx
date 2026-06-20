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
  DataFilterSpec,
  FacetValue,
  DatasetRef,
  FigurePreset,
  FigureSpec,
  LayerYAxis,
  LayerStyle,
  PlotKind,
  PlotLayer,
  ReferenceLineOrientation,
  ReferenceLineSpec,
  RecipeKind,
  RecipeLayer,
  RepeatedPanelCandidate,
  RepeatedPanelSkippedCandidate,
  RepeatedPanelSourceKind,
  SecondaryYAxisSpec,
  StyleProfile,
  StyleProfilesResponse,
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

const recipeKinds: RecipeKind[] = ["mean_sem_line", "grouped_points", "paired_before_after"];
const recipeLabels: Record<RecipeKind, string> = {
  mean_sem_line: "Mean +/- SEM line",
  grouped_points: "Grouped points",
  paired_before_after: "Paired before/after"
};
const errorModes: RecipeLayer["error"][] = ["sem", "sd", "none"];
const referenceLineOrientations: ReferenceLineOrientation[] = ["horizontal", "vertical"];

const colors = ["#2563eb", "#0f766e", "#dc2626", "#9333ea", "#b45309", "#111827"];
const markers = ["", "o", "s", "^", "D", "x"];
const linestyles = ["-", "--", "-.", ":"];
const cmaps = ["viridis", "magma", "plasma", "cividis", "coolwarm", "Greys"];
const scales: AxesSpec["xscale"][] = ["linear", "log", "symlog", "logit"];
const yAxisTargets: LayerYAxis[] = ["left", "right"];
const secondaryYAxisLayerKinds = new Set<PlotKind>([
  "line",
  "scatter",
  "bar",
  "hist",
  "errorbar",
  "step",
  "fill_between"
]);
const indexSource = "__index__";
const noneSource = "__none__";
const defaultFacetLimit = 12;

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

type LayoutPreset = "single" | "two_columns" | "two_rows" | "two_by_two" | "large_left" | "large_top";
type LayoutPresetValue = LayoutPreset | "custom";
type AxesGeometry = Pick<AxesSpec, "id" | "row" | "col" | "rowspan" | "colspan">;

const layoutPresets: Record<
  LayoutPreset,
  {
    label: string;
    rows: number;
    cols: number;
    axes: AxesGeometry[];
  }
> = {
  single: {
    label: "Single panel",
    rows: 1,
    cols: 1,
    axes: [{ id: "ax0", row: 0, col: 0, rowspan: 1, colspan: 1 }]
  },
  two_columns: {
    label: "Two columns",
    rows: 1,
    cols: 2,
    axes: [
      { id: "ax0", row: 0, col: 0, rowspan: 1, colspan: 1 },
      { id: "ax1", row: 0, col: 1, rowspan: 1, colspan: 1 }
    ]
  },
  two_rows: {
    label: "Two rows",
    rows: 2,
    cols: 1,
    axes: [
      { id: "ax0", row: 0, col: 0, rowspan: 1, colspan: 1 },
      { id: "ax1", row: 1, col: 0, rowspan: 1, colspan: 1 }
    ]
  },
  two_by_two: {
    label: "Two by two",
    rows: 2,
    cols: 2,
    axes: [
      { id: "ax0", row: 0, col: 0, rowspan: 1, colspan: 1 },
      { id: "ax1", row: 0, col: 1, rowspan: 1, colspan: 1 },
      { id: "ax2", row: 1, col: 0, rowspan: 1, colspan: 1 },
      { id: "ax3", row: 1, col: 1, rowspan: 1, colspan: 1 }
    ]
  },
  large_left: {
    label: "Large left",
    rows: 2,
    cols: 2,
    axes: [
      { id: "ax0", row: 0, col: 0, rowspan: 2, colspan: 1 },
      { id: "ax1", row: 0, col: 1, rowspan: 1, colspan: 1 },
      { id: "ax2", row: 1, col: 1, rowspan: 1, colspan: 1 }
    ]
  },
  large_top: {
    label: "Large top",
    rows: 2,
    cols: 2,
    axes: [
      { id: "ax0", row: 0, col: 0, rowspan: 1, colspan: 2 },
      { id: "ax1", row: 1, col: 0, rowspan: 1, colspan: 1 },
      { id: "ax2", row: 1, col: 1, rowspan: 1, colspan: 1 }
    ]
  }
};

const layoutPresetOrder: LayoutPreset[] = [
  "single",
  "two_columns",
  "two_rows",
  "two_by_two",
  "large_left",
  "large_top"
];

type FigureOverrideField =
  | "width"
  | "height"
  | "dpi"
  | "font_family"
  | "font_size"
  | "constrained_layout";

interface FacetBuildPayload {
  axes: AxesSpec[];
  rows: number;
  cols: number;
  shareX: boolean;
  shareY: boolean;
  layers?: PlotLayer[];
  recipes?: RecipeLayer[];
  message?: string;
}

function createId(prefix: string): string {
  if ("randomUUID" in crypto) {
    return `${prefix}-${crypto.randomUUID().slice(0, 8)}`;
  }
  return `${prefix}-${Math.random().toString(16).slice(2, 10)}`;
}

function profileById(styleProfiles: StyleProfilesResponse, profileId?: string | null): StyleProfile | undefined {
  if (!profileId) {
    return undefined;
  }
  return styleProfiles.profiles.find((profile) => profile.id === profileId);
}

function hasFigureOverride(spec: FigureSpec, field: FigureOverrideField): boolean {
  return spec.style.profile_overrides?.includes(field) ?? false;
}

function effectiveFigureValue(
  spec: FigureSpec,
  styleProfiles: StyleProfilesResponse,
  field: FigureOverrideField
): number | string | boolean | null {
  const profile = profileById(styleProfiles, spec.style.profile_id);
  if (profile && !hasFigureOverride(spec, field)) {
    const value = profile.figure[field];
    if (value !== undefined && value !== null) {
      return value;
    }
  }
  if (field === "font_family" || field === "font_size" || field === "constrained_layout") {
    return spec.style[field] ?? null;
  }
  return spec[field];
}

function addFigureOverride(spec: FigureSpec, field: FigureOverrideField): string[] {
  const overrides = spec.style.profile_overrides ?? [];
  return overrides.includes(field) ? overrides : [...overrides, field];
}

function updateFigureField(
  spec: FigureSpec,
  field: FigureOverrideField,
  value: number | string | boolean | null
): FigureSpec {
  const style = {
    ...spec.style,
    profile_overrides: spec.style.profile_id ? addFigureOverride(spec, field) : (spec.style.profile_overrides ?? [])
  };
  if (field === "font_family" || field === "font_size" || field === "constrained_layout") {
    return {
      ...spec,
      style: {
        ...style,
        [field]: value
      }
    };
  }
  return {
    ...spec,
    [field]: value,
    style
  };
}

function applyStyleProfile(spec: FigureSpec, profileId: string): FigureSpec {
  return {
    ...spec,
    mode: profileId ? "publish" : spec.mode,
    style: {
      ...spec.style,
      preset: profileId ? "custom" : spec.style.preset,
      profile_id: profileId || null,
      profile_overrides: []
    }
  };
}

function profileLayerDefaults(
  spec: FigureSpec,
  styleProfiles: StyleProfilesResponse,
  layer: PlotLayer
): LayerStyle | undefined {
  return profileById(styleProfiles, spec.style.profile_id)?.layers[layer.kind];
}

function profileRecipeDefaults(
  spec: FigureSpec,
  styleProfiles: StyleProfilesResponse,
  recipe: RecipeLayer
): LayerStyle | undefined {
  return profileById(styleProfiles, spec.style.profile_id)?.recipes[recipe.kind];
}

function inheritedStyleValue<T extends keyof LayerStyle>(
  style: LayerStyle,
  defaults: LayerStyle | undefined,
  field: T
): LayerStyle[T] {
  return style[field] ?? defaults?.[field] ?? null;
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

function isNumericDtype(dtype?: string): boolean {
  return Boolean(dtype && /int|float|double|decimal|number|bool/i.test(dtype));
}

function defaultFacetColumn(variable?: VariableSummary): string {
  return variable?.columns.find((column) => !isNumericDtype(variable.dtypes[column])) ?? firstColumn(variable);
}

function facetDisplayLabel(value: FacetValue): string {
  return value.label || String(value.value ?? "");
}

function facetFilter(column: string, value: FacetValue): DataFilterSpec {
  return {
    column,
    op: "eq",
    value: value.value ?? null,
    label: facetDisplayLabel(value)
  };
}

function facetLayout(count: number): { rows: number; cols: number } {
  const cols = Math.max(1, Math.min(3, count));
  return {
    rows: Math.max(1, Math.ceil(count / cols)),
    cols
  };
}

function createSecondaryYAxis(existing?: Partial<SecondaryYAxisSpec> | null): SecondaryYAxisSpec {
  return {
    ylabel: existing?.ylabel ?? "",
    yscale: existing?.yscale ?? "linear",
    ylim: existing?.ylim ?? null
  };
}

function createFacetAxes(values: FacetValue[], column: string, cols: number): AxesSpec[] {
  return values.map((value, index) => ({
    id: `ax${index}`,
    row: Math.floor(index / cols),
    col: index % cols,
    rowspan: 1,
    colspan: 1,
    title: `${column}: ${facetDisplayLabel(value)}`,
    xlabel: "",
    ylabel: "",
    xscale: "linear",
    yscale: "linear",
    xlim: null,
    ylim: null,
    secondary_y: createSecondaryYAxis(),
    grid: false,
    legend: true,
    colorbar: false
  }));
}

function repeatedPanelLabel(candidate: RepeatedPanelCandidate): string {
  return candidate.label || String(candidate.value ?? "");
}

function createRepeatedPanelAxes(candidates: RepeatedPanelCandidate[], titlePrefix: string, cols: number): AxesSpec[] {
  return candidates.map((candidate, index) => ({
    id: `ax${index}`,
    row: Math.floor(index / cols),
    col: index % cols,
    rowspan: 1,
    colspan: 1,
    title: `${titlePrefix}: ${repeatedPanelLabel(candidate)}`,
    xlabel: "",
    ylabel: "",
    xscale: "linear",
    yscale: "linear",
    xlim: null,
    ylim: null,
    secondary_y: createSecondaryYAxis(),
    grid: false,
    legend: true,
    colorbar: false
  }));
}

function normalizeDatasetRef(dataset: DatasetRef): DatasetRef {
  return {
    ...dataset,
    selection: dataset.selection ?? null,
    filters: dataset.filters ?? []
  };
}

function normalizeLayer(layer: PlotLayer): PlotLayer {
  return {
    ...layer,
    y_axis: layer.y_axis ?? "left",
    dataset: normalizeDatasetRef(layer.dataset)
  };
}

function normalizeRecipeDatasetRef(dataset: RecipeLayer["dataset"]): RecipeLayer["dataset"] {
  return {
    ...dataset,
    filters: dataset.filters ?? []
  };
}

function createAxis(
  index: number,
  row: number,
  col: number,
  existing?: AxesSpec,
  geometry?: Partial<Pick<AxesSpec, "id" | "rowspan" | "colspan">>
): AxesSpec {
  return {
    id: geometry?.id ?? `ax${index}`,
    row,
    col,
    rowspan: geometry?.rowspan ?? existing?.rowspan ?? 1,
    colspan: geometry?.colspan ?? existing?.colspan ?? 1,
    title: existing?.title ?? "",
    xlabel: existing?.xlabel ?? "",
    ylabel: existing?.ylabel ?? "",
    xscale: existing?.xscale ?? "linear",
    yscale: existing?.yscale ?? "linear",
    xlim: existing?.xlim ?? null,
    ylim: existing?.ylim ?? null,
    secondary_y: createSecondaryYAxis(existing?.secondary_y),
    grid: existing?.grid ?? false,
    legend: existing?.legend ?? true,
    colorbar: existing?.colorbar ?? false
  };
}

function normalizeAxis(axis: AxesSpec, index: number): AxesSpec {
  return createAxis(index, axis.row ?? 0, axis.col ?? 0, axis, {
    id: axis.id ?? `ax${index}`,
    rowspan: axis.rowspan ?? 1,
    colspan: axis.colspan ?? 1
  });
}

function resizeAxes(spec: FigureSpec, rows: number, cols: number): FigureSpec {
  const nextRows = Math.max(1, Math.min(6, Math.round(rows || 1)));
  const nextCols = Math.max(1, Math.min(6, Math.round(cols || 1)));
  const axes: AxesSpec[] = [];
  for (let row = 0; row < nextRows; row += 1) {
    for (let col = 0; col < nextCols; col += 1) {
      const index = axes.length;
      axes.push(createAxis(index, row, col, spec.axes[index], { rowspan: 1, colspan: 1 }));
    }
  }
  return withValidAxesTargets({ ...spec, rows: nextRows, cols: nextCols, axes }, axes);
}

function applyLayoutPreset(spec: FigureSpec, preset: LayoutPreset): FigureSpec {
  const definition = layoutPresets[preset];
  const existingById = new Map(spec.axes.map((axis) => [axis.id, axis]));
  const axes = definition.axes.map((geometry, index) =>
    createAxis(index, geometry.row, geometry.col, existingById.get(geometry.id) ?? spec.axes[index], geometry)
  );
  return withValidAxesTargets(
    {
      ...spec,
      rows: definition.rows,
      cols: definition.cols,
      axes
    },
    axes
  );
}

function withValidAxesTargets(spec: FigureSpec, axes: AxesSpec[]): FigureSpec {
  const validIds = new Set(axes.map((axis) => axis.id));
  const fallbackId = axes[0]?.id ?? "ax0";
  return {
    ...spec,
    axes,
    layers: spec.layers.map((layer) => ({
      ...layer,
      axes_id: validIds.has(layer.axes_id) ? layer.axes_id : fallbackId
    })),
    recipes: (spec.recipes ?? []).map((recipe) => ({
      ...recipe,
      axes_id: validIds.has(recipe.axes_id) ? recipe.axes_id : fallbackId
    })),
    reference_lines: (spec.reference_lines ?? []).map((referenceLine) => ({
      ...referenceLine,
      axes_id: validIds.has(referenceLine.axes_id) ? referenceLine.axes_id : fallbackId
    })),
    annotations: spec.annotations.map((annotation) => ({
      ...annotation,
      axes_id: validIds.has(annotation.axes_id) ? annotation.axes_id : fallbackId
    }))
  };
}

function inferLayoutPreset(spec: FigureSpec): LayoutPresetValue {
  const axes = spec.axes.map(axisGeometryKey).join("|");
  for (const preset of layoutPresetOrder) {
    const definition = layoutPresets[preset];
    if (spec.rows !== definition.rows || spec.cols !== definition.cols) {
      continue;
    }
    if (definition.axes.map(axisGeometryKey).join("|") === axes) {
      return preset;
    }
  }
  return "custom";
}

function axisGeometryKey(axis: AxesGeometry): string {
  return `${axis.id}:${axis.row}:${axis.col}:${axis.rowspan ?? 1}:${axis.colspan ?? 1}`;
}

function axisLabel(axis: AxesSpec, index: number): string {
  const span = axis.rowspan > 1 || axis.colspan > 1 ? `, ${axis.rowspan}x${axis.colspan}` : "";
  return `${axis.id} (${axis.row + 1}, ${axis.col + 1}${span}) ${index === 0 ? "primary" : ""}`.trim();
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
    variable: yVar.name,
    filters: []
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
    fill_alpha: kind === "fill_between" ? 0.3 : null,
    colorbar: kind === "heatmap" ? true : null
  };
  return {
    id: createId("layer"),
    kind,
    axes_id: "ax0",
    y_axis: "left",
    dataset,
    style,
    readonly: false,
    source: "generated"
  };
}

function createRecipe({
  kind,
  variable,
  xColumn,
  yColumn,
  groupColumn,
  subjectColumn,
  error
}: {
  kind: RecipeKind;
  variable: VariableSummary;
  xColumn: string;
  yColumn: string;
  groupColumn: string;
  subjectColumn: string;
  error: RecipeLayer["error"];
}): RecipeLayer {
  const label = yColumn || variable.name;
  return {
    id: createId("recipe"),
    kind,
    axes_id: "ax0",
    dataset: {
      variable: variable.name,
      x: xColumn || null,
      y: yColumn || null,
      group: kind === "mean_sem_line" && groupColumn ? groupColumn : null,
      subject: kind === "paired_before_after" ? subjectColumn || null : null,
      filters: []
    },
    style: {
      label,
      color: colors[0],
      marker: kind === "grouped_points" || kind === "paired_before_after" ? "o" : null,
      linestyle: kind === "mean_sem_line" ? "-" : null,
      linewidth: kind === "mean_sem_line" || kind === "paired_before_after" ? 1.8 : null,
      alpha: kind === "grouped_points" ? 0.78 : null
    },
    error,
    readonly: false,
    source: "recipe"
  };
}

function createFacetedLayers(baseLayer: PlotLayer, values: FacetValue[], facetColumn: string): PlotLayer[] {
  return values.map((value, index) => {
    const label = facetDisplayLabel(value);
    return {
      ...structuredClone(baseLayer),
      id: createId("layer"),
      axes_id: `ax${index}`,
      dataset: {
        ...baseLayer.dataset,
        filters: [...(baseLayer.dataset.filters ?? []), facetFilter(facetColumn, value)]
      },
      style: {
        ...baseLayer.style,
        label: baseLayer.style.label ? `${baseLayer.style.label} (${label})` : label
      }
    };
  });
}

function createFacetedRecipes(baseRecipe: RecipeLayer, values: FacetValue[], facetColumn: string): RecipeLayer[] {
  return values.map((value, index) => {
    const label = facetDisplayLabel(value);
    return {
      ...structuredClone(baseRecipe),
      id: createId("recipe"),
      axes_id: `ax${index}`,
      dataset: {
        ...baseRecipe.dataset,
        filters: [...(baseRecipe.dataset.filters ?? []), facetFilter(facetColumn, value)]
      },
      style: {
        ...baseRecipe.style,
        label: baseRecipe.style.label ? `${baseRecipe.style.label} (${label})` : label
      }
    };
  });
}

function createSelectedPanelLayers(baseLayer: PlotLayer, candidates: RepeatedPanelCandidate[]): PlotLayer[] {
  return candidates.map((candidate, index) => {
    const label = repeatedPanelLabel(candidate);
    return {
      ...structuredClone(baseLayer),
      id: createId("layer"),
      axes_id: `ax${index}`,
      dataset: {
        ...baseLayer.dataset,
        selection: candidate.selection ?? null,
        filters: baseLayer.dataset.filters ?? []
      },
      style: {
        ...baseLayer.style,
        label: baseLayer.style.label ? `${baseLayer.style.label} (${label})` : label
      }
    };
  });
}

function repeatedPanelSourceKind(variable?: VariableSummary): RepeatedPanelSourceKind | null {
  if (variable?.kind === "dataframe") {
    return "dataframe_column";
  }
  if (variable?.kind === "mapping") {
    return "mapping_keys";
  }
  if (variable?.kind === "sequence") {
    return "sequence_items";
  }
  return null;
}

function candidateIsLayerCompatible(candidate: RepeatedPanelCandidate, kind: PlotKind): boolean {
  const summary = candidate.summary;
  if (!summary) {
    return false;
  }
  if (kind === "heatmap" || kind === "contour") {
    return summary.kind === "dataframe" || summary.shape.length >= 2;
  }
  if (summary.kind === "ndarray" && summary.shape.length === 0) {
    return false;
  }
  return ["dataframe", "series", "ndarray", "sequence"].includes(summary.kind);
}

function panelSkipMessage(
  createdCount: number,
  skipped: RepeatedPanelSkippedCandidate[],
  incompatible: RepeatedPanelCandidate[]
): string {
  const skippedCount = skipped.length + incompatible.length;
  if (!skippedCount) {
    return `Created ${createdCount} repeated panel${createdCount === 1 ? "" : "s"}.`;
  }
  const firstReason = skipped[0]?.reason ?? "Candidate item is not compatible with the current layer settings.";
  return `Created ${createdCount} repeated panel${createdCount === 1 ? "" : "s"}; skipped ${skippedCount}: ${firstReason}`;
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

function cloneRecipe(recipe: RecipeLayer): RecipeLayer {
  return {
    ...structuredClone(recipe),
    id: createId("recipe"),
    style: {
      ...recipe.style,
      label: recipe.style.label ? `${recipe.style.label} copy` : undefined
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
      profile_id: null,
      profile_overrides: [],
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

function createReferenceLine(axesId: string, orientation: ReferenceLineOrientation): ReferenceLineSpec {
  return {
    id: createId("refline"),
    axes_id: axesId,
    orientation,
    value: 0,
    style: {
      label: orientation === "horizontal" ? "Baseline" : "Cutoff",
      color: "#6b7280",
      linestyle: "--",
      linewidth: 1.2,
      alpha: 0.85
    }
  };
}

function escapeAttributeValue(value: string): string {
  return value.replace(/\\/g, "\\\\").replace(/"/g, '\\"');
}

function hasFigureContent(spec: FigureSpec): boolean {
  return (
    spec.layers.length > 0 ||
    (spec.recipes?.length ?? 0) > 0 ||
    (spec.reference_lines?.length ?? 0) > 0
  );
}

function nextStepStatus(spec: FigureSpec): string {
  if (!hasFigureContent(spec)) {
    return "Select data, add a layer or recipe, then preview.";
  }
  return "Preview synced. Polish the figure, then save or export.";
}

function validationRepairText(issue: ValidationIssue): string {
  if (issue.suggestion) {
    return issue.suggestion;
  }
  switch (issue.code) {
    case "missing_variable":
      return "Choose an available source variable, or restart FigStudio from a scope that contains this name.";
    case "missing_column":
      return "Open the affected layer or recipe and choose a column that exists on the selected DataFrame.";
    case "unsupported_recipe_source":
      return "Stats recipes need a pandas DataFrame source. Switch the source or create a normal plot layer.";
    case "unsupported_filter_source":
      return "Filters need a pandas DataFrame source. Remove the filter or switch to a DataFrame-backed layer.";
    case "empty_filter_result":
      return "This filter currently matches no rows. Choose another facet value or check the live DataFrame.";
    case "missing_axes":
      return "Select a valid target axes for the layer, recipe, or annotation.";
    case "dimension_mismatch":
      return "Use X, Y, and error sources with matching lengths, or use index for X.";
    case "requires_2d_data":
      return "Use a 2D ndarray or gridded value column for heatmap and contour layers.";
    case "log_scale_non_positive":
      return "Remove non-positive data or switch the affected axis back to a linear scale.";
    case "invalid_reference_line_value":
      return "Use a finite reference value that is valid for the selected axes scale.";
    case "unsupported_secondary_y_layer":
      return "Use the right Y axis only for simple overlay layer kinds, or switch this layer back to the left Y axis.";
    case "invalid_grid_size":
      return "Set figure rows and columns to positive values in the Figure controls.";
    case "duplicate_axes_id":
    case "invalid_axes_span":
    case "axes_out_of_bounds":
    case "axes_overlap":
      return "Choose a built-in panel layout or reduce rows, columns, and spans until axes no longer overlap.";
    case "missing_style_profile":
      return "Pick an existing project profile or choose No project profile.";
    default:
      return issue.field
        ? "Click this issue to focus the affected field, then adjust the value."
        : "Click this issue to focus the affected editor context.";
  }
}

export function App() {
  const {
    session,
    variables,
    styleProfiles,
    spec,
    render,
    selectedVariable,
    selectedLayerId,
    status,
    setSession,
    setVariables,
    setStyleProfiles,
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
        const [sessionInfo, variableList, profiles, initialSpec] = await Promise.all([
          api.session(),
          api.variables(),
          api.styleProfiles(),
          api.spec()
        ]);
        if (cancelled) {
          return;
        }
        setSession(sessionInfo);
        setVariables(variableList);
        setStyleProfiles(profiles);
        setSpec(initialSpec);
        setStatus(nextStepStatus(initialSpec));
      } catch (error) {
        setStatus(error instanceof Error ? error.message : "Failed to load session");
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [setSession, setSpec, setStatus, setStyleProfiles, setVariables]);

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
          setStatus(`${count} validation error${count === 1 ? "" : "s"}: click a card to repair.`);
          return;
        }
        if (!hasFigureContent(spec)) {
          setRender(undefined);
          if (Date.now() >= manualStatusUntilRef.current) {
            setStatus(nextStepStatus(spec));
          }
          return;
        }
        const response = await api.render(spec, "svg");
        setRender(response);
        if (Date.now() >= manualStatusUntilRef.current) {
          setStatus(nextStepStatus(spec));
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
  const selectedRecipe = useMemo(
    () => spec?.recipes?.find((recipe) => recipe.id === selectedLayerId),
    [selectedLayerId, spec?.recipes]
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
    setManualStatus(`Repair ${issue.code}: ${validationRepairText(issue)}`);
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
  }, [selectedAxisId, selectedLayerId, spec?.axes, spec?.layers, spec?.recipes, spec?.reference_lines]);

  async function renderNow() {
    if (!spec) {
      return;
    }
    setStatus("Rendering");
    try {
      const validation = await api.validate(spec);
      setValidationIssues(validation.issues);
      if (!validation.ok) {
        setStatus("Fix validation errors: click a card to repair.");
        return;
      }
      if (!hasFigureContent(spec)) {
        setRender(undefined);
        setStatus(nextStepStatus(spec));
        return;
      }
      const response = await api.render(spec, "svg");
      setRender(response);
      setStatus(nextStepStatus(spec));
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
      const saveHelp = response.wrote_file
        ? "Script marker block updated."
        : `${response.message} Copy the replacement cell code from this panel.`;
      setSaveMessage(response.ok ? saveHelp : `${response.message} Generated code remains available below.`);
      if (!response.ok) {
        setStatus("Save blocked: copy generated code from the panel.");
      } else {
        setStatus(response.wrote_file ? "Script updated." : "Notebook replacement code ready.");
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
        setStatus("Export blocked: click a validation card to repair.");
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
      const axes = raw.axes?.map((axis, index) => normalizeAxis(axis as AxesSpec, index)) ?? [
        createAxis(0, 0, 0)
      ];
      const layers = (raw.layers ?? []).map((layer) => normalizeLayer(layer));
      const recipes = (raw.recipes ?? []).map((recipe) => ({
        ...recipe,
        dataset: normalizeRecipeDatasetRef(recipe.dataset)
      }));
      const imported = {
        ...raw,
        share_x: raw.share_x ?? false,
        share_y: raw.share_y ?? false,
        axes,
        layers,
        recipes,
        reference_lines: raw.reference_lines ?? [],
        annotations: raw.annotations ?? [],
        style: {
          preset: "custom",
          profile_id: null,
          profile_overrides: [],
          title: "",
          font_size: 10,
          constrained_layout: true,
          ...(raw.style ?? {})
        }
      } as FigureSpec;
      setSpec(imported);
      setSelectedLayerId(imported.layers[0]?.id ?? imported.recipes[0]?.id ?? "");
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

  function deleteRecipe(id: string) {
    updateSpec((draft) => ({
      ...draft,
      recipes: (draft.recipes ?? []).filter((recipe) => recipe.id !== id)
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

  function duplicateRecipe(recipe: RecipeLayer) {
    const next = cloneRecipe(recipe);
    updateSpec((draft) => ({
      ...draft,
      recipes: [...(draft.recipes ?? []), next]
    }));
    setSelectedLayerId(next.id);
  }

  function applyFacetBuild(payload: FacetBuildPayload) {
    updateSpec((draft) => {
      const adjusted = withValidAxesTargets(
        {
          ...draft,
          rows: payload.rows,
          cols: payload.cols,
          share_x: payload.shareX,
          share_y: payload.shareY
        },
        payload.axes
      );
      return {
        ...adjusted,
        layers: [...adjusted.layers, ...(payload.layers ?? [])],
        recipes: [...(adjusted.recipes ?? []), ...(payload.recipes ?? [])]
      };
    });
    const firstItem = payload.layers?.[0]?.id ?? payload.recipes?.[0]?.id ?? "";
    setSelectedLayerId(firstItem);
    setSelectedAxisId(payload.axes[0]?.id ?? "ax0");
    setManualStatus(payload.message ?? `Created ${payload.axes.length} faceted panel${payload.axes.length === 1 ? "" : "s"}.`);
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

      <nav className="panel-jump-nav" aria-label="Editor panels">
        <a href="#variables-panel">Explore</a>
        <a href="#preview-panel">Preview</a>
        <a href="#polish-panel">Polish</a>
      </nav>

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
          onAddRecipe={(recipe) => {
            updateSpec((draft) => ({
              ...draft,
              recipes: [...(draft.recipes ?? []), recipe]
            }));
            setSelectedLayerId(recipe.id);
          }}
          onApplyFacetBuild={applyFacetBuild}
          onStatus={setManualStatus}
        />

        <section className="canvas-column" id="preview-panel">
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
          styleProfiles={styleProfiles}
          selectedLayer={selectedLayer}
          selectedRecipe={selectedRecipe}
          selectedAxisId={selectedAxisId}
          layerFocusRequest={layerFocusRequest}
          onSelectLayer={setSelectedLayerId}
          onSelectAxis={setSelectedAxisId}
          onUpdateSpec={updateSpec}
          onDeleteLayer={deleteLayer}
          onDuplicateLayer={duplicateLayer}
          onDeleteRecipe={deleteRecipe}
          onDuplicateRecipe={duplicateRecipe}
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
  onAddRecipe: (recipe: RecipeLayer) => void;
  onApplyFacetBuild: (payload: FacetBuildPayload) => void;
  onStatus: (message: string) => void;
}

function VariablePanel({
  variables,
  selected,
  onSelect,
  onAddLayer,
  onAddRecipe,
  onApplyFacetBuild,
  onStatus
}: VariablePanelProps) {
  const variable = variables.find((item) => item.name === selected) ?? variables[0];
  const dataframeVariables = variables.filter((item) => item.kind === "dataframe");
  const [builderMode, setBuilderMode] = useState<"layer" | "recipe">("layer");
  const [kind, setKind] = useState<PlotKind>("line");
  const [xVariable, setXVariable] = useState(indexSource);
  const [xColumn, setXColumn] = useState("");
  const [yVariable, setYVariable] = useState("");
  const [yColumn, setYColumn] = useState("");
  const [yerrVariable, setYerrVariable] = useState(noneSource);
  const [yerrColumn, setYerrColumn] = useState("");
  const [recipeKind, setRecipeKind] = useState<RecipeKind>("mean_sem_line");
  const [recipeVariableName, setRecipeVariableName] = useState("");
  const [recipeXColumn, setRecipeXColumn] = useState("");
  const [recipeYColumn, setRecipeYColumn] = useState("");
  const [recipeGroupColumn, setRecipeGroupColumn] = useState("");
  const [recipeSubjectColumn, setRecipeSubjectColumn] = useState("");
  const [recipeError, setRecipeError] = useState<RecipeLayer["error"]>("sem");
  const [facetColumn, setFacetColumn] = useState("");
  const [facetLimit, setFacetLimit] = useState(defaultFacetLimit);
  const [facetShareX, setFacetShareX] = useState(true);
  const [facetShareY, setFacetShareY] = useState(false);
  const [facetBusy, setFacetBusy] = useState(false);

  const xVar = findVariable(variables, xVariable);
  const yVar = findVariable(variables, yVariable) ?? variable;
  const yerrVar = findVariable(variables, yerrVariable);
  const recipeVariable =
    dataframeVariables.find((item) => item.name === recipeVariableName) ??
    (variable?.kind === "dataframe" ? variable : dataframeVariables[0]);
  const compatibility = compatibilityText(kind, yVar, xVar);
  const facetSource = builderMode === "layer" ? yVar : recipeVariable;
  const facetSourceKind = repeatedPanelSourceKind(facetSource);
  const isSelectedPanelSource = builderMode === "layer" && (facetSourceKind === "mapping_keys" || facetSourceKind === "sequence_items");
  const layerCanFacet =
    builderMode === "layer" &&
    yVar?.kind === "dataframe" &&
    (xVariable === indexSource || xVariable === yVar.name) &&
    (kind !== "errorbar" || yerrVariable === noneSource || yerrVariable === yVar.name);
  const layerCanSelectPanels =
    Boolean(isSelectedPanelSource && yVar) &&
    xVariable !== yVar?.name &&
    (kind !== "errorbar" || yerrVariable === noneSource || yerrVariable !== yVar?.name);
  const recipeCanFacet = builderMode === "recipe" && Boolean(recipeVariable);
  const canFacet = Boolean(
    facetSourceKind === "dataframe_column" ? layerCanFacet || recipeCanFacet : layerCanSelectPanels
  );

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

  useEffect(() => {
    if (!recipeVariable) {
      return;
    }
    const subjectColumn =
      recipeVariable.columns.find((column) => /subject|animal|mouse|participant|id/i.test(column)) ??
      firstColumn(recipeVariable);
    setRecipeVariableName(recipeVariable.name);
    setRecipeXColumn(firstColumn(recipeVariable));
    setRecipeYColumn(secondColumn(recipeVariable));
    setRecipeGroupColumn("");
    setRecipeSubjectColumn(subjectColumn);
  }, [recipeVariable?.name, recipeKind]);

  useEffect(() => {
    setFacetColumn(facetSource?.kind === "dataframe" ? defaultFacetColumn(facetSource) : "");
  }, [facetSource?.name, facetSource?.kind, builderMode]);

  async function applyFacets() {
    if (!facetSource || !facetSourceKind || !canFacet) {
      return;
    }
    if (facetSourceKind === "dataframe_column" && !facetColumn) {
      return;
    }
    setFacetBusy(true);
    onStatus("Reading repeated-panel candidates");
    try {
      const response = await api.repeatedPanelCandidates({
        variable: facetSource.name,
        source_kind: facetSourceKind,
        column: facetSourceKind === "dataframe_column" ? facetColumn : null,
        max_values: facetLimit
      });
      if (!response.candidates.length) {
        onStatus(`No repeated-panel candidates found for ${facetSource.name}.`);
        return;
      }
      if (response.source_kind === "dataframe_column") {
        const values = response.candidates.map((candidate) => ({
          value: candidate.value,
          label: candidate.label
        }));
        const { rows, cols } = facetLayout(values.length);
        const axes = createFacetAxes(values, facetColumn, cols);
        if (builderMode === "layer") {
          const baseLayer = createLayer(
            kind,
            variables,
            yVar?.name ?? facetSource.name,
            yColumn,
            xVariable,
            xColumn,
            yerrVariable,
            yerrColumn
          );
          onApplyFacetBuild({
            axes,
            rows,
            cols,
            shareX: facetShareX,
            shareY: facetShareY,
            layers: createFacetedLayers(baseLayer, values, facetColumn)
          });
        } else if (recipeVariable) {
          const baseRecipe = createRecipe({
            kind: recipeKind,
            variable: recipeVariable,
            xColumn: recipeXColumn,
            yColumn: recipeYColumn,
            groupColumn: recipeGroupColumn,
            subjectColumn: recipeSubjectColumn,
            error: recipeError
          });
          onApplyFacetBuild({
            axes,
            rows,
            cols,
            shareX: facetShareX,
            shareY: facetShareY,
            recipes: createFacetedRecipes(baseRecipe, values, facetColumn)
          });
        }
      } else if (builderMode === "layer") {
        const compatible = response.candidates.filter((candidate) => candidateIsLayerCompatible(candidate, kind));
        const incompatible = response.candidates.filter((candidate) => !candidateIsLayerCompatible(candidate, kind));
        if (!compatible.length) {
          onStatus("No compatible mapping/sequence items for the current layer settings.");
          return;
        }
        const { rows, cols } = facetLayout(compatible.length);
        const titlePrefix = response.source_kind === "mapping_keys" ? "mapping key" : "sequence item";
        const axes = createRepeatedPanelAxes(compatible, titlePrefix, cols);
        const baseLayer = createLayer(
          kind,
          variables,
          yVar?.name ?? facetSource.name,
          yColumn,
          xVariable,
          xColumn,
          yerrVariable,
          yerrColumn
        );
        onApplyFacetBuild({
          axes,
          rows,
          cols,
          shareX: facetShareX,
          shareY: facetShareY,
          layers: createSelectedPanelLayers(baseLayer, compatible),
          message: panelSkipMessage(compatible.length, response.skipped, incompatible)
        });
      }
      if (response.truncated) {
        onStatus(`Created first ${response.candidates.length} panels; more candidates were available.`);
      }
    } catch (error) {
      onStatus(error instanceof Error ? error.message : "Repeated-panel build failed");
    } finally {
      setFacetBusy(false);
    }
  }

  return (
    <aside className="side-panel variables-panel" id="variables-panel" data-testid="variable-panel">
      <PanelTitle icon={<Braces size={16} />} title="Explore" />
      <p className="panel-help">Choose source data, then create the first plot layer or statistics recipe.</p>
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
        <h2>{builderMode === "layer" ? "Create plot layer" : "Create statistics recipe"}</h2>
        <label>
          Build from selected data
          <select
            data-testid="builder-mode-select"
            value={builderMode}
            onChange={(event) => setBuilderMode(event.target.value as "layer" | "recipe")}
          >
            <option value="layer">Plot layer</option>
            <option value="recipe">Stats recipe</option>
          </select>
        </label>

        {builderMode === "layer" ? (
          <>
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
          </>
        ) : (
          <>
            <label>
              Recipe
              <select
                data-testid="recipe-kind-select"
                value={recipeKind}
                onChange={(event) => setRecipeKind(event.target.value as RecipeKind)}
              >
                {recipeKinds.map((item) => (
                  <option key={item} value={item}>
                    {recipeLabels[item]}
                  </option>
                ))}
              </select>
            </label>
            <label>
              DataFrame
              <select
                data-testid="recipe-source-select"
                value={recipeVariable?.name ?? ""}
                onChange={(event) => setRecipeVariableName(event.target.value)}
              >
                {dataframeVariables.map((item) => (
                  <option key={item.name} value={item.name}>
                    {item.name}
                  </option>
                ))}
              </select>
            </label>
            <div className="source-grid">
              <label>
                X / condition
                <select
                  data-testid="recipe-x-column-select"
                  value={recipeXColumn}
                  onChange={(event) => setRecipeXColumn(event.target.value)}
                >
                  {recipeVariable?.columns.map((column) => (
                    <option key={column} value={column}>
                      {column}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Y / value
                <select
                  data-testid="recipe-y-column-select"
                  value={recipeYColumn}
                  onChange={(event) => setRecipeYColumn(event.target.value)}
                >
                  {recipeVariable?.columns.map((column) => (
                    <option key={column} value={column}>
                      {column}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            {recipeKind === "mean_sem_line" ? (
              <label>
                Group column
                <select
                  data-testid="recipe-group-column-select"
                  value={recipeGroupColumn}
                  onChange={(event) => setRecipeGroupColumn(event.target.value)}
                >
                  <option value="">none</option>
                  {recipeVariable?.columns.map((column) => (
                    <option key={column} value={column}>
                      {column}
                    </option>
                  ))}
                </select>
              </label>
            ) : null}
            {recipeKind === "paired_before_after" ? (
              <label>
                Subject column
                <select
                  data-testid="recipe-subject-column-select"
                  value={recipeSubjectColumn}
                  onChange={(event) => setRecipeSubjectColumn(event.target.value)}
                >
                  {recipeVariable?.columns.map((column) => (
                    <option key={column} value={column}>
                      {column}
                    </option>
                  ))}
                </select>
              </label>
            ) : null}
            <label>
              Error
              <select
                data-testid="recipe-error-select"
                value={recipeError}
                onChange={(event) => setRecipeError(event.target.value as RecipeLayer["error"])}
              >
                {errorModes.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </label>
            {!dataframeVariables.length ? (
              <p className="compatibility-note">Stats recipes require a pandas DataFrame variable.</p>
            ) : null}
            <button
              className="primary-button"
              data-testid="add-recipe-button"
              disabled={!recipeVariable || !recipeXColumn || !recipeYColumn}
              onClick={() =>
                recipeVariable &&
                onAddRecipe(
                  createRecipe({
                    kind: recipeKind,
                    variable: recipeVariable,
                    xColumn: recipeXColumn,
                    yColumn: recipeYColumn,
                    groupColumn: recipeGroupColumn,
                    subjectColumn: recipeSubjectColumn,
                    error: recipeError
                  })
                )
              }
            >
              <Layers3 size={16} />
              Add recipe
            </button>
          </>
        )}

        {facetSourceKind ? (
          <div className="facet-builder">
            <h2>{facetSourceKind === "dataframe_column" ? "Facet panels" : "Repeated panels"}</h2>
            {facetSourceKind === "dataframe_column" ? (
              <label>
                Facet by DataFrame column
                <select
                  data-testid="facet-column-select"
                  value={facetColumn}
                  onChange={(event) => setFacetColumn(event.target.value)}
                >
                  {facetSource?.columns.map((column) => (
                    <option key={column} value={column}>
                      {column}
                    </option>
                  ))}
                </select>
              </label>
            ) : (
              <p className="compatibility-note" data-testid="repeated-panel-kind-note">
                Repeat by {facetSourceKind === "mapping_keys" ? "mapping keys" : "sequence items"}.
              </p>
            )}
            <div className="split-row">
              <NumberField
                label="Max panels"
                value={facetLimit}
                step={1}
                min={1}
                max={12}
                testId="facet-limit-field"
                field="facet.max_values"
                onChange={(value) => setFacetLimit(Math.max(1, Math.min(12, Math.round(value || 1))))}
              />
              <ToggleField
                label="Share X"
                value={facetShareX}
                testId="facet-share-x-field"
                field="share_x"
                onChange={setFacetShareX}
              />
            </div>
            <ToggleField
              label="Share Y"
              value={facetShareY}
              testId="facet-share-y-field"
              field="share_y"
              onChange={setFacetShareY}
            />
            {!canFacet ? (
              <p className="compatibility-note">
                {facetSourceKind === "dataframe_column"
                  ? "Facets require the main DataFrame with index or same-DataFrame X/error sources."
                  : "Mapping and sequence panels require index X or an independent X/error source."}
              </p>
            ) : null}
            <button
              className="primary-button"
              data-testid="create-facet-panels-button"
              disabled={!canFacet || (facetSourceKind === "dataframe_column" && !facetColumn) || facetBusy}
              onClick={applyFacets}
            >
              <Layers3 size={16} />
              {facetSourceKind === "dataframe_column" ? "Create facet panels" : "Create panels"}
            </button>
          </div>
        ) : null}
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

function supportsSecondaryYAxis(kind: PlotKind): boolean {
  return secondaryYAxisLayerKinds.has(kind);
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
          <div>
            <strong>Add data to the canvas</strong>
            <span>Select a variable, add a plot layer or stats recipe, then polish it on the right.</span>
          </div>
          <ol data-testid="empty-preview-steps">
            <li>Choose a variable in Explore.</li>
            <li>Map X and Y, then add a layer.</li>
            <li>Use Polish for labels, layout, and styles.</li>
          </ol>
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
          <span>
            {issue.message}
            <small>Suggested fix: {validationRepairText(issue)}</small>
          </span>
        </button>
      ))}
    </div>
  );
}

function ReferenceLineControls({
  referenceLines,
  selectedAxisId,
  onUpdateSpec
}: {
  referenceLines: ReferenceLineSpec[];
  selectedAxisId: string;
  onUpdateSpec: (updater: (spec: FigureSpec) => FigureSpec) => void;
}) {
  function addReferenceLine(orientation: ReferenceLineOrientation) {
    const referenceLine = createReferenceLine(selectedAxisId, orientation);
    onUpdateSpec((draft) => ({
      ...draft,
      reference_lines: [...(draft.reference_lines ?? []), referenceLine]
    }));
  }

  function updateReferenceLine(id: string, patch: Partial<ReferenceLineSpec>) {
    onUpdateSpec((draft) => ({
      ...draft,
      reference_lines: (draft.reference_lines ?? []).map((referenceLine) =>
        referenceLine.id === id ? { ...referenceLine, ...patch } : referenceLine
      )
    }));
  }

  function deleteReferenceLine(id: string) {
    onUpdateSpec((draft) => ({
      ...draft,
      reference_lines: (draft.reference_lines ?? []).filter((referenceLine) => referenceLine.id !== id)
    }));
  }

  return (
    <section className="control-group" data-testid="reference-line-controls">
      <h2>Reference lines</h2>
      <div className="layer-actions">
        <button
          className="mini-button"
          data-testid="add-horizontal-reference-line-button"
          onClick={() => addReferenceLine("horizontal")}
        >
          Horizontal
        </button>
        <button
          className="mini-button"
          data-testid="add-vertical-reference-line-button"
          onClick={() => addReferenceLine("vertical")}
        >
          Vertical
        </button>
      </div>
      {referenceLines.length ? (
        <div className="annotation-list" data-testid="reference-line-list">
          {referenceLines.map((referenceLine) => {
            const style = referenceLine.style ?? {};
            return (
              <div key={referenceLine.id} className="annotation-card" data-testid="reference-line-card">
                <div className="split-row">
                  <SelectField
                    label="Direction"
                    value={referenceLine.orientation}
                    options={referenceLineOrientations}
                    testId="reference-line-orientation-field"
                    field="reference_lines.orientation"
                    onChange={(value) =>
                      updateReferenceLine(referenceLine.id, {
                        orientation: value as ReferenceLineOrientation
                      })
                    }
                  />
                  <NumberField
                    label="Value"
                    value={referenceLine.value}
                    testId="reference-line-value-field"
                    field="reference_lines.value"
                    onChange={(value) => updateReferenceLine(referenceLine.id, { value })}
                  />
                </div>
                <TextField
                  label="Legend label"
                  value={style.label ?? ""}
                  testId="reference-line-label-field"
                  field="reference_lines.style.label"
                  onChange={(value) =>
                    updateReferenceLine(referenceLine.id, {
                      style: { ...style, label: value || null }
                    })
                  }
                />
                <label data-testid="reference-line-color-field" data-field="reference_lines.style.color">
                  Color
                  <div className="swatches">
                    {colors.map((swatch) => (
                      <button
                        key={swatch}
                        className={swatch === style.color ? "selected" : ""}
                        style={{ background: swatch }}
                        aria-label={swatch}
                        data-testid="reference-line-color-swatch"
                        onClick={() =>
                          updateReferenceLine(referenceLine.id, {
                            style: { ...style, color: swatch }
                          })
                        }
                      />
                    ))}
                  </div>
                </label>
                <div className="split-row">
                  <SelectField
                    label="Line style"
                    value={style.linestyle ?? "--"}
                    options={linestyles}
                    testId="reference-line-linestyle-field"
                    field="reference_lines.style.linestyle"
                    onChange={(value) =>
                      updateReferenceLine(referenceLine.id, {
                        style: { ...style, linestyle: value || null }
                      })
                    }
                  />
                  <NumberField
                    label="Line width"
                    value={Number(style.linewidth ?? 1.2)}
                    step={0.1}
                    min={0}
                    testId="reference-line-linewidth-field"
                    field="reference_lines.style.linewidth"
                    onChange={(value) =>
                      updateReferenceLine(referenceLine.id, {
                        style: { ...style, linewidth: value }
                      })
                    }
                  />
                </div>
                <NumberField
                  label="Alpha"
                  value={Number(style.alpha ?? 0.85)}
                  step={0.05}
                  min={0}
                  max={1}
                  testId="reference-line-alpha-field"
                  field="reference_lines.style.alpha"
                  onChange={(value) =>
                    updateReferenceLine(referenceLine.id, {
                      style: { ...style, alpha: value }
                    })
                  }
                />
                <button
                  className="mini-button danger-button"
                  data-testid="delete-reference-line-button"
                  onClick={() => deleteReferenceLine(referenceLine.id)}
                >
                  <Trash2 size={14} />
                  Delete
                </button>
              </div>
            );
          })}
        </div>
      ) : (
        <p className="muted">No reference lines on this axes.</p>
      )}
    </section>
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
  styleProfiles,
  selectedLayer,
  selectedRecipe,
  selectedAxisId,
  layerFocusRequest,
  onSelectLayer,
  onSelectAxis,
  onUpdateSpec,
  onDeleteLayer,
  onDuplicateLayer,
  onDeleteRecipe,
  onDuplicateRecipe
}: {
  spec?: FigureSpec;
  styleProfiles: StyleProfilesResponse;
  selectedLayer?: PlotLayer;
  selectedRecipe?: RecipeLayer;
  selectedAxisId: string;
  layerFocusRequest: { layerId: string; nonce: number } | null;
  onSelectLayer: (id: string) => void;
  onSelectAxis: (id: string) => void;
  onUpdateSpec: (updater: (spec: FigureSpec) => FigureSpec) => void;
  onDeleteLayer: (id: string) => void;
  onDuplicateLayer: (layer: PlotLayer) => void;
  onDeleteRecipe: (id: string) => void;
  onDuplicateRecipe: (recipe: RecipeLayer) => void;
}) {
  const selectedAxis = spec?.axes.find((axis) => axis.id === selectedAxisId) ?? spec?.axes[0];
  const recipes = spec?.recipes ?? [];
  const layoutPreset = spec ? inferLayoutPreset(spec) : "custom";
  const activeProfile = spec ? profileById(styleProfiles, spec.style.profile_id) : undefined;
  const profileOverrides = spec?.style.profile_overrides ?? [];
  const profileOverrideSummary = spec?.style.profile_id
    ? profileOverrides.length
      ? `Overrides: ${profileOverrides.join(", ")}`
      : "Using project profile defaults"
    : "";

  return (
    <aside className="side-panel inspector-panel" id="polish-panel" data-testid="inspector-panel">
      <PanelTitle icon={<Settings2 size={16} />} title="Polish" />
      <p className="panel-help">Tune figure setup, axes, annotations, layers, and recipes without leaving the preview.</p>
      {!spec || !selectedAxis ? (
        <p className="muted">Waiting for session</p>
      ) : (
        <>
          <section className="control-group">
            <h2>Figure setup</h2>
            <SelectField
              label="Style preset"
              value={spec.style.preset ?? "custom"}
              options={Object.keys(stylePresets)}
              testId="style-preset-field"
              field="style.preset"
              optionLabel={(value) => stylePresets[value as FigurePreset].label}
              onChange={(value) => onUpdateSpec((draft) => applyPreset(draft, value as FigurePreset))}
            />
            <SelectField
              label="Project profile"
              value={spec.style.profile_id ?? ""}
              options={["", ...styleProfiles.profiles.map((profile) => profile.id)]}
              testId="style-profile-field"
              field="style.profile_id"
              optionLabel={(value) =>
                value ? (profileById(styleProfiles, value)?.label ?? value) : "No project profile"
              }
              onChange={(value) => onUpdateSpec((draft) => applyStyleProfile(draft, value))}
            />
            {profileOverrideSummary ? (
              <p className="profile-note" data-testid="style-profile-note">
                {activeProfile?.label ?? spec.style.profile_id}: {profileOverrideSummary}
              </p>
            ) : null}
            {styleProfiles.warnings.length ? (
              <p className="compatibility-note" data-testid="style-profile-warning">
                {styleProfiles.warnings.join(" ")}
              </p>
            ) : null}
            <SelectField
              label="Panel layout"
              value={layoutPreset}
              options={["custom", ...layoutPresetOrder]}
              testId="layout-preset-field"
              field="axes.layout"
              optionLabel={(value) =>
                value === "custom" ? "Custom layout" : layoutPresets[value as LayoutPreset].label
              }
              onChange={(value) => {
                if (value !== "custom") {
                  onUpdateSpec((draft) => applyLayoutPreset(draft, value as LayoutPreset));
                }
              }}
            />
            <div className="split-row">
              <NumberField
                label="Width"
                value={Number(effectiveFigureValue(spec, styleProfiles, "width"))}
                testId="figure-width-field"
                field="width"
                onChange={(value) => onUpdateSpec((draft) => updateFigureField(draft, "width", value))}
              />
              <NumberField
                label="Height"
                value={Number(effectiveFigureValue(spec, styleProfiles, "height"))}
                testId="figure-height-field"
                field="height"
                onChange={(value) => onUpdateSpec((draft) => updateFigureField(draft, "height", value))}
              />
            </div>
            <div className="split-row">
              <NumberField
                label="DPI"
                value={Number(effectiveFigureValue(spec, styleProfiles, "dpi"))}
                step={1}
                min={24}
                testId="figure-dpi-field"
                field="dpi"
                onChange={(value) => onUpdateSpec((draft) => updateFigureField(draft, "dpi", value))}
              />
              <NumberField
                label="Font size"
                value={Number(effectiveFigureValue(spec, styleProfiles, "font_size"))}
                testId="font-size-field"
                field="style.font_size"
                onChange={(value) => onUpdateSpec((draft) => updateFigureField(draft, "font_size", value))}
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
            <div className="split-row">
              <ToggleField
                label="Share X"
                value={spec.share_x}
                testId="share-x-field"
                field="share_x"
                onChange={(value) => onUpdateSpec((draft) => ({ ...draft, share_x: value }))}
              />
              <ToggleField
                label="Share Y"
                value={spec.share_y}
                testId="share-y-field"
                field="share_y"
                onChange={(value) => onUpdateSpec((draft) => ({ ...draft, share_y: value }))}
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
                  value={String(effectiveFigureValue(spec, styleProfiles, "font_family") ?? "")}
                  testId="font-family-field"
                  field="style.font_family"
                  onChange={(value) =>
                    onUpdateSpec((draft) => updateFigureField(draft, "font_family", value || null))
                  }
                />
                <ToggleField
                  label="Constrained layout"
                  value={Boolean(effectiveFigureValue(spec, styleProfiles, "constrained_layout"))}
                  testId="constrained-layout-field"
                  field="style.constrained_layout"
                  onChange={(value) =>
                    onUpdateSpec((draft) => updateFigureField(draft, "constrained_layout", value))
                  }
                />
              </>
            ) : null}
          </section>

          <section className="control-group">
            <h2>Axes labels and scale</h2>
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
                    {axisLabel(axis, index)}
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
            <TextField
              label="Right Y label"
              value={selectedAxis.secondary_y?.ylabel ?? ""}
              testId="axis-secondary-ylabel-field"
              field="axes.secondary_y.ylabel"
              onChange={(value) => updateSecondaryAxis(onUpdateSpec, selectedAxis.id, { ylabel: value })}
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
            <SelectField
              label="Right Y scale"
              value={selectedAxis.secondary_y?.yscale ?? "linear"}
              options={scales}
              testId="axis-secondary-yscale-field"
              field="axes.secondary_y.yscale"
              onChange={(value) =>
                updateSecondaryAxis(onUpdateSpec, selectedAxis.id, {
                  yscale: value as SecondaryYAxisSpec["yscale"]
                })
              }
            />
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
            <LimitField
              label="Right Y limits"
              value={selectedAxis.secondary_y?.ylim ?? null}
              testId="axis-secondary-ylim-field"
              field="axes.secondary_y.ylim"
              onChange={(value) => updateSecondaryAxis(onUpdateSpec, selectedAxis.id, { ylim: value })}
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

          <ReferenceLineControls
            referenceLines={(spec.reference_lines ?? []).filter(
              (referenceLine) => referenceLine.axes_id === selectedAxis.id
            )}
            selectedAxisId={selectedAxis.id}
            onUpdateSpec={onUpdateSpec}
          />

          <AnnotationControls
            annotations={spec.annotations.filter((annotation) => annotation.axes_id === selectedAxis.id)}
            selectedAxisId={selectedAxis.id}
            onUpdateSpec={onUpdateSpec}
          />

          <section className="control-group">
            <h2>Layers and recipes</h2>
            <div className="layer-list">
              {spec.layers.map((layer) => {
                const defaults = profileLayerDefaults(spec, styleProfiles, layer);
                const label = inheritedStyleValue(layer.style, defaults, "label") || layer.dataset.variable;
                return (
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
                    <span>{label}</span>
                    <small>
                      {layer.kind} · {layer.axes_id}
                      {layer.y_axis === "right" ? " · right Y" : ""}
                    </small>
                  </button>
                );
              })}
              {recipes.map((recipe) => {
                const defaults = profileRecipeDefaults(spec, styleProfiles, recipe);
                const label =
                  inheritedStyleValue(recipe.style, defaults, "label") || recipe.dataset.y || recipe.dataset.variable;
                return (
                  <button
                    key={recipe.id}
                    className={recipe.id === selectedRecipe?.id ? "selected" : ""}
                    data-testid="layer-row"
                    data-layer-id={recipe.id}
                    data-axes-id={recipe.axes_id}
                    ref={(node) => {
                      if (node && layerFocusRequest?.layerId === recipe.id) {
                        window.setTimeout(() => node.focus({ preventScroll: true }), 0);
                      }
                    }}
                    onClick={() => onSelectLayer(recipe.id)}
                  >
                    <span>{label}</span>
                    <small>
                      recipe · {recipe.kind} · {recipe.axes_id}
                    </small>
                  </button>
                );
              })}
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
                  defaults={profileLayerDefaults(spec, styleProfiles, selectedLayer)}
                  axes={spec.axes}
                  onChange={(next) =>
                    onUpdateSpec((draft) => ({
                      ...draft,
                      layers: draft.layers.map((layer) => (layer.id === next.id ? next : layer))
                    }))
                  }
                />
              </>
            ) : selectedRecipe ? (
              <>
                <div className="layer-actions">
                  <button
                    className="mini-button"
                    data-testid="duplicate-layer-button"
                    onClick={() => onDuplicateRecipe(selectedRecipe)}
                  >
                    <Copy size={14} />
                    Duplicate
                  </button>
                  <button
                    className="mini-button danger-button"
                    data-testid="delete-layer-button"
                    onClick={() => onDeleteRecipe(selectedRecipe.id)}
                  >
                    <Trash2 size={14} />
                    Delete
                  </button>
                </div>
                <RecipeControls
                  recipe={selectedRecipe}
                  defaults={profileRecipeDefaults(spec, styleProfiles, selectedRecipe)}
                  axes={spec.axes}
                  onChange={(next) =>
                    onUpdateSpec((draft) => ({
                      ...draft,
                      recipes: (draft.recipes ?? []).map((recipe) =>
                        recipe.id === next.id ? next : recipe
                      )
                    }))
                  }
                />
              </>
            ) : (
              <p className="muted">Add or select a layer or recipe to edit its target axes and style.</p>
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

function updateSecondaryAxis(
  onUpdateSpec: (updater: (spec: FigureSpec) => FigureSpec) => void,
  axisId: string,
  patch: Partial<SecondaryYAxisSpec>
) {
  onUpdateSpec((draft) => ({
    ...draft,
    axes: draft.axes.map((axis) =>
      axis.id === axisId
        ? { ...axis, secondary_y: { ...createSecondaryYAxis(axis.secondary_y), ...patch } }
        : axis
    )
  }));
}

function RecipeControls({
  recipe,
  defaults,
  axes,
  onChange
}: {
  recipe: RecipeLayer;
  defaults?: LayerStyle;
  axes: AxesSpec[];
  onChange: (recipe: RecipeLayer) => void;
}) {
  const label = inheritedStyleValue(recipe.style, defaults, "label") ?? "";
  const effectiveColor = inheritedStyleValue(recipe.style, defaults, "color") ?? "";
  const marker = inheritedStyleValue(recipe.style, defaults, "marker") ?? "";
  const linestyle = inheritedStyleValue(recipe.style, defaults, "linestyle") ?? "";
  const linewidth = inheritedStyleValue(recipe.style, defaults, "linewidth") ?? 1.8;
  const alpha = inheritedStyleValue(recipe.style, defaults, "alpha") ?? 1;
  return (
    <div className="layer-controls">
      {defaults ? <p className="profile-note">Layer defaults inherited from project profile.</p> : null}
      <SelectField
        label="Axes"
        value={recipe.axes_id}
        options={axes.map((axis) => axis.id)}
        testId="recipe-axes-field"
        field="axes_id"
        onChange={(value) => onChange({ ...recipe, axes_id: value })}
      />
      <SelectField
        label="Recipe"
        value={recipe.kind}
        options={recipeKinds}
        optionLabel={(value) => recipeLabels[value as RecipeKind]}
        testId="recipe-kind-field"
        field="kind"
        onChange={(value) => onChange({ ...recipe, kind: value as RecipeKind })}
      />
      <TextField
        label="DataFrame"
        value={recipe.dataset.variable}
        testId="recipe-variable-field"
        field="dataset.variable"
        onChange={(value) => onChange({ ...recipe, dataset: { ...recipe.dataset, variable: value } })}
      />
      <div className="split-row">
        <TextField
          label="X column"
          value={recipe.dataset.x ?? ""}
          testId="recipe-x-field"
          field="dataset.x"
          onChange={(value) => onChange({ ...recipe, dataset: { ...recipe.dataset, x: value || null } })}
        />
        <TextField
          label="Y column"
          value={recipe.dataset.y ?? ""}
          testId="recipe-y-field"
          field="dataset.y"
          onChange={(value) => onChange({ ...recipe, dataset: { ...recipe.dataset, y: value || null } })}
        />
      </div>
      {recipe.kind === "mean_sem_line" ? (
        <TextField
          label="Group column"
          value={recipe.dataset.group ?? ""}
          testId="recipe-group-field"
          field="dataset.group"
          onChange={(value) => onChange({ ...recipe, dataset: { ...recipe.dataset, group: value || null } })}
        />
      ) : null}
      {recipe.kind === "paired_before_after" ? (
        <TextField
          label="Subject column"
          value={recipe.dataset.subject ?? ""}
          testId="recipe-subject-field"
          field="dataset.subject"
          onChange={(value) => onChange({ ...recipe, dataset: { ...recipe.dataset, subject: value || null } })}
        />
      ) : null}
      <SelectField
        label="Error"
        value={recipe.error}
        options={errorModes}
        testId="recipe-error-field"
        field="error"
        onChange={(value) => onChange({ ...recipe, error: value as RecipeLayer["error"] })}
      />
      <TextField
        label="Label"
        value={String(label)}
        testId="recipe-label-field"
        field="style.label"
        onChange={(value) => onChange({ ...recipe, style: { ...recipe.style, label: value || null } })}
      />
      <label data-testid="recipe-color-field" data-field="style.color">
        Color
        <div className="swatches">
          {colors.map((swatch) => (
            <button
              key={swatch}
              className={swatch === effectiveColor ? "selected" : ""}
              style={{ background: swatch }}
              aria-label={swatch}
              data-testid="recipe-color-swatch"
              onClick={() => onChange({ ...recipe, style: { ...recipe.style, color: swatch } })}
            />
          ))}
        </div>
      </label>
      <div className="split-row">
        <SelectField
          label="Marker"
          value={String(marker)}
          options={markers}
          testId="recipe-marker-field"
          field="style.marker"
          optionLabel={(value) => value || "none"}
          onChange={(value) => onChange({ ...recipe, style: { ...recipe.style, marker: value || null } })}
        />
        <SelectField
          label="Line style"
          value={String(linestyle)}
          options={linestyles}
          testId="recipe-linestyle-field"
          field="style.linestyle"
          onChange={(value) => onChange({ ...recipe, style: { ...recipe.style, linestyle: value || null } })}
        />
      </div>
      <div className="split-row">
        <NumberField
          label="Line width"
          value={Number(linewidth)}
          step={0.1}
          min={0}
          testId="recipe-linewidth-field"
          field="style.linewidth"
          onChange={(value) => onChange({ ...recipe, style: { ...recipe.style, linewidth: value } })}
        />
        <NumberField
          label="Alpha"
          value={Number(alpha)}
          step={0.05}
          min={0}
          max={1}
          testId="recipe-alpha-field"
          field="style.alpha"
          onChange={(value) => onChange({ ...recipe, style: { ...recipe.style, alpha: value } })}
        />
      </div>
    </div>
  );
}

function LayerControls({
  layer,
  defaults,
  axes,
  onChange
}: {
  layer: PlotLayer;
  defaults?: LayerStyle;
  axes: AxesSpec[];
  onChange: (layer: PlotLayer) => void;
}) {
  const isFieldLayer = layer.kind === "heatmap" || layer.kind === "contour";
  const label = inheritedStyleValue(layer.style, defaults, "label") ?? "";
  const effectiveColor = inheritedStyleValue(layer.style, defaults, "color") ?? "";
  const marker = inheritedStyleValue(layer.style, defaults, "marker") ?? "";
  const linestyle = inheritedStyleValue(layer.style, defaults, "linestyle") ?? "";
  const linewidth = inheritedStyleValue(layer.style, defaults, "linewidth") ?? 1.8;
  const alpha = inheritedStyleValue(layer.style, defaults, "alpha") ?? 1;
  const cmap = inheritedStyleValue(layer.style, defaults, "cmap") ?? "viridis";
  const bins = inheritedStyleValue(layer.style, defaults, "bins") ?? 30;
  const fillAlpha = inheritedStyleValue(layer.style, defaults, "fill_alpha") ?? 0.3;
  const colorbarDefault = inheritedStyleValue(layer.style, defaults, "colorbar");
  return (
    <div className="layer-controls">
      {defaults ? <p className="profile-note">Layer defaults inherited from project profile.</p> : null}
      <div className="split-row">
        <SelectField
          label="Axes"
          value={layer.axes_id}
          options={axes.map((axis) => axis.id)}
          testId="layer-axes-field"
          field="axes_id"
          onChange={(value) => onChange({ ...layer, axes_id: value })}
        />
        <SelectField
          label="Y axis"
          value={layer.y_axis ?? "left"}
          options={yAxisTargets}
          testId="layer-y-axis-field"
          field="y_axis"
          optionLabel={(value) => (value === "right" ? "Right" : "Left")}
          onChange={(value) => onChange({ ...layer, y_axis: value as LayerYAxis })}
        />
      </div>
      <SelectField
        label="Plot type"
        value={layer.kind}
        options={plotKinds}
        testId="layer-kind-field"
        field="kind"
        onChange={(value) => {
          const nextKind = value as PlotKind;
          onChange({
            ...layer,
            kind: nextKind,
            y_axis: supportsSecondaryYAxis(nextKind) ? (layer.y_axis ?? "left") : "left"
          });
        }}
      />
      {layer.y_axis === "right" && !supportsSecondaryYAxis(layer.kind) ? (
        <p className="compatibility-note">Right Y axis supports simple overlay layer kinds in this beta slice.</p>
      ) : null}
      <TextField
        label="Label"
        value={String(label)}
        testId="layer-label-field"
        field="style.label"
        onChange={(value) => onChange({ ...layer, style: { ...layer.style, label: value || null } })}
      />
      {isFieldLayer ? (
        <>
          <SelectField
            label="Colormap"
            value={String(cmap)}
            options={cmaps}
            testId="layer-cmap-field"
            field="style.cmap"
            onChange={(value) => onChange({ ...layer, style: { ...layer.style, cmap: value } })}
          />
          <ToggleField
            label="Colorbar"
            value={Boolean(colorbarDefault ?? layer.kind === "heatmap")}
            testId="layer-colorbar-field"
            field="style.colorbar"
            onChange={(value) => onChange({ ...layer, style: { ...layer.style, colorbar: value } })}
          />
        </>
      ) : (
        <label data-testid="layer-color-field" data-field="style.color">
          Color
          <div className="swatches">
            {colors.map((swatch) => (
              <button
                key={swatch}
                className={swatch === effectiveColor ? "selected" : ""}
                style={{ background: swatch }}
                aria-label={swatch}
                data-testid="color-swatch"
                onClick={() => onChange({ ...layer, style: { ...layer.style, color: swatch } })}
              />
            ))}
          </div>
        </label>
      )}
      <div className="split-row">
        <SelectField
          label="Marker"
          value={String(marker)}
          options={markers}
          testId="layer-marker-field"
          field="style.marker"
          optionLabel={(value) => value || "none"}
          onChange={(value) => onChange({ ...layer, style: { ...layer.style, marker: value || null } })}
        />
        <SelectField
          label="Line style"
          value={String(linestyle)}
          options={linestyles}
          testId="layer-linestyle-field"
          field="style.linestyle"
          onChange={(value) => onChange({ ...layer, style: { ...layer.style, linestyle: value || null } })}
        />
      </div>
      <div className="split-row">
        <NumberField
          label="Line width"
          value={Number(linewidth)}
          step={0.1}
          min={0}
          testId="layer-linewidth-field"
          field="style.linewidth"
          onChange={(value) => onChange({ ...layer, style: { ...layer.style, linewidth: value } })}
        />
        <NumberField
          label="Alpha"
          value={Number(alpha)}
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
          value={Number(bins)}
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
          value={Number(fillAlpha)}
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
