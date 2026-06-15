import { create } from "zustand";
import type { FigureSpec, PlotLayer, RenderResponse, SessionInfo, VariableSummary } from "./types";

interface AppState {
  session?: SessionInfo;
  variables: VariableSummary[];
  spec?: FigureSpec;
  render?: RenderResponse;
  selectedVariable?: string;
  selectedLayerId?: string;
  status: string;
  setSession: (session: SessionInfo) => void;
  setVariables: (variables: VariableSummary[]) => void;
  setSpec: (spec: FigureSpec) => void;
  setRender: (render: RenderResponse) => void;
  setSelectedVariable: (name: string) => void;
  setSelectedLayerId: (id: string) => void;
  setStatus: (status: string) => void;
  updateSpec: (updater: (spec: FigureSpec) => FigureSpec) => void;
  selectedLayer: () => PlotLayer | undefined;
}

export const useAppStore = create<AppState>((set, get) => ({
  variables: [],
  status: "Loading session",
  setSession: (session) => set({ session }),
  setVariables: (variables) =>
    set((state) => ({
      variables,
      selectedVariable: state.selectedVariable ?? variables[0]?.name
    })),
  setSpec: (spec) =>
    set((state) => ({
      spec,
      selectedLayerId: state.selectedLayerId ?? spec.layers[0]?.id
    })),
  setRender: (render) => set({ render }),
  setSelectedVariable: (selectedVariable) => set({ selectedVariable }),
  setSelectedLayerId: (selectedLayerId) => set({ selectedLayerId }),
  setStatus: (status) => set({ status }),
  updateSpec: (updater) => {
    const current = get().spec;
    if (!current) {
      return;
    }
    const next = updater(structuredClone(current));
    set({ spec: next });
  },
  selectedLayer: () => {
    const state = get();
    return state.spec?.layers.find((layer) => layer.id === state.selectedLayerId);
  }
}));
