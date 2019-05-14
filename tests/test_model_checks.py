import factory
from geoalchemy2 import Geometry
import pytest

from threedi_modelchecker.model_checks import (
    ThreediModelChecker,
    get_enum_columns,
    get_foreign_key_columns,
    get_none_nullable_columns,
    get_null_errors,
    get_unique_columns,
    get_geometry_columns,
    query_invalid_type,
    query_invalid_geometry,
    query_invalid_geometry_types,
    query_invalid_enums,
    query_missing_foreign_key,
    query_not_null,
    query_not_unique,
    sqlalchemy_to_sqlite_type,
)
from threedi_modelchecker.threedi_model import constants, custom_types, models
from tests import factories


def test_check_fk(session):
    factories.ManholeFactory.create_batch(5)

    foreign_key_q = query_missing_foreign_key(
        session,
        models.Manhole.connection_node_id,
        models.ConnectionNode.id
    )
    assert foreign_key_q.count() == 0


def test_check_fk_no_entries(session):
    foreign_key_q = query_missing_foreign_key(
        session,
        models.Manhole.connection_node_id,
        models.ConnectionNode.id
    )
    assert foreign_key_q.count() == 0


def test_check_fk_null_fk(session):
    conn_node = factories.ConnectionNodeFactory()
    factories.ManholeFactory.create_batch(5, manhole_indicator=conn_node.id)
    factories.ManholeFactory(manhole_indicator=None)

    foreign_key_q = query_missing_foreign_key(
        session,
        models.Manhole.manhole_indicator,
        models.ConnectionNode.id
    )
    assert foreign_key_q.count() == 0


def test_check_fk_both_null(session):
    global_settings = factories.GlobalSettingsFactory(control_group_id=None)

    assert session.query(models.GlobalSetting).first().id is not None
    assert session.query(models.GlobalSetting.control_group_id).scalar() is None
    assert session.query(models.ControlGroup.id).scalar() is None
    foreign_key_q = query_missing_foreign_key(
        session,
        models.GlobalSetting.control_group_id,
        models.ControlGroup.id
    )
    assert foreign_key_q.count() == 0


def test_check_fk_missing_fk(session):
    conn_node = factories.ConnectionNodeFactory()
    factories.ManholeFactory.create_batch(5, manhole_indicator=conn_node.id)
    missing_fk = factories.ManholeFactory(manhole_indicator=-1)

    foreign_key_q = query_missing_foreign_key(
        session,
        models.Manhole.manhole_indicator,
        models.ConnectionNode.id
    )
    assert foreign_key_q.count() == 1
    assert foreign_key_q.first().id == missing_fk.id


def test_check_unique(session):
    factories.ManholeFactory.create_batch(5)

    not_unique_q = query_not_unique(session, models.Manhole.code)
    assert not_unique_q.count() == 0


def test_check_unique_duplicate_value(session):
    manholes = factories.ManholeFactory.create_batch(
        5, zoom_category=factory.Sequence(lambda n: n))
    duplicate_manhole = factories.ManholeFactory(
        zoom_category=manholes[0].zoom_category)

    not_unique_q = query_not_unique(session, models.Manhole.zoom_category)
    assert not_unique_q.count() == 2
    not_unique_q_ids = list(not_unique_q.values('id'))
    unpacked_ids = [id for id, in not_unique_q_ids]
    assert manholes[0].id in unpacked_ids
    assert duplicate_manhole.id in unpacked_ids


def test_check_unique_null_values(session):
    factories.ManholeFactory.create_batch(
        5, zoom_category=factory.Sequence(lambda n: n))
    factories.ManholeFactory.create_batch(3, zoom_category=None)

    not_unique_q = query_not_unique(session, models.ConnectionNode.id)
    assert not_unique_q.count() == 0


def test_not_null(session):
    factories.ConnectionNodeFactory.create_batch(
        5, storage_area=3.0)

    not_null_q = query_not_null(session, models.ConnectionNode.storage_area)
    assert not_null_q.count() == 0


def test_not_null_with_null_value(session):
    factories.ConnectionNodeFactory.create_batch(
        5, storage_area=3.0)
    null_node = factories.ConnectionNodeFactory(storage_area=None)

    not_null_q = query_not_null(session, models.ConnectionNode.storage_area)
    assert not_null_q.count() == 1
    assert not_null_q.first().id == null_node.id


def test_get_not_null_errors(session):
    factories.ConnectionNodeFactory.create_batch(
        5, storage_area=3.0)
    null_node = factories.ConnectionNodeFactory(storage_area=None)

    errors = get_null_errors(
        session, models.ConnectionNode.__table__.c.storage_area)
    error_list = list(errors)
    assert len(error_list) == 1
    assert null_node.id == error_list[0].id


