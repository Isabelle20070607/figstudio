from fastapi.testclient import TestClient

from figstudio.models import DatasetRef, FigureSpec, PlotLayer
from figstudio.registry import VariableRegistry
from figstudio.server import create_app
from figstudio.session import FigStudioSession


def test_api_session_variables_render_and_notebook_save():
    session = FigStudioSession(registry=VariableRegistry({"values": [1, 2, 3]}), port=8001)
    client = TestClient(create_app(session))

    session_response = client.get("/api/session")
    assert session_response.status_code == 200
    assert session_response.json()["has_script_writeback"] is False

    variables_response = client.get("/api/variables")
    assert variables_response.status_code == 200
    assert variables_response.json()[0]["name"] == "values"

    spec = FigureSpec(
        layers=[
            PlotLayer(
                id="layer-1",
                kind="line",
                dataset=DatasetRef(variable="values"),
            )
        ]
    )
    render_response = client.post("/api/render", json={"spec": spec.model_dump(), "format": "svg"})
    assert render_response.status_code == 200
    assert "<svg" in render_response.json()["image"]

    save_response = client.post("/api/save-code", json={"spec": spec.model_dump()})
    assert save_response.status_code == 200
    assert save_response.json()["wrote_file"] is False
    assert "notebook_cell" in save_response.json()
