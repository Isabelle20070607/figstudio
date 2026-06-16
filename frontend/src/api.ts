import type {
  FigureSpec,
  RenderResponse,
  SaveCodeResponse,
  SessionInfo,
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
  spec: () => request<FigureSpec>("/api/spec"),
  render: (spec: FigureSpec, format: "svg" | "png" = "svg") =>
    request<RenderResponse>("/api/render", {
      method: "POST",
      body: JSON.stringify({ spec, format })
    }),
  validate: (spec: FigureSpec) =>
    request<ValidationResponse>("/api/validate", {
      method: "POST",
      body: JSON.stringify({ spec })
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
  exportFigure: (spec: FigureSpec, format: "svg" | "png" | "pdf") =>
    request<{ data?: string; output_path?: string | null; format: string; code: string }>("/api/export", {
      method: "POST",
      body: JSON.stringify({ spec, format })
    })
};
