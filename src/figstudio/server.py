"""FastAPI application for FigStudio sessions."""

from __future__ import annotations

from importlib.resources import files
import os
from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

from figstudio.codegen import MatplotlibCodegen
from figstudio.models import (
    ExportRequest,
    ExportResponse,
    ErrorDetail,
    FigureSpec,
    RenderRequest,
    RenderResponse,
    SaveCodeRequest,
    SaveCodeResponse,
    ValidationRequest,
    ValidationResponse,
)
from figstudio.render import RenderEngine
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
    app = FastAPI(title="FigStudio", version="0.2.0")
    codegen = MatplotlibCodegen()

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

    @app.get("/api/spec")
    def get_spec() -> FigureSpec:
        return session.spec

    @app.post("/api/validate")
    def validate(request: ValidationRequest) -> ValidationResponse:
        return validate_figure_spec(session.registry.namespace_dict(), request.spec)

    @app.post("/api/spec")
    def update_spec(spec: FigureSpec) -> RenderResponse:
        session.spec = spec
        _raise_if_validation_failed(validate_figure_spec(session.registry.namespace_dict(), spec))
        try:
            image, code = RenderEngine(session.registry.namespace_dict(), codegen).render_base64(spec, "svg")
        except Exception as exc:
            _raise_api_error("render_failed", str(exc), details={"format": "svg"})
        return RenderResponse(image=image, format="svg", code=code)

    @app.post("/api/render")
    def render(request: RenderRequest) -> RenderResponse:
        session.spec = request.spec
        _raise_if_validation_failed(validate_figure_spec(session.registry.namespace_dict(), request.spec))
        try:
            image, code = RenderEngine(session.registry.namespace_dict(), codegen).render_base64(
                request.spec,
                request.format,
            )
        except Exception as exc:
            _raise_api_error("render_failed", str(exc), details={"format": request.format})
        return RenderResponse(image=image, format=request.format, code=code)

    @app.post("/api/save-code")
    def save_code(request: SaveCodeRequest) -> SaveCodeResponse:
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
        _raise_if_validation_failed(validate_figure_spec(session.registry.namespace_dict(), request.spec))
        try:
            data = RenderEngine(session.registry.namespace_dict(), codegen).export(
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
            code=codegen.generate(request.spec),
        )

    @app.websocket("/api/events")
    async def events(websocket: WebSocket):
        await websocket.accept()
        await websocket.send_json({"type": "connected", "session": session.info().model_dump()})
        while True:
            message = await websocket.receive_json()
            await websocket.send_json({"type": "ack", "message": message})

    return app


def _raise_if_validation_failed(response: ValidationResponse) -> None:
    if response.ok:
        return
    _raise_api_error(
        "validation_failed",
        "FigureSpec has validation errors.",
        details={"issues": [issue.model_dump() for issue in response.issues]},
    )
