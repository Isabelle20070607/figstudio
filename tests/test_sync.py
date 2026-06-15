from pathlib import Path
import uuid

import pytest

from figstudio.sync import CodeSyncEngine, CodeSyncError


def test_replace_default_block():
    source = "a = 1\n# figstudio:start main\nold()\n# figstudio:end main\nb = 2\n"

    updated = CodeSyncEngine("main").replace_block(source, "new()\n")

    assert updated == "a = 1\n# figstudio:start main\nnew()\n# figstudio:end main\nb = 2\n"


def test_missing_block_rejected():
    with pytest.raises(CodeSyncError):
        CodeSyncEngine("main").replace_block("print('x')\n", "new()\n")


def test_duplicate_block_rejected():
    source = (
        "# figstudio:start main\n"
        "# figstudio:end main\n"
        "# figstudio:start main\n"
        "# figstudio:end main\n"
    )

    with pytest.raises(CodeSyncError):
        CodeSyncEngine("main").replace_block(source, "new()\n")


def test_replace_file_reads_utf8_sig():
    temp_dir = Path.cwd() / ".test-temp"
    temp_dir.mkdir(exist_ok=True)
    path = temp_dir / f"script-{uuid.uuid4().hex}.py"
    path.write_text("\ufeff# figstudio:start main\nold()\n# figstudio:end main\n", encoding="utf-8")

    try:
        CodeSyncEngine("main").replace_file(path, "new()")

        assert "new()" in path.read_text(encoding="utf-8")
    finally:
        if path.exists():
            path.unlink()