def test_threedi_db_and_factories(threedi_db):
    """Test to ensure that the threedi_db and factories use the same
    session object."""
    session = threedi_db.get_session()
    manhole = factories.ManholeFactory()
    q = session.query(models.Manhole)
    assert q.count() == 1


def test_run_spatial_function(session):
    """Example how to use spatial functions.

     Works on postgis and spatialite"""
    c1 = factories.ConnectionNodeFactory()
    from geoalchemy2 import func
    q = session.query(func.ST_AsGeoJSON(models.ConnectionNode.the_geom))
    r = q.first()


def test_check_valid_type(session):
    if session.bind.name == 'postgresql':
        pytest.skip('type checks not working on postgres')
    factories.ManholeFactory(zoom_category=123)
    factories.ManholeFactory(zoom_category=456)

    invalid_types_q = query_invalid_type(session, models.Manhole.zoom_category)
    assert invalid_types_q.count() == 0


def test_check_valid_type_integer(session):
    if session.bind.name == 'postgresql':
        pytest.skip('type checks not working on postgres')
    factories.ManholeFactory(zoom_category=123)
    factories.ManholeFactory(zoom_category=None)
    m1 = factories.ManholeFactory(zoom_category='abc')
    m2 = factories.ManholeFactory(zoom_category=1.23)

    invalid_types_q = query_invalid_type(session, models.Manhole.zoom_category)
    assert invalid_types_q.count() == 2
    invalid_type_ids = invalid_types_q.values('id')
    unpacked_ids = [id for id, in invalid_type_ids]
    assert m1.id in unpacked_ids
    assert m2.id in unpacked_ids


def test_check_valid_type_varchar(session):
    if session.bind.name == 'postgresql':
        pytest.skip('type checks not working on postgres')
    factories.ManholeFactory(code='abc')
    factories.ManholeFactory(code=123)

    invalid_type_q = query_invalid_type(session, models.Manhole.code)
    assert invalid_type_q.count() == 0


def test_check_valid_type_boolean(session):
    if session.bind.name == 'postgresql':
        pytest.skip('type checks not working on postgres')
    factories.GlobalSettingsFactory(use_1d_flow=True)
    factories.GlobalSettingsFactory(use_1d_flow=1)
    # factories.GlobalSettingsFactory(use_1d_flow='true')
    # factories.GlobalSettingsFactory(use_1d_flow='1')
    # factories.GlobalSettingsFactory(use_1d_flow=1.0)

    invalid_type_q = query_invalid_type(session, models.GlobalSetting.use_1d_flow)
    assert invalid_type_q.count() == 0


def test_query_invalid_geometry(session):
    c = factories.ConnectionNodeFactory(
        the_geom='SRID=28992;POINT(-371.064544 42.28787)'
    )

    invalid_geom_q = query_invalid_geometry(
        session, models.ConnectionNode.the_geom
    )
    assert invalid_geom_q.count() == 0


def test_query_invalid_geometry_with_invalid_geoms(session):
    if session.bind.name == 'postgresql':
        pytest.skip('Not sure how to insert invalid types in postgresql')

    inser_invalid_geom_q = """
    INSERT INTO v2_connection_nodes (id, code, the_geom) 
    VALUES (2, 'the_code', 'invalid_geom')
    """
    session.execute(inser_invalid_geom_q)
    factories.ConnectionNodeFactory(
        the_geom='SRID=28992;POINT(-71.064544 42.28787)'
    )

    invalid_geom_q = query_invalid_geometry(
        session, models.ConnectionNode.the_geom
    )
    assert invalid_geom_q.count() == 1


def test_query_invalid_geometry_with_none_geoms(session):
    if session.bind.name == 'postgresql':
        pytest.skip('Not sure how to insert invalid types in postgresql')
    factories.ConnectionNodeFactory(
        the_geom_linestring='SRID=4326;LINESTRING(71.0 42.2, 71.3 42.3)'
    )
    none_geom = factories.ConnectionNodeFactory(
            the_geom_linestring=None
    )

    invalid_geom_q = query_invalid_geometry(
        session, models.ConnectionNode.the_geom_linestring
    )
    assert invalid_geom_q.count() == 0


def test_query_invalid_geometry_types(session):
    factories.ConnectionNodeFactory.create_batch(
        2, the_geom='SRID=28992;POINT(-71.064544 42.28787)'
    )

    invalid_geometry_types_q = query_invalid_geometry_types(
        session, models.ConnectionNode.the_geom)
    assert invalid_geometry_types_q.count() == 0


