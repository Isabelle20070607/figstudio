"""Command-line interface for FigStudio."""

from __future__ import annotations

import argparse
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import runpy
import sys
import time
from typing import Any, Sequence

import numpy as np
import pandas as pd

from figstudio.codegen import MatplotlibCodegen
from figstudio.models import ExportFormat, ValidationContext, ValidationResponse
from figstudio.registry import VariableRegistry
from figstudio.render import RenderEngine
from figstudio.session import FigStudioSession, open
from figstudio.spec_io import load_spec
from figstudio.style_profiles import load_style_profiles, profile_map
from figstudio.validation import validate_figure_spec

DEFAULT_DEMO_PORT = 8767
EXIT_OK = 0
EXIT_VALIDATION_FAILED = 1
EXIT_USAGE_OR_RUNTIME_ERROR = 2
_RENDER_FORMATS = {"svg", "png"}
_EXPORT_FORMATS = {"svg", "png", "pdf"}


class FigStudioCliError(RuntimeError):
    """User-facing CLI failure."""


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.version:
        print(_version())
        return EXIT_OK

    try:
        if args.command == "demo":
            return _start_demo_session(args)
        if args.command == "codegen":
            return _command_codegen(args)
        if args.command == "validate":
            return _command_validate(args)
        if args.command == "render":
            return _command_render(args)
        if args.command == "export":
            return _command_export(args)
        return _start_empty_session(args)
    except FigStudioCliError as exc:
        print(f"figstudio: {exc}", file=sys.stderr)
        return EXIT_USAGE_OR_RUNTIME_ERROR
    except Exception as exc:
        print(f"figstudio: {exc}", file=sys.stderr)
        return EXIT_USAGE_OR_RUNTIME_ERROR


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="figstudio")
    parser.add_argument("--version", action="store_true", help="Print the installed FigStudio version.")
    parser.add_argument("--no-browser", action="store_true", help="Start without opening a browser.")
    parser.add_argument("--port", type=int, default=None, help="Bind to a specific localhost port.")
    parser.add_argument("--project", default=None, help="Project root containing .figstudio/styles.json.")
    subparsers = parser.add_subparsers(dest="command")

    demo_parser = subparsers.add_parser("demo", help="Start a demo session with sample data.")
    demo_parser.add_argument("--no-browser", action="store_true", help="Start without opening a browser.")
    demo_parser.add_argument("--port", type=int, default=None, help="Bind to a specific localhost port.")
    demo_parser.add_argument("--project", default=None, help="Project root containing .figstudio/styles.json.")

    codegen_parser = subparsers.add_parser("codegen", help="Generate plain Matplotlib code from a spec.")
    codegen_parser.add_argument("spec", help="Path to a .figstudio.json FigureSpec.")
    codegen_parser.add_argument("--output", "-o", default=None, help="Write code to this file instead of stdout.")
    codegen_parser.add_argument("--project", default=None, help="Project root containing .figstudio/styles.json.")

    validate_parser = subparsers.add_parser("validate", help="Validate a spec against optional trusted data.")
    validate_parser.add_argument("spec", help="Path to a .figstudio.json FigureSpec.")
    validate_parser.add_argument("--data-script", default=None, help="Trusted Python script that defines data variables.")
    validate_parser.add_argument(
        "--context",
        choices=["edit", "export"],
        default="edit",
        help="Validation context.",
    )
    validate_parser.add_argument(
        "--export-format",
        choices=sorted(_EXPORT_FORMATS),
        default=None,
        help="Export format for publication-readiness preflight.",
    )
    validate_parser.add_argument("--json", action="store_true", help="Print the full validation payload as JSON.")
    validate_parser.add_argument("--project", default=None, help="Project root containing .figstudio/styles.json.")

    render_parser = subparsers.add_parser("render", help="Render a preview image from a spec.")
    render_parser.add_argument("spec", help="Path to a .figstudio.json FigureSpec.")
    render_parser.add_argument("--data-script", required=True, help="Trusted Python script that defines data variables.")
    render_parser.add_argument("--output", "-o", required=True, help="Output image path.")
    render_parser.add_argument("--format", choices=sorted(_RENDER_FORMATS), default=None, help="Render format.")
    render_parser.add_argument("--dpi", type=int, default=None, help="Override render DPI.")
    render_parser.add_argument("--project", default=None, help="Project root containing .figstudio/styles.json.")

    export_parser = subparsers.add_parser("export", help="Export a publication file from a spec.")
    export_parser.add_argument("spec", help="Path to a .figstudio.json FigureSpec.")
    export_parser.add_argument("--data-script", required=True, help="Trusted Python script that defines data variables.")
    export_parser.add_argument("--output", "-o", required=True, help="Output export path.")
    export_parser.add_argument("--format", choices=sorted(_EXPORT_FORMATS), default=None, help="Export format.")
    export_parser.add_argument("--dpi", type=int, default=None, help="Override export DPI.")
    export_parser.add_argument("--project", default=None, help="Project root containing .figstudio/styles.json.")
    return parser


