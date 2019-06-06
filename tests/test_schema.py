from . import factories
from threedi_modelchecker.schema import ModelSchema, constants


def test_check_latest_migration_missing(threedi_db):
    factories.MigrationHistoryFactory()
    schema_checker = ModelSchema(threedi_db)
    latest = schema_checker._is_latest_migration()
    assert not latest


def test_check_latest_migration_correct(threedi_db):
    factories.MigrationHistoryFactory(
        id=constants.LATEST_MIGRATION_ID,
        migration=constants.LATEST_MIGRATION_NAME
    )
    schema_checker = ModelSchema(threedi_db)
    latest = schema_checker._is_latest_migration()
    assert latest
