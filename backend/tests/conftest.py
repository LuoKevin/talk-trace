from collections.abc import Iterator
from pathlib import Path

import pytest


@pytest.fixture()
def isolated_storage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point SQLite and upload storage at a temporary test directory."""
    from app.api import jobs
    from app.db import database

    data_dir = tmp_path / "data"
    upload_dir = data_dir / "uploads"
    db_path = data_dir / "talktrace.db"

    monkeypatch.setattr(database, "DATA_DIR", data_dir)
    monkeypatch.setattr(database, "UPLOAD_DIR", upload_dir)
    monkeypatch.setattr(database, "DB_PATH", db_path)
    monkeypatch.setattr(jobs, "UPLOAD_DIR", upload_dir)

    database.init_db()
    return data_dir


@pytest.fixture()
def anyio_backend() -> Iterator[str]:
    yield "asyncio"
