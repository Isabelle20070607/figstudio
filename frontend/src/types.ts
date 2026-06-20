export type PlotKind =
  | "line"
  | "scatter"
  | "bar"
  | "barh"
  | "hist"
  | "boxplot"
  | "violin"
  | "errorbar"
  | "heatmap"
  | "contour"
  | "step"
  | "fill_between";

export type RecipeKind = "mean_sem_line" | "mean_sem_bar" | "count_bar" | "grouped_points" | "paired_before_after";

export type FigurePreset = "custom" | "journal_single" | "journal_double" | "poster" | "slide";

export type ReferenceLineOrientation = "horizontal" | "vertical";
export type LayerYAxis = "left" | "right";

export interface DataFilterSpec {
  column: string;
  op: "eq";
  value?: unknown;
  label?: string | null;
}

export interface DataSelectionSpec {
  kind: "mapping_key" | "sequence_index";
  key?: unknown;
  index?: number | null;
  label?: string | null;
}

export interface VariableSummary {
  name: string;
  kind: string;
  type_name: string;
  shape: Array<number | string>;
  columns: string[];
  dtypes: Record<string, string>;
  sample: unknown;
  truncated: boolean;
}

export interface DatasetRef {
  variable: string;
  selection?: DataSelectionSpec | null;
  x_variable?: string | null;
  y_variable?: string | null;
  z_variable?: string | null;
  yerr_variable?: string | null;
  x?: string | null;
  y?: string | null;
  z?: string | null;
  yerr?: string | null;
  filters: DataFilterSpec[];
}

export interface RecipeDatasetRef {
  variable: string;
  x?: string | null;
  y?: string | null;
  group?: string | null;
  subject?: string | null;
  filters: DataFilterSpec[];
}

export interface LayerStyle {
  label?: string | null;
  color?: string | null;
  marker?: string | null;
  linestyle?: string | null;
  linewidth?: number | null;
  alpha?: number | null;
  cmap?: string | null;
  bins?: number | null;
  fill_alpha?: number | null;
  colorbar?: boolean | null;
}

export interface PlotLayer {
  id: string;
  kind: PlotKind;
  axes_id: string;
  y_axis: LayerYAxis;
  dataset: DatasetRef;
  style: LayerStyle;
  readonly: boolean;
  source: string;
}

export interface RecipeLayer {
  id: string;
  kind: RecipeKind;
  axes_id: string;
  dataset: RecipeDatasetRef;
  style: LayerStyle;
  error: "sem" | "sd" | "none";
  readonly: boolean;
  source: string;
}

export interface SecondaryYAxisSpec {
  ylabel: string;
  yscale: "linear" | "log" | "symlog" | "logit";
  ylim?: [number | null, number | null] | null;
}

export interface AxesSpec {
  id: string;
  row: number;
  col: number;
  rowspan: number;
  colspan: number;
  title: string;
  xlabel: string;
  ylabel: string;
  xscale: "linear" | "log" | "symlog" | "logit";
  yscale: "linear" | "log" | "symlog" | "logit";
  xlim?: [number | null, number | null] | null;
  ylim?: [number | null, number | null] | null;
  secondary_y: SecondaryYAxisSpec;
  grid: boolean;
  legend: boolean;
  colorbar: boolean;
}

export interface AnnotationSpec {
  id: string;
  axes_id: string;
  text: string;
  x: number;
  y: number;
  xytext?: [number, number] | null;
}

export interface ReferenceLineSpec {
  id: string;
  axes_id: string;
  orientation: ReferenceLineOrientation;
  value: number;
  style: LayerStyle;
}

export interface FigureStyle {
  preset: FigurePreset;
  profile_id?: string | null;
  profile_overrides: string[];
  title: string;
  font_family?: string | null;
  font_size: number;
  constrained_layout: boolean;
}

export interface StyleProfileFigureDefaults {
  width?: number | null;
  height?: number | null;
  dpi?: number | null;
  font_family?: string | null;
  font_size?: number | null;
  constrained_layout?: boolean | null;
}

export interface StyleProfile {
  id: string;
  label: string;
  description?: string | null;
  figure: StyleProfileFigureDefaults;
  layers: Record<string, LayerStyle>;
  recipes: Record<string, LayerStyle>;
}

export interface StyleProfilesResponse {
  profiles: StyleProfile[];
  source_path?: string | null;
  warnings: string[];
}

export interface FigureSpec {
  version: number;
  mode: "explore" | "publish";
  width: number;
  height: number;
  dpi: number;
  rows: number;
  cols: number;
  share_x: boolean;
  share_y: boolean;
  axes: AxesSpec[];
  layers: PlotLayer[];
  recipes: RecipeLayer[];
  reference_lines: ReferenceLineSpec[];
  annotations: AnnotationSpec[];
  style: FigureStyle;
  show: boolean;
}

export interface SessionInfo {
  id: string;
  url: string;
  block_id: string;
  mode: string;
  script_path?: string | null;
  project_path: string;
  has_script_writeback: boolean;
  has_figure: boolean;
  figure_tree?: Record<string, unknown> | null;
}

export interface RenderResponse {
  image: string;
  format: string;
  code: string;
}

export interface SaveCodeResponse {
  ok: boolean;
  code: string;
  notebook_cell: string;
  wrote_file: boolean;
  script_path?: string | null;
  message: string;
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown> | null;
  } | null;
}

export interface ValidationIssue {
  severity: "error" | "warning";
  code: string;
  message: string;
  suggestion?: string | null;
  layer_id?: string | null;
  axes_id?: string | null;
  field?: string | null;
  details?: Record<string, unknown> | null;
}

export interface ValidationResponse {
  ok: boolean;
  issues: ValidationIssue[];
}

export interface FacetValuesRequest {
  variable: string;
  column: string;
  max_values: number;
}

export interface FacetValue {
  value?: unknown;
  label: string;
}

export interface FacetValuesResponse {
  values: FacetValue[];
  truncated: boolean;
}

export type RepeatedPanelSourceKind = "dataframe_column" | "mapping_keys" | "sequence_items";

export interface RepeatedPanelCandidatesRequest {
  variable: string;
  source_kind?: RepeatedPanelSourceKind | null;
  column?: string | null;
  max_values: number;
}

export interface RepeatedPanelCandidate {
  label: string;
  value?: unknown;
  selection?: DataSelectionSpec | null;
  summary?: VariableSummary | null;
}

export interface RepeatedPanelSkippedCandidate {
  label: string;
  reason: string;
}

export interface RepeatedPanelCandidatesResponse {
  source_kind: RepeatedPanelSourceKind;
  candidates: RepeatedPanelCandidate[];
  skipped: RepeatedPanelSkippedCandidate[];
  truncated: boolean;
}
