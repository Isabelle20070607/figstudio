"""FastAPI application for FigStudio sessions."""

from __future__ import annotations

from collections.abc import Mapping
from importlib.resources import files
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

from figstudio.codegen import MatplotlibCodegen
from figstudio.models import (
    DataSelectionSpec,
    ExportRequest,
    ExportResponse,
    ErrorDetail,
    FacetValue,
    FacetValuesRequest,
    FacetValuesResponse,
    FigureSpec,
    RecipeCatalogResponse,
    RenderRequest,
    RenderResponse,
    RepeatedPanelCandidate,
    RepeatedPanelCandidatesRequest,
    RepeatedPanelCandidatesResponse,
    RepeatedPanelSkippedCandidate,
    SaveCodeRequest,
    SaveCodeResponse,
    ExportFormat,
    StyleProfilesResponse,
    ValidationContext,
    ValidationRequest,
    ValidationResponse,
)
from figstudio.registry import _jsonable
from figstudio.registry import VariableRegistry
from figstudio.recipes import recipe_catalog
from figstudio.render import RenderEngine
from figstudio.selection import is_python_literal_key
from figstudio.style_profiles import load_style_profiles, profile_map
from figstudio.sync import CodeSyncEngine, CodeSyncError
from figstudio.validation import validate_figure_spec

if TYPE_CHECKING:
    from figstudio.session import FigStudioSession


def _raise_api_error(
    code: str,
    message: str,
    *,
    status_code: int = 400,
    details: dict[str, object] | None = None,
) -> None:
    error = ErrorDetail(code=code, message=message, details=details)
    raise HTTPException(status_code=status_code, detail={"error": error.model_dump()})


def _frontend_dist_path() -> Path:
    source_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if os.environ.get("FIGSTUDIO_DEV_STATIC") == "1" and (source_dist / "index.html").exists():
        return source_dist
    package_static = files("figstudio").joinpath("static")
    if package_static.joinpath("index.html").is_file():
        return Path(str(package_static))
    return source_dist


def create_app(session: "FigStudioSession") -> FastAPI:
    app = FastAPI(title="FigStudio", version="0.3.1")

    frontend_dist = _frontend_dist_path()
    if frontend_dist.exists():
        app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")

    @app.get("/", response_class=HTMLResponse)
    def index() -> HTMLResponse:
        index_path = frontend_dist / "index.html"
        if index_path.exists():
            return HTMLResponse(index_path.read_text(encoding="utf-8"))
        return HTMLResponse(
            """
            <html>
              <body style="font-family: system-ui; margin: 2rem;">
                <h1>FigStudio API is running</h1>
                <p>Build the React frontend with <code>cd frontend; npm run build</code>.</p>
              </body>
            </html>
            """
        )

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon() -> Response:
        return Response(status_code=204)

    @app.get("/api/session")
    def get_session():
        return session.info()

    @app.get("/api/variables")
    def get_variables():
        return session.registry.summaries()

    @app.get("/api/style-profiles")
    def get_style_profiles() -> StyleProfilesResponse:
        return _style_profiles(session)

    @app.get("/api/recipe-catalog")
    def get_recipe_catalog() -> RecipeCatalogResponse:
        return recipe_catalog()

    @app.get("/api/spec")
    def get_spec() -> FigureSpec:
        return session.spec

    @app.post("/api/validate")
    def validate(request: ValidationRequest) -> ValidationResponse:
        return _validate_spec(
            session,
            request.spec,
            context=request.context,
            export_format=request.export_format,
        )

    @app.post("/api/facet-values")
    def facet_values(request: FacetValuesRequest) -> FacetValuesResponse:
        return _facet_values(session, request)

    @app.post("/api/repeated-panel-candidates")
    def repeated_panel_candidates(request: RepeatedPanelCandidatesRequest) -> RepeatedPanelCandidatesResponse:
        return _repeated_panel_candidates(session, request)

    @app.post("/api/spec")
    def update_spec(spec: FigureSpec) -> RenderResponse:
        session.spec = spec
        _raise_if_validation_failed(_validate_spec(session, spec))
        try:
            image, code = _render_engine(session).render_base64(spec, "svg")
        except Exception as exc:
            _raise_api_error("render_failed", str(exc), details={"format": "svg"})
        return RenderResponse(image=image, format="svg", code=code)

    @app.post("/api/render")
    def render(request: RenderRequest) -> RenderResponse:
        session.spec = request.spec
        _raise_if_validation_failed(_validate_spec(session, request.spec))
        try:
            image, code = _render_engine(session).render_base64(
                request.spec,
                request.format,
            )
        except Exception as exc:
            _raise_api_error("render_failed", str(exc), details={"format": request.format})
        return RenderResponse(image=image, format=request.format, code=code)

    @app.post("/api/save-code")
    def save_code(request: SaveCodeRequest) -> SaveCodeResponse:
        codegen = _codegen(session)
        code = request.code or codegen.generate(request.spec)
        notebook_cell = codegen.notebook_cell(request.spec)
        if session.script_path:
            try:
                CodeSyncEngine(session.block_id).replace_file(session.script_path, code)
            except CodeSyncError as exc:
                return SaveCodeResponse(
                    ok=False,
                    code=code,
                    notebook_cell=notebook_cell,
                    wrote_file=False,
                    script_path=session.script_path,
                    message=str(exc),
                    error=ErrorDetail(code="writeback_failed", message=str(exc)),
                )
            except OSError as exc:
                return SaveCodeResponse(
                    ok=False,
                    code=code,
                    notebook_cell=notebook_cell,
                    wrote_file=False,
                    script_path=session.script_path,
                    message=str(exc),
                    error=ErrorDetail(code="writeback_io_failed", message=str(exc)),
                )
            return SaveCodeResponse(
                code=code,
                notebook_cell=notebook_cell,
                wrote_file=True,
                script_path=session.script_path,
                message="Updated controlled FigStudio block.",
            )
        return SaveCodeResponse(
            code=code,
            notebook_cell=notebook_cell,
            wrote_file=False,
            script_path=None,
            message="No script_path was provided. Use notebook_cell as replacement code.",
        )

    @app.post("/api/export")
    def export(request: ExportRequest) -> ExportResponse:
        validation = _validate_spec(
            session,
            request.spec,
            context="export",
            export_format=request.format,
        )
        _raise_if_validation_failed(validation)
        try:
            engine = _render_engine(session)
            data = engine.export(
                request.spec,
                request.output_path,
                request.format,
                dpi=request.dpi,
            )
        except Exception as exc:
            _raise_api_error(
                "export_failed",
                str(exc),
                details={"format": request.format, "output_path": request.output_path},
            )
        return ExportResponse(
            format=request.format,
            output_path=request.output_path,
            data=data,
            code=engine.codegen.generate(request.spec),
        )

    @app.websocket("/api/events")
    async def events(websocket: WebSocket):
        await websocket.accept()
        await websocket.send_json({"type": "connected", "session": session.info().model_dump()})
        while True:
            message = await websocket.receive_json()
            await websocket.send_json({"type": "ack", "message": message})

    return app


