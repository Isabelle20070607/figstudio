"""FigStudio public API."""

from figstudio.spec_io import load_spec, save_spec
from figstudio.session import FigStudioSession, open

__all__ = ["FigStudioSession", "load_spec", "open", "save_spec"]
