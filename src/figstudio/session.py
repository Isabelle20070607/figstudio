"""Session lifecycle and public open() API."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import socket
import threading
from typing import Any, Mapping
from uuid import uuid4
import webbrowser

import uvicorn

from figstudio.inspector import FigureInspector
from figstudio.models import FigureSpec, SessionInfo
from figstudio.registry import VariableRegistry
from figstudio.style_profiles import resolve_project_path


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@dataclass
class FigStudioSession:
    registry: VariableRegistry
    figure: Any | None = None
    script_path: str | None = None
    project_path: str | Path | None = None
    block_id: str = "main"
    mode: str = "auto"
    host: str = "127.0.0.1"
    port: int = field(default_factory=_free_port)
    id: str = field(default_factory=lambda: uuid4().hex)
    spec: FigureSpec = field(default_factory=FigureSpec)
    _server: uvicorn.Server | None = None
    _thread: threading.Thread | None = None
    _figure_tree: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        self.project_path = str(
            resolve_project_path(script_path=self.script_path, project_path=self.project_path)
        )

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def start(self, *, open_browser: bool = True) -> "FigStudioSession":
        from figstudio.server import create_app

        if self.figure is not None:
            inspector = FigureInspector(self.figure)
            self._figure_tree = inspector.tree()
            self.registry.inject(inspector.extracted_namespace())
            self.spec = inspector.to_spec()

        app = create_app(self)
        config = uvicorn.Config(
            app,
            host=self.host,
            port=self.port,
            log_level="warning",
            access_log=False,
        )
        self._server = uvicorn.Server(config)
        self._thread = threading.Thread(target=self._server.run, name="figstudio-server", daemon=True)
        self._thread.start()
        if open_browser:
            webbrowser.open(self.url)
        return self

    def stop(self) -> None:
        if self._server:
            self._server.should_exit = True
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)

    def info(self) -> SessionInfo:
        return SessionInfo(
            id=self.id,
            url=self.url,
            block_id=self.block_id,
            mode=self.mode,
            script_path=self.script_path,
            project_path=str(self.project_path),
            has_script_writeback=self.script_path is not None,
            has_figure=self.figure is not None,
            figure_tree=self._figure_tree,
        )


def open(
    namespace: Mapping[str, Any] | None = None,
    *,
    figure: Any | None = None,
    script_path: str | None = None,
    project_path: str | Path | None = None,
    block_id: str = "main",
    mode: str = "auto",
    open_browser: bool = True,
) -> FigStudioSession:
    """Open a local FigStudio editing session."""

    registry = VariableRegistry(namespace or {})
    return FigStudioSession(
        registry=registry,
        figure=figure,
        script_path=script_path,
        project_path=project_path,
        block_id=block_id,
        mode=mode,
    ).start(open_browser=open_browser)