def _style_profiles(session: "FigStudioSession") -> StyleProfilesResponse:
    return load_style_profiles(session.project_path)


def _codegen(session: "FigStudioSession") -> MatplotlibCodegen:
    return MatplotlibCodegen(style_profiles=profile_map(_style_profiles(session)))


def _render_engine(session: "FigStudioSession") -> RenderEngine:
    profiles = profile_map(_style_profiles(session))
    return RenderEngine(
        session.registry.namespace_dict(),
        MatplotlibCodegen(style_profiles=profiles),
        style_profiles=profiles,
    )


def _validate_spec(
    session: "FigStudioSession",
    spec: FigureSpec,
    *,
    context: ValidationContext = "edit",
    export_format: ExportFormat | None = None,
) -> ValidationResponse:
    return validate_figure_spec(
        session.registry.namespace_dict(),
        spec,
        style_profiles=profile_map(_style_profiles(session)),
        context=context,
        export_format=export_format,
    )


def _facet_values(session: "FigStudioSession", request: FacetValuesRequest) -> FacetValuesResponse:
    namespace = session.registry.namespace_dict()
    value = namespace.get(request.variable)
    if value is None:
        _raise_api_error(
            "missing_variable",
            f"Variable {request.variable!r} is not available.",
            details={"variable": request.variable},
        )
    if not _is_dataframe(value):
        _raise_api_error(
            "unsupported_facet_source",
            f"Facet values require a pandas DataFrame; {request.variable!r} is {type(value).__name__}.",
            details={"variable": request.variable, "type": type(value).__name__},
        )
    columns = [str(column) for column in getattr(value, "columns", [])]
    if request.column not in columns:
        _raise_api_error(
            "missing_column",
            f"Column {request.column!r} is not available on DataFrame {request.variable!r}.",
            details={"variable": request.variable, "column": request.column, "available_columns": columns[:12]},
        )

    values, truncated = _ordered_facet_values(value, request.column, request.max_values)
    return FacetValuesResponse(values=values, truncated=truncated)


