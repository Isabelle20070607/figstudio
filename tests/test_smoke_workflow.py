from fastapi.testclient import TestClient

from figstudio.models import DatasetRef, FigureSpec, LayerStyle, PlotLayer
from figstudio.registry import VariableRegistry
from figstudio.server import create_app
from figstudio.session import FigStudioSession


def test_local_app_smoke_workflow_without_real_port():
    session = FigStudioSession(
        registry=VariableRegistry(
            {
                "time": [0, 1, 2, 3],
                "signal": [0.0, 0.8, 0.9, 0.1],
            }
        ),
        port=8765,
    )
    client = TestClient(create_app(session))

    root = client.get("/")
    assert root.status_code == 200
    assert "FigStudio" in root.text

    variables = client.get("/api/variables").json()
    assert {item["name"] for item in variables} == {"signal", "time"}

    spec = FigureSpec(
        layers=[
            PlotLayer(
                id="layer-smoke",
                kind="line",
                dataset=DatasetRef(variable="signal"),
                style=LayerStyle(label="Signal", color="#2563eb", marker="o"),
            )
        ]
    )
    rendered = client.post("/api/render", json={"spec": spec.model_dump(), "format": "svg"})
    assert rendered.status_code == 200
    assert "<svg" in rendered.json()["image"]
    assert "axes_flat[0].plot" in rendered.json()["code"]

    saved = client.post("/api/save-code", json={"spec": spec.model_dump()})
    assert saved.status_code == 200
    assert saved.json()["wrote_file"] is False
    assert "notebook_cell" in saved.json()
