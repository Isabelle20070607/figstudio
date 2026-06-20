"""Helpers for dataset item selection in repeated panel specs."""

from __future__ import annotations

from collections.abc import Mapping
import math
from typing import Any

from figstudio.models import DataSelectionSpec


def is_mapping_source(value: Any) -> bool:
    return isinstance(value, Mapping)


def is_sequence_source(value: Any) -> bool:
    return isinstance(value, list | tuple)


def normalize_mapping_key(key: Any) -> Any:
    if isinstance(key, list | tuple):
        return tuple(normalize_mapping_key(item) for item in key)
    return key


def is_python_literal_key(key: Any) -> bool:
    normalized = normalize_mapping_key(key)
    return _is_python_literal_value(normalized)


def python_literal_key(key: Any) -> str:
    normalized = normalize_mapping_key(key)
    if not _is_python_literal_value(normalized):
        raise ValueError(f"Unsupported mapping key for code generation: {key!r}")
    return repr(normalized)


def apply_selection(value: Any, selection: DataSelectionSpec | None) -> Any:
    if selection is None:
        return value
    if selection.kind == "mapping_key":
        return value[normalize_mapping_key(selection.key)]
    if selection.kind == "sequence_index":
        return value[selection.index]
    return value


def _is_python_literal_value(value: Any) -> bool:
    if value is None or isinstance(value, str | bool | int):
        return True
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, tuple):
        return all(_is_python_literal_value(item) for item in value)
    return False
