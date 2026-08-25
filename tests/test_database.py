from pathlib import Path

from storage.database import DEFAULT_DATABASE_PATH, Database


def test_default_database_path_is_independent_of_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    database = Database()

    try:
        assert Path(database.engine.url.database).resolve() == DEFAULT_DATABASE_PATH
        assert (
            Path(database.engine.url.database).resolve()
            != (tmp_path / "devops.db").resolve()
        )
    finally:
        database.close()
