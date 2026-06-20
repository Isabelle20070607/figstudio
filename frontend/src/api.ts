import type {
  FacetValuesResponse,
  FigureSpec,
  RepeatedPanelCandidatesRequest,
  RepeatedPanelCandidatesResponse,
  RenderResponse,
  SaveCodeResponse,
  SessionInfo,
  StyleProfilesResponse,
  ExportFormat,
  ValidationContext,
  ValidationResponse,
  VariableSummary
} from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    ...init
  });
  if (!response.ok) {
    const text = await response.text();
    let payload: { detail?: { error?: { code?: string; message?: string } } } | undefined;
    try {
      payload = JSON.parse(text) as typeof payload;
    } catch {
      payload = undefined;
    }
    const error = payload?.detail?.error;
    if (error?.message) {
      throw new Error(error.code ? `${error.code}: ${error.message}` : error.message);
    }
    throw new Error(text || `${response.status} ${response.statusText}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  session: () => request<SessionInfo>("/api/session"),
  variables: () => request<VariableSummary[]>("/api/variables"),
  styleProfiles: () => request<StyleProfilesResponse>("/api/style-profiles"),
  spec: () => request<FigureSpec>("/api/spec"),
  render: (spec: FigureSpec, format: "svg" | "png" = "svg") =>
    request<RenderResponse>("/api/render", {
      method: "POST",
      body: JSON.stringify({ spec, format })
    }),
  validate: (
    spec: FigureSpec,
    options: { context?: ValidationContext; exportFormat?: ExportFormat } = {}
  ) =>
    request<ValidationResponse>("/api/validate", {
      method: "POST",
      body: JSON.stringify({
        spec,
        context: options.context ?? "edit",
        export_format: options.exportFormat ?? null
      })
    }),
  facetValues: (variable: string, column: string, maxValues = 12) =>
    request<FacetValuesResponse>("/api/facet-values", {
      method: "POST",
      body: JSON.stringify({ variable, column, max_values: maxValues })
    }),
  repeatedPanelCandidates: (payload: RepeatedPanelCandidatesRequest) =>
    request<RepeatedPanelCandidatesResponse>("/api/repeated-panel-candidates", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  updateSpec: (spec: FigureSpec) =>
    request<RenderResponse>("/api/spec", {
      method: "POST",
      body: JSON.stringify(spec)
    }),
  saveCode: (spec: FigureSpec, code?: string) =>
    request<SaveCodeResponse>("/api/save-code", {
      method: "POST",
      body: JSON.stringify({ spec, code })
    }),
  exportFigure: (spec: FigureSpec, format: ExportFormat) =>
    request<{ data?: string; output_path?: string | null; format: string; code: string }>("/api/export", {
      method: "POST",
      body: JSON.stringify({ spec, format })
    })
};
