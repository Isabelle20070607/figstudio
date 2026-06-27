from __future__ import annotations

from typing import get_args

from fastapi.testclient import TestClient

from figstudio.layers import layer_catalog, layer_supports_secondary_y
from figstudio.models import PlotKind
from figstudio.registry import VariableRegistry
from figstudio.server import create_app
from figstudio.session import FigStudioSession


def _layer(payload: dict, kind: str) -> dict:
    return next(layer for layer in payload["layers"] if layer["kind"] == kind)


def test_bundled_layer_catalog_covers_plot_kind_contract():
    catalog = layer_catalog()

    assert catalog.version == 1
    assert len(catalog.groups) == 3
    assert {layer.kind for layer in catalog.layers} == set(get_args(PlotKind))
    assert {layer.group_id for layer in catalog.layers} <= {group.id for group in catalog.groups}


def test_layer_catalog_api_exposes_validation_and_style_metadata():
    session = FigStudioSession(registry=VariableRegistry({}), port=8001)
    client = TestClient(create_app(session))

    response = client.get("/api/layer-catalog")

    assert response.status_code == 200
    payload = response.json()
    assert payload["version"] == 1
    assert len(payload["groups"]) == 3
    assert {layer["kind"] for layer in payload["layers"]} == set(get_args(PlotKind))

    line = _layer(payload, "line")
    assert line["label"] == "Line"
    assert line["required_fields"] == ["y"]
    assert line["optional_fields"] == ["x"]
    assert line["supports_secondary_y"] is True
    assert line["default_style"]["linewidth"] == 1.8

    barh = _layer(payload, "barh")
    assert barh["supports_secondary_y"] is False
    assert layer_supports_secondary_y("barh") is False

    heatmap = _layer(payload, "heatmap")
    assert heatmap["expects_2d"] is True
    assert heatmap["supports_colorbar"] is True
    assert heatmap["legend_policy"] == "none"