def _repeated_panel_candidates(
    session: "FigStudioSession",
    request: RepeatedPanelCandidatesRequest,
) -> RepeatedPanelCandidatesResponse:
    namespace = session.registry.namespace_dict()
    value = namespace.get(request.variable)
    if value is None:
        _raise_api_error(
            "missing_variable",
            f"Variable {request.variable!r} is not available.",
            details={"variable": request.variable},
        )

    source_kind = request.source_kind or _candidate_source_kind(value)
    if source_kind is None:
        _raise_api_error(
            "unsupported_repeated_panel_source",
            f"Repeated panels require a DataFrame, mapping, list, or tuple source; {request.variable!r} is {type(value).__name__}.",
            details={"variable": request.variable, "type": type(value).__name__},
        )

    limit = max(1, min(100, request.max_values or 12))
    if source_kind == "dataframe_column":
        if not _is_dataframe(value):
            _raise_api_error(
                "unsupported_repeated_panel_source",
                f"DataFrame repeated-panel candidates require a pandas DataFrame; {request.variable!r} is {type(value).__name__}.",
                details={"variable": request.variable, "type": type(value).__name__},
            )
        if not request.column:
            _raise_api_error(
                "missing_column",
                "DataFrame repeated-panel candidates require a column.",
                details={"variable": request.variable, "available_columns": _dataframe_columns(value)[:12]},
            )
        columns = _dataframe_columns(value)
        if request.column not in columns:
            _raise_api_error(
                "missing_column",
                f"Column {request.column!r} is not available on DataFrame {request.variable!r}.",
                details={"variable": request.variable, "column": request.column, "available_columns": columns[:12]},
            )
        values, truncated = _ordered_facet_values(value, request.column, limit)
        return RepeatedPanelCandidatesResponse(
            source_kind=source_kind,
            candidates=[
                RepeatedPanelCandidate(label=item.label, value=item.value)
                for item in values
            ],
            truncated=truncated,
        )

    if source_kind == "mapping_keys":
        if not isinstance(value, Mapping):
            _raise_api_error(
                "unsupported_repeated_panel_source",
                f"Mapping repeated-panel candidates require a mapping; {request.variable!r} is {type(value).__name__}.",
                details={"variable": request.variable, "type": type(value).__name__},
            )
        return _mapping_panel_candidates(value, limit)

    if source_kind == "sequence_items":
        if not isinstance(value, list | tuple):
            _raise_api_error(
                "unsupported_repeated_panel_source",
                f"Sequence repeated-panel candidates require a list or tuple; {request.variable!r} is {type(value).__name__}.",
                details={"variable": request.variable, "type": type(value).__name__},
            )
        return _sequence_panel_candidates(value, limit)

    _raise_api_error(
        "unsupported_repeated_panel_source",
        f"Unsupported repeated-panel candidate source {source_kind!r}.",
        details={"variable": request.variable, "source_kind": source_kind},
    )


def _ordered_facet_values(value: Any, column: str, max_values: int) -> tuple[list[FacetValue], bool]:
    limit = max(1, min(100, max_values or 12))
    values: list[FacetValue] = []
    seen: set[str] = set()
    truncated = False
    for raw_value in value[column].tolist():
        if _is_null_facet_value(raw_value):
            continue
        json_value = _jsonable(raw_value)
        key = repr(json_value)
        if key in seen:
            continue
        seen.add(key)
        if len(values) >= limit:
            truncated = True
            break
        values.append(FacetValue(value=json_value, label=str(json_value)))
    return values, truncated


def _mapping_panel_candidates(value: Mapping[Any, Any], limit: int) -> RepeatedPanelCandidatesResponse:
    candidates: list[RepeatedPanelCandidate] = []
    skipped: list[RepeatedPanelSkippedCandidate] = []
    truncated = False
    for key, item in value.items():
        label = str(key)
        if not is_python_literal_key(key):
            skipped.append(
                RepeatedPanelSkippedCandidate(
                    label=label,
                    reason="Mapping key cannot be represented as a stable Python literal.",
                )
            )
            continue
        if len(candidates) >= limit:
            truncated = True
            break
        candidates.append(
            RepeatedPanelCandidate(
                label=label,
                selection=DataSelectionSpec(kind="mapping_key", key=key, label=label),
                summary=_candidate_summary(item),
            )
        )
    return RepeatedPanelCandidatesResponse(
        source_kind="mapping_keys",
        candidates=candidates,
        skipped=skipped,
        truncated=truncated,
    )


def _sequence_panel_candidates(value: list[Any] | tuple[Any, ...], limit: int) -> RepeatedPanelCandidatesResponse:
    candidates: list[RepeatedPanelCandidate] = []
    truncated = len(value) > limit
    for index, item in enumerate(value[:limit]):
        label = str(index)
        candidates.append(
            RepeatedPanelCandidate(
                label=label,
                selection=DataSelectionSpec(kind="sequence_index", index=index, label=label),
                summary=_candidate_summary(item),
            )
        )
    return RepeatedPanelCandidatesResponse(
        source_kind="sequence_items",
        candidates=candidates,
        truncated=truncated,
    )


def _candidate_summary(value: Any):
    summaries = VariableRegistry({"selected": value}).summaries()
    return summaries[0] if summaries else None


def _candidate_source_kind(value: Any):
    if _is_dataframe(value):
        return "dataframe_column"
    if isinstance(value, Mapping):
        return "mapping_keys"
    if isinstance(value, list | tuple):
        return "sequence_items"
    return None


def _dataframe_columns(value: Any) -> list[str]:
    return [str(column) for column in getattr(value, "columns", [])]


def _is_dataframe(value: object) -> bool:
    return type(value).__module__.startswith("pandas") and type(value).__name__ == "DataFrame"


def _is_null_facet_value(value: object) -> bool:
    if value is None:
        return True
    try:
        import pandas as pd

        return bool(pd.isna(value))
    except Exception:
        return False


def _raise_if_validation_failed(response: ValidationResponse) -> None:
    if response.ok:
        return
    _raise_api_error(
        "validation_failed",
        "FigureSpec has validation errors.",
        details={"issues": [issue.model_dump() for issue in response.issues]},
    )
