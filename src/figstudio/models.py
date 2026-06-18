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

RecipeKind = Literal["mean_sem_line", "grouped_points", "paired_before_after"]

FigurePreset = Literal["custom", "journal_single", "journal_double", "poster", "slide"]


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
    x_variable: str | None = None
    y_variable: str | None = None
    z_variable: str | None = None
    yerr_variable: str | None = None
    x: str | None = None
    y: str | None = None
    z: str | None = None
    yerr: str | None = None


class RecipeDatasetRef(BaseModel):
    variable: str
    x: str | None = None
    y: str | None = None
    group: str | None = None
    subject: str | None = None


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
    colorbar: bool | None = None


class PlotLayer(BaseModel):
    id: str
    kind: PlotKind = "line"
    axes_id: str = "ax0"
    dataset: DatasetRef
    style: LayerStyle = Field(default_factory=LayerStyle)
    readonly: bool = False
    source: str = "generated"


class RecipeLayer(BaseModel):
    id: str
    kind: RecipeKind
    axes_id: str = "ax0"
    dataset: RecipeDatasetRef
    style: LayerStyle = Field(default_factory=LayerStyle)
    error: Literal["sem", "sd", "none"] = "sem"
    readonly: bool = False
    source: str = "recipe"


class AxesSpec(BaseModel):
    id: str = "ax0"
    row: int = 0
    col: int = 0
    rowspan: int = 1
    colspan: int = 1
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
    preset: FigurePreset = "custom"
    profile_id: str | None = None
    profile_overrides: list[str] = Field(default_factory=list)
    title: str = ""
    font_family: str | None = None
    font_size: float = 10
    constrained_layout: bool = True


class StyleProfileFigureDefaults(BaseModel):
    width: float | None = None
    height: float | None = None
    dpi: int | None = None
    font_family: str | None = None
    font_size: float | None = None
    constrained_layout: bool | None = None


class StyleProfile(BaseModel):
    id: str
    label: str
    description: str | None = None
    figure: StyleProfileFigureDefaults = Field(default_factory=StyleProfileFigureDefaults)
    layers: dict[str, LayerStyle] = Field(default_factory=dict)
    recipes: dict[str, LayerStyle] = Field(default_factory=dict)


class StyleProfilesResponse(BaseModel):
    profiles: list[StyleProfile] = Field(default_factory=list)
    source_path: str | None = None
    warnings: list[str] = Field(default_factory=list)


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
    recipes: list[RecipeLayer] = Field(default_factory=list)
    annotations: list[AnnotationSpec] = Field(default_factory=list)
    style: FigureStyle = Field(default_factory=FigureStyle)
    show: bool = False


class SessionInfo(BaseModel):
    id: str
    url: str
    block_id: str
    mode: str
    script_path: str | None
    project_path: str
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


class ValidationIssue(BaseModel):
    severity: Literal["error", "warning"] = "error"
    code: str
    message: str
    suggestion: str | None = None
    layer_id: str | None = None
    axes_id: str | None = None
    field: str | None = None
    details: dict[str, Any] | None = None


class ValidationRequest(BaseModel):
    spec: FigureSpec


class ValidationResponse(BaseModel):
    ok: bool = True
    issues: list[ValidationIssue] = Field(default_factory=list)


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict[str, Any] | None = None


class SaveCodeRequest(BaseModel):
    spec: FigureSpec
    code: str | None = None


class SaveCodeResponse(BaseModel):
    ok: bool = True
    code: str
    notebook_cell: str
    wrote_file: bool
    script_path: str | None = None
    message: str
    error: ErrorDetail | None = None


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
