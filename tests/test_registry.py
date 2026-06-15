import pytest

from figstudio.registry import VariableRegistry


def test_dataframe_summary():
    pd = pytest.importorskip("pandas")
    df = pd.DataFrame({"x": [1, 2], "y": [3.0, 4.0]})

    summaries = VariableRegistry({"df": df}).summaries()

    assert summaries[0].name == "df"
    assert summaries[0].kind == "dataframe"
    assert summaries[0].columns == ["x", "y"]
    assert summaries[0].shape == [2, 2]


def test_private_variables_are_ignored():
    summaries = VariableRegistry({"_hidden": [1, 2], "visible": [1, 2]}).summaries()

    assert [summary.name for summary in summaries] == ["visible"]
