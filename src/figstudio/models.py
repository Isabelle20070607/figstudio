"""Pydantic models shared by the backend and generated API contracts."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


PlotKind = Literal[
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
    "fill_between",
]


class VariableSummary(BaseModel):
    name: str
    kind: str
    type_name: str
    shape: list[int | str] = Field(default_factory=list)
    columns: list[str] = Field(default_factory=list)
    dtypes: dict[str, str] = Field(default_factory=dict)
    sample: Any = None
    truncated: bool = False


class DatasetRef(BaseModel):
    variable: str
    x: str | None = None
    y: str | None = None
    z: str | None = None
    yerr: str | None = None


class LayerStyle(BaseModel):
    label: str | None = None
    color: str | None = None
    marker: str | None = None
    linestyle: str | None = None
    linewidth: float | None = None
    alpha: float | None = None
    cmap: str | None = None
    bins: int | None = None
    fill_alpha: float | None = None


class PlotLayer(BaseModel):
    id: str
    kind: PlotKind = "line"
    axes_id: str = "ax0"
    dataset: DatasetRef
    style: LayerStyle = Field(default_factory=LayerStyle)
    readonly: bool = False
    source: str = "generated"


class AxesSpec(BaseModel):
    id: str = "ax0"
    row: int = 0
    col: int = 0
    title: str = ""
    xlabel: str = ""
    ylabel: str = ""
    xscale: Literal["linear", "log", "symlog", "logit"] = "linear"
    yscale: Literal["linear", "log", "symlog", "logit"] = "linear"
    xlim: tuple[float | None, float | None] | None = None
    ylim: tuple[float | None, float | None] | None = None
    grid: bool = False
    legend: bool = True
    colorbar: bool = False


class AnnotationSpec(BaseModel):
    id: str
    axes_id: str = "ax0"
    text: str
    x: float
    y: float
    xytext: tuple[float, float] | None = None


class FigureStyle(BaseModel):
    title: str = ""
    font_family: str | None = None
    font_size: float = 10
    constrained_layout: bool = True


class FigureSpec(BaseModel):
    version: int = 1
    mode: Literal["explore", "publish"] = "explore"
    width: float = 6.4
    height: float = 4.8
    dpi: int = 120
    rows: int = 1
    cols: int = 1
    axes: list[AxesSpec] = Field(default_factory=lambda: [AxesSpec()])
    layers: list[PlotLayer] = Field(default_factory=list)
    annotations: list[AnnotationSpec] = Field(default_factory=list)
    style: FigureStyle = Field(default_factory=FigureStyle)
    show: bool = False


class SessionInfo(BaseModel):
    id: str
    url: str
    block_id: str
    mode: str
    script_path: str | None
    has_script_writeback: bool
    has_figure: bool
    figure_tree: dict[str, Any] | None = None


class RenderRequest(BaseModel):
    spec: FigureSpec
    format: Literal["png", "svg"] = "svg"


class RenderResponse(BaseModel):
    image: str
    format: str
    code: str


class SaveCodeRequest(BaseModel):
    spec: FigureSpec
    code: str | None = None


class SaveCodeResponse(BaseModel):
    code: str
    notebook_cell: str
    wrote_file: bool
    script_path: str | None = None
    message: str


class ExportRequest(BaseModel):
    spec: FigureSpec
    format: Literal["png", "svg", "pdf"] = "svg"
    output_path: str | None = None
    dpi: int | None = None


class ExportResponse(BaseModel):
    format: str
    output_path: str | None = None
    data: str | None = None
    code: str