def _start_demo_session(args: argparse.Namespace) -> int:
    session = _demo_session(port=args.port, project_path=args.project)
    session.start(open_browser=not args.no_browser)
    print(session.url, flush=True)
    _wait_until_interrupted(session)
    return EXIT_OK


def _start_empty_session(args: argparse.Namespace) -> int:
    if args.port is not None:
        session = FigStudioSession(
            registry=VariableRegistry({}),
            port=args.port,
            project_path=args.project,
        ).start(open_browser=not args.no_browser)
    else:
        session = open({}, project_path=args.project, open_browser=not args.no_browser)
    print(session.url, flush=True)
    _wait_until_interrupted(session)
    return EXIT_OK


def _command_codegen(args: argparse.Namespace) -> int:
    spec = _load_spec(args.spec)
    code = MatplotlibCodegen(style_profiles=_load_profile_map(args.project)).generate(spec)
    if args.output:
        Path(args.output).expanduser().write_text(code, encoding="utf-8")
    else:
        print(code, end="")
    return EXIT_OK


def _command_validate(args: argparse.Namespace) -> int:
    spec = _load_spec(args.spec)
    namespace = _load_namespace(args.data_script) if args.data_script else {}
    response = validate_figure_spec(
        namespace,
        spec,
        style_profiles=_load_profile_map(args.project),
        context=args.context,
        export_format=args.export_format,
    )
    if args.json:
        print(response.model_dump_json(indent=2))
    else:
        _print_validation_response(response)
    return EXIT_OK if response.ok else EXIT_VALIDATION_FAILED


def _command_render(args: argparse.Namespace) -> int:
    output_path = Path(args.output).expanduser()
    output_format = _resolve_format(args.format, output_path, _RENDER_FORMATS)
    return _write_rendered_file(
        spec_path=args.spec,
        data_script=args.data_script,
        output_path=output_path,
        output_format=output_format,
        dpi=args.dpi,
        project=args.project,
        context="edit",
        export_format=None,
    )


def _command_export(args: argparse.Namespace) -> int:
    output_path = Path(args.output).expanduser()
    output_format = _resolve_format(args.format, output_path, _EXPORT_FORMATS)
    return _write_rendered_file(
        spec_path=args.spec,
        data_script=args.data_script,
        output_path=output_path,
        output_format=output_format,
        dpi=args.dpi,
        project=args.project,
        context="export",
        export_format=output_format,
    )


def _write_rendered_file(
    *,
    spec_path: str,
    data_script: str,
    output_path: Path,
    output_format: str,
    dpi: int | None,
    project: str | None,
    context: ValidationContext,
    export_format: ExportFormat | None,
) -> int:
    spec = _load_spec(spec_path)
    namespace = _load_namespace(data_script)
    profiles = _load_profile_map(project)
    validation = validate_figure_spec(
        namespace,
        spec,
        style_profiles=profiles,
        context=context,
        export_format=export_format,
    )
    if not validation.ok:
        _print_validation_response(validation, stream=sys.stderr)
        return EXIT_VALIDATION_FAILED

    engine = RenderEngine(namespace, MatplotlibCodegen(style_profiles=profiles), style_profiles=profiles)
    if context == "export":
        engine.export(spec, str(output_path), output_format, dpi=dpi)
    else:
        output_path.write_bytes(engine.render_bytes(spec, format=output_format, dpi=dpi))
    print(str(output_path))
    return EXIT_OK


