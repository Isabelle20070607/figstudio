"""Variable introspection for FigStudio sessions."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from figstudio.models import VariableSummary


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, str | int | float | bool):
        return value
    try:
        if hasattr(value, "item"):
            return value.item()
    except Exception:
        pass
    return repr(value)


@dataclass
class VariableRegistry:
    """Stores live Python objects and exposes small summaries to the UI."""

    namespace: Mapping[str, Any]
    sample_rows: int = 20
    max_items: int = 200

    def __post_init__(self) -> None:
        self._values = {
            name: value
            for name, value in dict(self.namespace or {}).items()
            if not name.startswith("_")
        }

    def namespace_dict(self) -> dict[str, Any]:
        return dict(self._values)

    def inject(self, values: Mapping[str, Any]) -> None:
        self._values.update(values)

    def get(self, name: str) -> Any:
        return self._values[name]

    def summaries(self) -> list[VariableSummary]:
        summaries: list[VariableSummary] = []
        for name, value in sorted(self._values.items()):
            summary = self._summarize(name, value)
            if summary is not None:
                summaries.append(summary)
        return summaries

    def _summarize(self, name: str, value: Any) -> VariableSummary | None:
        module = type(value).__module__
        type_name = type(value).__name__

        if module.startswith("pandas") and type_name == "DataFrame":
            return self._summarize_dataframe(name, value)
        if module.startswith("pandas") and type_name == "Series":
            return self._summarize_series(name, value)
        if module.startswith("numpy") and hasattr(value, "shape"):
            return self._summarize_array(name, value)
        if isinstance(value, list | tuple):
            return self._summarize_sequence(name, value)
        if type_name == "Figure" and module.startswith("matplotlib"):
            return VariableSummary(
                name=name,
                kind="figure",
                type_name=f"{module}.{type_name}",
            )
        return None

    def _summarize_dataframe(self, name: str, value: Any) -> VariableSummary:
        sample = value.head(self.sample_rows).to_dict(orient="records")
        return VariableSummary(
            name=name,
            kind="dataframe",
            type_name="pandas.DataFrame",
            shape=[int(value.shape[0]), int(value.shape[1])],
            columns=[str(column) for column in value.columns],
            dtypes={str(column): str(dtype) for column, dtype in value.dtypes.items()},
            sample=[{str(k): _jsonable(v) for k, v in row.items()} for row in sample],
            truncated=len(value) > self.sample_rows,
        )

    def _summarize_series(self, name: str, value: Any) -> VariableSummary:
        sample = value.head(self.sample_rows).tolist()
        return VariableSummary(
            name=name,
            kind="series",
            type_name="pandas.Series",
            shape=[int(value.shape[0])],
            columns=[str(value.name)] if value.name is not None else [],
            dtypes={str(value.name or "value"): str(value.dtype)},
            sample=[_jsonable(item) for item in sample],
            truncated=len(value) > self.sample_rows,
        )

    def _summarize_array(self, name: str, value: Any) -> VariableSummary:
        flattened = value.ravel()[: self.sample_rows] if hasattr(value, "ravel") else []
        return VariableSummary(
            name=name,
            kind="ndarray",
            type_name="numpy.ndarray",
            shape=[int(part) for part in value.shape],
            sample=[_jsonable(item) for item in flattened],
            truncated=int(getattr(value, "size", 0)) > self.sample_rows,
        )

    def _summarize_sequence(self, name: str, value: list[Any] | tuple[Any, ...]) -> VariableSummary | None:
        if not value:
            return VariableSummary(
                name=name,
                kind="sequence",
                type_name=type(value).__name__,
                shape=[0],
                sample=[],
            )
        if len(value) > self.max_items and not all(isinstance(item, int | float) for item in value[:20]):
            return None
        return VariableSummary(
            name=name,
            kind="sequence",
            type_name=type(value).__name__,
            shape=[len(value)],
            sample=[_jsonable(item) for item in value[: self.sample_rows]],
            truncated=len(value) > self.sample_rows,
        )
