"""Command-line entrypoint for FigStudio."""

from __future__ import annotations

import argparse
from importlib.metadata import PackageNotFoundError, version
import time
from typing import Sequence

import numpy as np
import pandas as pd

from figstudio.registry import VariableRegistry
from figstudio.session import FigStudioSession, open


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="figstudio")
    parser.add_argument("--version", action="store_true", help="Print the installed FigStudio version.")
    parser.add_argument("--no-browser", action="store_true", help="Start without opening a browser.")
    parser.add_argument("--port", type=int, default=None, help="Bind to a specific localhost port.")
    subparsers = parser.add_subparsers(dest="command")

    demo_parser = subparsers.add_parser("demo", help="Start a demo session with sample data.")
    demo_parser.add_argument("--no-browser", action="store_true", help="Start without opening a browser.")
    demo_parser.add_argument("--port", type=int, default=None, help="Bind to a specific localhost port.")

    args = parser.parse_args(argv)
    if args.version:
        print(_version())
        return

    if args.command == "demo":
        session = _demo_session(port=args.port)
        session.start(open_browser=not args.no_browser)
    else:
        if args.port is not None:
            session = FigStudioSession(registry=VariableRegistry({}), port=args.port).start(
                open_browser=not args.no_browser
            )
        else:
            session = open({}, open_browser=not args.no_browser)

    print(session.url, flush=True)
    _wait_until_interrupted(session)


def _demo_session(port: int | None = None) -> FigStudioSession:
    x = np.linspace(0, 10, 120)
    df = pd.DataFrame(
        {
            "time": x,
            "signal": np.sin(x),
            "baseline": np.cos(x) * 0.25,
            "error": np.full_like(x, 0.12),
        }
    )
    heatmap = np.outer(np.sin(np.linspace(0, np.pi, 32)), np.cos(np.linspace(0, np.pi, 48)))
    return FigStudioSession(
        registry=VariableRegistry({"df": df, "heatmap": heatmap}),
        port=port or 8765,
    )


def _version() -> str:
    try:
        return version("figstudio")
    except PackageNotFoundError:
        return "0.1.0"


def _wait_until_interrupted(session: FigStudioSession) -> None:
    try:
        while True:
            time.sleep(0.25)
    except KeyboardInterrupt:
        session.stop()


if __name__ == "__main__":
    main()