def _load_spec(path: str) -> Any:
    source = Path(path).expanduser()
    if not source.exists():
        raise FigStudioCliError(f"Spec file not found: {source}")
    try:
        return load_spec(source)
    except Exception as exc:
        raise FigStudioCliError(f"Could not load spec {source}: {exc}") from exc


def _load_namespace(data_script: str) -> dict[str, Any]:
    source = Path(data_script).expanduser()
    if not source.exists():
        raise FigStudioCliError(f"Data script not found: {source}")
    try:
        return runpy.run_path(str(source))
    except Exception as exc:
        raise FigStudioCliError(f"Could not execute data script {source}: {exc}") from exc


def _load_profile_map(project_path: str | None) -> dict[str, Any]:
    project = Path(project_path).expanduser().resolve() if project_path else Path.cwd().resolve()
    return profile_map(load_style_profiles(project))


def _resolve_format(explicit: str | None, output_path: Path, supported: set[str]) -> str:
    if explicit:
        return explicit
    suffix = output_path.suffix.lower().lstrip(".")
    if suffix in supported:
        return suffix
    supported_list = ", ".join(sorted(supported))
    if suffix:
        raise FigStudioCliError(
            f"Cannot infer format from output suffix {output_path.suffix!r}; "
            f"use --format with one of: {supported_list}."
        )
    raise FigStudioCliError(f"Output path has no suffix; use --format with one of: {supported_list}.")


def _print_validation_response(
    response: ValidationResponse,
    *,
    stream: Any = sys.stdout,
) -> None:
    if not response.issues:
        print("OK: no validation issues.", file=stream)
        return
    if response.ok:
        print(f"OK: {len(response.issues)} warning(s).", file=stream)
    else:
        print(f"ERROR: {len(response.issues)} validation issue(s).", file=stream)
    for issue in response.issues:
        location = f" [{issue.field}]" if issue.field else ""
        print(f"- {issue.severity}: {issue.code}{location}: {issue.message}", file=stream)
        if issue.suggestion:
            print(f"  Suggested fix: {issue.suggestion}", file=stream)


def _demo_session(port: int | None = None, project_path: str | None = None) -> FigStudioSession:
    x = np.linspace(0, 10, 120)
    df = pd.DataFrame(
        {
            "time": x,
            "signal": np.sin(x),
            "baseline": np.cos(x) * 0.25,
            "error": np.full_like(x, 0.12),
            "condition": np.where(x < 3.4, "control", np.where(x < 6.8, "drug", "washout")),
        }
    )
    heatmap = np.outer(np.sin(np.linspace(0, np.pi, 32)), np.cos(np.linspace(0, np.pi, 48)))
    signal_map = {
        condition: group["signal"].to_numpy()
        for condition, group in df.groupby("condition", sort=False)
    }
    signal_sequence = [
        df.loc[df["condition"] == condition, "signal"].to_numpy()
        for condition in ["control", "drug", "washout"]
    ]
    return FigStudioSession(
        registry=VariableRegistry(
            {
                "df": df,
                "heatmap": heatmap,
                "signal_map": signal_map,
                "signal_sequence": signal_sequence,
            }
        ),
        port=port or DEFAULT_DEMO_PORT,
        project_path=project_path,
    )


def _version() -> str:
    try:
        return version("figstudio")
    except PackageNotFoundError:
        return "0.4.0"


def _wait_until_interrupted(session: FigStudioSession) -> None:
    try:
        while True:
            time.sleep(0.25)
    except KeyboardInterrupt:
        session.stop()