def test_query_invalid_geometry_types_invalid_geom_type(session):
    if session.bind.name == 'postgresql':
        pytest.skip('Not sure how to insert invalid geometry types in postgresql')
    factories.ConnectionNodeFactory(
        the_geom='SRID=28992;POINT(-71.064544 42.28787)'
    )
    invalid_geom_type = factories.ConnectionNodeFactory(
        the_geom='SRID=28992;LINESTRING(71.0 42.2, 71.3 42.3)'
    )
    invalid_geometry_types_q = query_invalid_geometry_types(
        session, models.ConnectionNode.the_geom)
    assert invalid_geometry_types_q.count() == 1
    assert invalid_geometry_types_q.first().id == invalid_geom_type.id


def test_query_invalid_values(session):
    factories.BoundaryConditions2DFactory()

    invalid_boundaries_q = query_invalid_enums(
        session, models.BoundaryConditions2D.boundary_type)
    assert invalid_boundaries_q.count() == 0


def test_query_invalid_values_with_null_values(session):
    factories.BoundaryConditions2DFactory(boundary_type=None)

    invalid_boundaries_q = query_invalid_enums(
        session, models.BoundaryConditions2D.boundary_type)
    assert invalid_boundaries_q.count() == 0


def test_query_invalid_values_with_invalid_value(session):
    factories.BoundaryConditions2DFactory()
    faulty_boundary = factories.BoundaryConditions2DFactory(boundary_type=-1)

    invalid_boundaries_q = query_invalid_enums(
        session, models.BoundaryConditions2D.boundary_type)
    assert invalid_boundaries_q.count() == 1
    assert invalid_boundaries_q.first().id == faulty_boundary.id


def test_query_invalid_values_string_enum(session):
    factories.AggregationSettingsFactory()

    invalid_boundaries_q = query_invalid_enums(
        session, models.AggregationSettings.aggregation_method)
    assert invalid_boundaries_q.count() == 0


def test_query_invalid_values_string_enum_with_invalid_value(session):
    if session.bind.name == 'postgresql':
        pytest.skip('Not able to add invalid aggregation method due to '
                    'CHECKED CONSTRAINT')
    a = factories.AggregationSettingsFactory(aggregation_method='invalid')

    invalid_boundaries_q = query_invalid_enums(
        session, models.AggregationSettings.aggregation_method)
    assert invalid_boundaries_q.count() == 1
    assert invalid_boundaries_q.first().id == a.id


def test_get_none_nullable_columns():
    not_null_columns = get_none_nullable_columns(models.Manhole.__table__)
    assert len(not_null_columns) == 3
    assert models.Manhole.id in not_null_columns
    assert models.Manhole.code in not_null_columns
    assert models.Manhole.display_name in not_null_columns


def test_get_unique_columns():
    unique_columns = get_unique_columns(models.Manhole.__table__)
    assert len(unique_columns) == 1
    assert models.Manhole.id in unique_columns
    assert models.Manhole.connection_node_id


def test_get_foreign_key_columns():
    foreign_key_columns = get_foreign_key_columns(models.Manhole.__table__)
    assert len(foreign_key_columns) == 1
    fk = foreign_key_columns.pop()
    assert models.Manhole.connection_node_id == fk.parent
    assert models.ConnectionNode.id == fk.column


def test_get_geometry_columns():
    geometry_columns = get_geometry_columns(models.ConnectionNode.__table__)

    assert len(geometry_columns) == 2
    assert models.ConnectionNode.the_geom in geometry_columns
    assert models.ConnectionNode.the_geom_linestring in geometry_columns


def test_get_enum_columns():
    enum_columns = get_enum_columns(models.BoundaryConditions2D.__table__)

    assert len(enum_columns) == 1
    assert enum_columns[0] == models.BoundaryConditions2D.boundary_type


def test_get_enum_columns_varcharenum():
    enum_columns = get_enum_columns(models.AggregationSettings.__table__)

    assert len(enum_columns) == 2
    enum_types = [e.type for e in enum_columns]
    assert models.AggregationSettings.aggregation_method.type in enum_types
    assert models.AggregationSettings.flow_variable.type in enum_types


def test_sqlalchemy_to_sqlite_type_with_custom_type():
    customIntegerEnum = custom_types.IntegerEnum(constants.BoundaryType)
    assert sqlalchemy_to_sqlite_type(customIntegerEnum) == 'integer'


class TestThreediModelChecker(object):

    def test_not_null_columns_errors(self, modelchecker):
        result = modelchecker.yield_null_errors()
        print(result)

    def test_foreign_keys_errors(self, modelchecker):
        result = modelchecker.yield_foreign_key_errors()
        print(result)

    def test_data_types_errors(self, modelchecker):
        result = modelchecker.yield_data_type_errors()
        print(result)

    def test_not_unique_errors(self, modelchecker):
        result = modelchecker.yield_not_unique_errors()
        print(result)

    def test_parse_model(self, modelchecker):
        all_errors = modelchecker.parse_model()
        print(all_errors)
