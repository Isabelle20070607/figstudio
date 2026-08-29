"""Hatch build hook for bundling the React frontend into the Python package."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version: str, build_data: dict[str, object]) -> None:
        if version == "editable":
            return
        if self.target_name not in {"sdist", "wheel"}:
            return
        skip_frontend_build = os.environ.get("FIGSTUDIO_SKIP_FRONTEND_BUILD") == "1"

        root = Path(self.root)
        frontend = root / "frontend"
        dist = frontend / "dist"
        static = root / "src" / "figstudio" / "static"
        npm = shutil.which("npm")

        if npm is None and not skip_frontend_build:
            raise RuntimeError("npm is required to build FigStudio frontend assets.")

        if not skip_frontend_build and not (frontend / "node_modules").exists():
            subprocess.run([npm, "ci"], cwd=frontend, check=True)
        if not skip_frontend_build:
            subprocess.run([npm, "run", "build"], cwd=frontend, check=True)
        if not (dist / "index.html").exists():
            if skip_frontend_build:
                raise RuntimeError("frontend/dist is required when FIGSTUDIO_SKIP_FRONTEND_BUILD=1.")
            raise RuntimeError("npm run build did not create frontend/dist/index.html.")

        if static.exists():
            shutil.rmtree(static)
        shutil.copytree(dist, static)
