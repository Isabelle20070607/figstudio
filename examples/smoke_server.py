"""Run a deterministic local FigStudio smoke-test server."""

from __future__ import annotations

import os

import numpy as np
import pandas as pd
import uvicorn

from figstudio.registry import VariableRegistry
from figstudio.server import create_app
from figstudio.session import FigStudioSession


def main() -> None:
    os.environ.setdefault("FIGSTUDIO_DEV_STATIC", "1")
    df = pd.DataFrame(
        {
            "time": np.linspace(0, 10, 80),
            "signal": np.sin(np.linspace(0, 10, 80)),
        }
    )
    session = FigStudioSession(registry=VariableRegistry({"df": df}), port=8765)
    uvicorn.run(
        create_app(session),
        host="127.0.0.1",
        port=8765,
        log_level="warning",
        access_log=False,
    )


if __name__ == "__main__":
    main()
