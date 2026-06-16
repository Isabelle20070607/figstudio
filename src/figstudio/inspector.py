"""Best-effort inspection of existing Matplotlib figures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

import numpy as np
from matplotlib.colors import to_hex

from figstudio.models import AxesSpec, DatasetRef, FigureSpec, LayerStyle, PlotLayer


def _color_value(value: Any) -> str | None:
    if value is None:
        return None
    try:
        array = np.asarray(value)
        if array.ndim > 1 and len(array):
            value = array[0]
        return to_hex(value)
    except (TypeError, ValueError):
        return str(value)


def _public_label(value: str | None) -> str | None:
    if not value or value.startswith("_"):
        return None
    return value


def _float(value: Any) -> float:
    return float(np.asarray(value).item())


@dataclass
class _InspectedLayer:
    layer: PlotLayer
    namespace: dict[str, Any]


@dataclass
class FigureInspector:
    figure: Any

    def extracted_namespace(self) -> dict[str, Any]:
        extracted: dict[str, Any] = {}
        for inspected in self._layers():
            extracted.update(inspected.namespace)
        return extracted

    def tree(self) -> dict[str, Any]:
        axes_nodes = []
        for index, axis in enumerate(_plot_axes(self.figure)):
            axes_nodes.append(
                {
                    "id": f"ax{index}",
                    "title": axis.get_title(),
                    "xlabel": axis.get_xlabel(),
                    "ylabel": axis.get_ylabel(),
                    "lines": [
                        {
                            "label": line.get_label(),
                            "color": _color_value(line.get_color()),
                            "linestyle": line.get_linestyle(),
                            "marker": line.get_marker(),
                            "readonly": False,
                        }
                        for line in axis.lines
                    ],
                    "scatter_collections": len(_scatter_collections(axis)),
                    "images": len(axis.images),
                    "bar_containers": len(_bar_containers(axis)),
                    "histograms": _histogram_nodes(axis),
                    "boxplots": _boxplot_nodes(axis),
                    "violin_plots": _violin_nodes(axis),
                    "collections": len(axis.collections),
                    "patches": len(axis.patches),
                    "legend": _legend_node(axis),
                }
            )
        return {
            "type": type(self.figure).__name__,
            "axes": axes_nodes,
            "colorbars": _colorbar_nodes(self.figure),
        }

    def to_spec(self) -> FigureSpec:
        width, height = self.figure.get_size_inches()
        axes_specs: list[AxesSpec] = []
        for index, axis in enumerate(_plot_axes(self.figure)):
            axis_id = f"ax{index}"
            axes_specs.append(
                AxesSpec(
                    id=axis_id,
                    row=index,
                    col=0,
                    title=axis.get_title(),
                    xlabel=axis.get_xlabel(),
                    ylabel=axis.get_ylabel(),
                    xscale=axis.get_xscale(),
                    yscale=axis.get_yscale(),
                    grid=any(line.get_visible() for line in axis.get_xgridlines()),
                    legend=axis.get_legend() is not None,
                    colorbar=bool(axis.images),
                )
            )
        return FigureSpec(
            mode="publish",
            width=float(width),
            height=float(height),
            dpi=int(self.figure.dpi),
            rows=max(1, len(axes_specs)),
            cols=1,
            axes=axes_specs or [AxesSpec()],
            layers=[inspected.layer for inspected in self._layers()],
        )

    def _layers(self) -> list[_InspectedLayer]:
        inspected: list[_InspectedLayer] = []
        for axis_index, axis in enumerate(_plot_axes(self.figure)):
            axis_id = f"ax{axis_index}"
            has_boxplot_metadata = bool(_boxplot_nodes(axis))
            for line in axis.lines:
                if _looks_like_box_line(line) or (
                    has_boxplot_metadata and _public_label(line.get_label()) is None
                ):
                    continue
                index = len(inspected)
                x_name = f"_figstudio_line_{index}_x"
                y_name = f"_figstudio_line_{index}_y"
                inspected.append(
                    _InspectedLayer(
                        namespace={x_name: line.get_xdata(), y_name: line.get_ydata()},
                        layer=PlotLayer(
                            id=f"line-{uuid4().hex[:8]}",
                            kind="line",
                            axes_id=axis_id,
                            dataset=DatasetRef(
                                variable=y_name,
                                x_variable=x_name,
                                y_variable=y_name,
                            ),
                            style=LayerStyle(
                                label=_public_label(line.get_label()),
                                color=_color_value(line.get_color()),
                                marker=line.get_marker(),
                                linestyle=line.get_linestyle(),
                                linewidth=float(line.get_linewidth()),
                                alpha=line.get_alpha(),
                            ),
                            source="inspected",
                        ),
                    )
                )

            for collection in _scatter_collections(axis):
                offsets = np.asarray(collection.get_offsets())
                if offsets.ndim != 2 or offsets.shape[1] < 2 or len(offsets) == 0:
                    continue
                index = len(inspected)
                x_name = f"_figstudio_scatter_{index}_x"
                y_name = f"_figstudio_scatter_{index}_y"
                inspected.append(
                    _InspectedLayer(
                        namespace={x_name: offsets[:, 0], y_name: offsets[:, 1]},
                        layer=PlotLayer(
                            id=f"scatter-{uuid4().hex[:8]}",
                            kind="scatter",
                            axes_id=axis_id,
                            dataset=DatasetRef(
                                variable=y_name,
                                x_variable=x_name,
                                y_variable=y_name,
                            ),
                            style=LayerStyle(
                                label=_public_label(collection.get_label()),
                                color=_color_value(collection.get_facecolors()),
                                marker="o",
                                alpha=collection.get_alpha(),
                            ),
                            source="inspected",
                        ),
                    )
                )

            for image in axis.images:
                index = len(inspected)
                z_name = f"_figstudio_image_{index}_z"
                cmap = getattr(image.get_cmap(), "name", None)
                inspected.append(
                    _InspectedLayer(
                        namespace={z_name: np.asarray(image.get_array())},
                        layer=PlotLayer(
                            id=f"image-{uuid4().hex[:8]}",
                            kind="heatmap",
                            axes_id=axis_id,
                            dataset=DatasetRef(variable=z_name, z_variable=z_name),
                            style=LayerStyle(
                                label=_public_label(image.get_label()),
                                cmap=cmap,
                                alpha=image.get_alpha(),
                            ),
                            source="inspected",
                        ),
                    )
                )

            for container in _bar_containers(axis):
                patches = list(container.patches)
                if not patches:
                    continue
                index = len(inspected)
                x_name = f"_figstudio_bar_{index}_x"
                y_name = f"_figstudio_bar_{index}_y"
                orientation = getattr(container, "orientation", "vertical")
                if orientation == "horizontal":
                    x_values = [patch.get_y() + patch.get_height() / 2 for patch in patches]
                    y_values = [patch.get_width() for patch in patches]
                    kind = "barh"
                else:
                    x_values = [patch.get_x() + patch.get_width() / 2 for patch in patches]
                    y_values = [patch.get_height() for patch in patches]
                    kind = "bar"
                inspected.append(
                    _InspectedLayer(
                        namespace={x_name: x_values, y_name: y_values},
                        layer=PlotLayer(
                            id=f"{kind}-{uuid4().hex[:8]}",
                            kind=kind,
                            axes_id=axis_id,
                            dataset=DatasetRef(
                                variable=y_name,
                                x_variable=x_name,
                                y_variable=y_name,
                            ),
                            style=LayerStyle(
                                label=_public_label(container.get_label()),
                                color=_color_value(patches[0].get_facecolor()),
                                alpha=patches[0].get_alpha(),
                            ),
                            source="inspected",
                        ),
                    )
                )

        return inspected


def _plot_axes(figure: Any) -> list[Any]:
    return [axis for axis in getattr(figure, "axes", []) if not _is_colorbar_axis(axis)]


def _is_colorbar_axis(axis: Any) -> bool:
    return getattr(axis, "get_label", lambda: "")() == "<colorbar>"


def _scatter_collections(axis: Any) -> list[Any]:
    collections = []
    for collection in axis.collections:
        if collection.__class__.__name__ in {"FillBetweenPolyCollection", "LineCollection"}:
            continue
        if not hasattr(collection, "get_offsets"):
            continue
        try:
            offsets = np.asarray(collection.get_offsets())
        except Exception:
            continue
        if offsets.ndim == 2 and offsets.shape[1] >= 2 and len(offsets):
            collections.append(collection)
    return collections


def _bar_containers(axis: Any) -> list[Any]:
    return [
        container
        for container in getattr(axis, "containers", [])
        if container.__class__.__name__ == "BarContainer" and getattr(container, "patches", None)
        and not _looks_like_histogram_container(container)
    ]


def _legend_node(axis: Any) -> dict[str, Any] | None:
    legend = axis.get_legend()
    if legend is None:
        return None
    labels = [text.get_text() for text in legend.get_texts() if text.get_text()]
    return {
        "visible": bool(legend.get_visible()),
        "labels": labels,
        "title": legend.get_title().get_text() or None,
    }


def _colorbar_nodes(figure: Any) -> list[dict[str, Any]]:
    nodes = []
    for index, axis in enumerate(getattr(figure, "axes", [])):
        if not _is_colorbar_axis(axis):
            continue
        nodes.append(
            {
                "id": f"colorbar{len(nodes)}",
                "figure_axes_index": index,
                "label": axis.get_ylabel() or axis.get_xlabel() or None,
                "collections": [collection.__class__.__name__ for collection in axis.collections],
            }
        )
    return nodes


def _histogram_nodes(axis: Any) -> list[dict[str, Any]]:
    nodes = []
    for container in getattr(axis, "containers", []):
        if not _looks_like_histogram_container(container):
            continue
        patches = list(container.patches)
        edges = [_float(patches[0].get_x())]
        edges.extend(_float(patch.get_x() + patch.get_width()) for patch in patches)
        nodes.append(
            {
                "bins": len(patches),
                "edges": edges,
                "counts": [_float(patch.get_height()) for patch in patches],
                "label": _public_label(next((patch.get_label() for patch in patches), None)),
                "color": _color_value(patches[0].get_facecolor()),
            }
        )
    return nodes


def _looks_like_histogram_container(container: Any) -> bool:
    patches = list(getattr(container, "patches", []) or [])
    if len(patches) < 2:
        return False
    widths = np.asarray([patch.get_width() for patch in patches], dtype=float)
    if not np.all(np.isfinite(widths)) or np.any(widths <= 0):
        return False
    left_edges = np.asarray([patch.get_x() for patch in patches], dtype=float)
    right_edges = left_edges + widths
    contiguous = np.allclose(left_edges[1:], right_edges[:-1])
    label = getattr(container, "get_label", lambda: "")()
    return bool(contiguous and str(label).startswith("_container"))


def _boxplot_nodes(axis: Any) -> list[dict[str, Any]]:
    boxes = [line for line in axis.lines if _looks_like_box_line(line)]
    tick_labels = [label.get_text() for label in axis.get_xticklabels()]
    nodes = []
    for index, line in enumerate(boxes):
        xdata = np.asarray(line.get_xdata(), dtype=float)
        ydata = np.asarray(line.get_ydata(), dtype=float)
        if xdata.size == 0 or ydata.size == 0:
            continue
        center = float(np.nanmean([np.nanmin(xdata), np.nanmax(xdata)]))
        nodes.append(
            {
                "position": center,
                "q1": float(np.nanmin(ydata)),
                "q3": float(np.nanmax(ydata)),
                "label": tick_labels[index] if index < len(tick_labels) and tick_labels[index] else None,
            }
        )
    return nodes


def _looks_like_box_line(line: Any) -> bool:
    try:
        xdata = np.asarray(line.get_xdata(), dtype=float)
        ydata = np.asarray(line.get_ydata(), dtype=float)
    except Exception:
        return False
    if xdata.size != 5 or ydata.size != 5:
        return False
    return bool(
        np.isclose(xdata[0], xdata[-1])
        and np.isclose(ydata[0], ydata[-1])
        and len(np.unique(np.round(xdata, 12))) == 2
        and len(np.unique(np.round(ydata, 12))) == 2
    )


def _violin_nodes(axis: Any) -> list[dict[str, Any]]:
    nodes = []
    for collection in axis.collections:
        if collection.__class__.__name__ != "FillBetweenPolyCollection":
            continue
        paths = getattr(collection, "get_paths", lambda: [])()
        if not paths:
            continue
        vertices = np.asarray(paths[0].vertices, dtype=float)
        if vertices.ndim != 2 or vertices.shape[1] < 2 or len(vertices) == 0:
            continue
        nodes.append(
            {
                "position": float(np.nanmedian(vertices[:, 0])),
                "ymin": float(np.nanmin(vertices[:, 1])),
                "ymax": float(np.nanmax(vertices[:, 1])),
                "color": _color_value(collection.get_facecolor()),
            }
        )
    return nodes
