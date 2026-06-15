"""FastAPI application for FigStudio sessions."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from figstudio.codegen import MatplotlibCodegen
from figstudio.models import (
    ExportRequest,
    ExportResponse,
    FigureSpec,
    RenderRequest,
    RenderResponse,
    SaveCodeRequest,
    SaveCodeResponse,
)
from figstudio.render import RenderEngine
from figstudio.sync import CodeSyncEngine, CodeSyncError

if TYPE_CHECKING:
    from figstudio.session import FigStudioSession


def create_app(session: "FigStudioSession") -> FastAPI:
    app = FastAPI(title="FigStudio", version="0.1.0")
    codegen = MatplotlibCodegen()

    frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
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

    @app.get("/api/session")
    def get_session():
        return session.info()

    @app.get("/api/variables")
    def get_variables():
        return session.registry.summaries()

    @app.get("/api/spec")
    def get_spec() -> FigureSpec:
        return session.spec

    @app.post("/api/spec")
    def update_spec(spec: FigureSpec) -> RenderResponse:
        session.spec = spec
        image, code = RenderEngine(session.registry.namespace_dict(), codegen).render_base64(spec, "svg")
        return RenderResponse(image=image, format="svg", code=code)

    @app.post("/api/render")
    def render(request: RenderRequest) -> RenderResponse:
        session.spec = request.spec
        image, code = RenderEngine(session.registry.namespace_dict(), codegen).render_base64(
            request.spec,
            request.format,
        )
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
                    code=code,
                    notebook_cell=notebook_cell,
                    wrote_file=False,
                    script_path=session.script_path,
                    message=str(exc),
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
        data = RenderEngine(session.registry.namespace_dict(), codegen).export(
            request.spec,
            request.output_path,
            request.format,
            dpi=request.dpi,
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
