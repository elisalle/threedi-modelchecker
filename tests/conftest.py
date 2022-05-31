from . import factories
from threedi_modelchecker.model_checks import Context
from threedi_modelchecker.model_checks import ThreediModelChecker
from threedi_modelchecker.threedi_database import ThreediDatabase

import os
import pathlib
import pytest
import shutil


try:
    import psycopg2
except ImportError:
    psycopg2 = None

data_dir = pathlib.Path(__file__).parent / "data"


@pytest.fixture(
    scope="session",
    params=["spatialite3", "spatialite4", "postgis"],
)
def threedi_db(request, tmpdir_factory):
    """Fixture which yields a empty 3di database

    A global Session object is configured based on database type. This allows
    the factories to operate on the same session object. See:
    https://factoryboy.readthedocs.io/en/latest/orms.html#managing-sessions
    """
    if request.param == "spatialite3":
        tmp_path = tmpdir_factory.mktemp("spatialite3")
        tmp_sqlite = tmp_path / "empty_v3.sqlite"
        shutil.copyfile(data_dir / "empty_v3.sqlite", tmp_sqlite)
        return ThreediDatabase(
            {"db_path": tmp_sqlite},
            db_type="spatialite",
            echo=False,
        )
    elif request.param == "spatialite4":
        tmp_path = tmpdir_factory.mktemp("spatialite4")
        tmp_sqlite = tmp_path / "empty_v4.sqlite"
        shutil.copyfile(data_dir / "empty_v4.sqlite", tmp_sqlite)
        return ThreediDatabase(
            {"db_path": tmp_sqlite},
            db_type="spatialite",
            echo=False,
        )
    elif request.param == "postgis":
        postgis_settings = {
            "host": os.environ.get("TEST_DB_HOST") or "localhost",
            "port": 5432,
            "database": "postgis",
            "username": "postgis",
            "password": "mysecret",
        }
        if psycopg2 is None:
            pytest.skip("Skipping postgres test as psycopg2 is not available.")
        return ThreediDatabase(postgis_settings, db_type="postgres", echo=False)


@pytest.fixture
def session(threedi_db):
    """Fixture which yields a session to an empty 3di database.

    At the end of the test, all uncommitted changes are rolled back. Never
    commit any transactions to the session! This will persist the changes
    and affect the upcoming tests.

    :return: sqlalchemy.orm.session.Session
    """
    s = threedi_db.get_session()

    factories.inject_session(s)
    s.model_checker_context = Context()

    yield s
    # Rollback the session => no changes to the database
    s.rollback()
    factories.inject_session(None)


@pytest.fixture
def modelchecker(threedi_db):
    mc = ThreediModelChecker(threedi_db)
    return mc


@pytest.fixture
def in_memory_sqlite():
    """An in-memory database without a schema (to test schema migrations)"""
    return ThreediDatabase({"db_path": ""}, db_type="spatialite", echo=False)


@pytest.fixture
def empty_sqlite_v3(tmp_path):
    """A function-scoped empty spatialite v3 in the latest migration state"""
    tmp_sqlite = tmp_path / "empty_v3.sqlite"
    shutil.copyfile(data_dir / "empty_v3.sqlite", tmp_sqlite)
    return ThreediDatabase({"db_path": tmp_sqlite}, db_type="spatialite", echo=False)


@pytest.fixture
def empty_sqlite_v4(tmp_path):
    """An function-scoped empty spatialite v4 in the latest migration state"""
    tmp_sqlite = tmp_path / "empty_v4.sqlite"
    shutil.copyfile(data_dir / "empty_v4.sqlite", tmp_sqlite)
    return ThreediDatabase({"db_path": tmp_sqlite}, db_type="spatialite", echo=False)


@pytest.fixture
def south_latest_sqlite(tmp_path):
    """An empty SQLite that is in its latest South migration state"""
    tmp_sqlite = tmp_path / "south_latest.sqlite"
    shutil.copyfile(data_dir / "south_latest.sqlite", tmp_sqlite)
    return ThreediDatabase({"db_path": tmp_sqlite}, db_type="spatialite", echo=False)


@pytest.fixture
def oldest_sqlite(tmp_path):
    """A real SQLite that is in its oldest possible south migration state (160)"""
    tmp_sqlite = tmp_path / "noordpolder.sqlite"
    shutil.copyfile(data_dir / "noordpolder.sqlite", tmp_sqlite)
    return ThreediDatabase({"db_path": tmp_sqlite}, db_type="spatialite", echo=False)
