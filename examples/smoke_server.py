"""Run a deterministic local FigStudio smoke-test server."""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd
import uvicorn

from figstudio.registry import VariableRegistry
from figstudio.server import create_app
from figstudio.session import FigStudioSession

DEFAULT_SMOKE_PORT = 8767
SMOKE_PROJECT_PATH = Path(__file__).resolve().with_name("smoke_project")


def main() -> None:
    os.environ.setdefault("FIGSTUDIO_DEV_STATIC", "1")
    port = int(os.environ.get("FIGSTUDIO_SMOKE_PORT", DEFAULT_SMOKE_PORT))
    time = np.tile(np.arange(5), 8)
    subject = np.repeat([f"s{index}" for index in range(1, 9)], 5)
    condition = np.repeat(["baseline", "drug"], 20)
    df = pd.DataFrame(
        {
            "time": time,
            "signal": np.sin(time / 2) + np.repeat(np.linspace(-0.2, 0.2, 8), 5),
            "condition": condition,
            "subject": subject,
        }
    )
    signal_map = {
        condition_value: group["signal"].to_numpy()
        for condition_value, group in df.groupby("condition", sort=False)
    }
    signal_sequence = [
        df.loc[df["subject"] == subject_id, "signal"].to_numpy()
        for subject_id in sorted(df["subject"].unique())
    ]
    session = FigStudioSession(
        registry=VariableRegistry(
            {
                "df": df,
                "signal_map": signal_map,
                "signal_sequence": signal_sequence,
            }
        ),
        port=port,
        project_path=SMOKE_PROJECT_PATH,
    )
    uvicorn.run(
        create_app(session),
        host="127.0.0.1",
        port=port,
        log_level="warning",
        access_log=False,
    )


if __name__ == "__main__":
    main()
