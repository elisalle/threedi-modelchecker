import pytest
from sqlalchemy import func, text
from sqlalchemy.orm import aliased, Query
from threedi_schema import constants, models

from threedi_modelchecker.checks.other import (
    ChannelManholeLevelCheck,
    ConnectionNodesDistance,
    ConnectionNodesLength,
    CrossSectionLocationCheck,
    LinestringLocationCheck,
    OpenChannelsWithNestedNewton,
    PotentialBreachInterdistanceCheck,
    PotentialBreachStartEndCheck,
    PumpStorageTimestepCheck,
    SpatialIndexCheck,
)

from . import factories


def test_connection_nodes_length(session):
    factories.GlobalSettingsFactory(epsg_code=28992)
    factories.WeirFactory(
        connection_node_start=factories.ConnectionNodeFactory(
            the_geom="SRID=4326;POINT(-0.38222995634060702 -0.13872239147499893)"
        ),
        connection_node_end=factories.ConnectionNodeFactory(
            the_geom="SRID=4326;POINT(-0.3822292515698168 -0.1387223869163263)"
        ),
    )
    weir_too_short = factories.WeirFactory(
        connection_node_start=factories.ConnectionNodeFactory(
            the_geom="SRID=4326;POINT(-0.38222938832999598 -0.13872236685816669)"
        ),
        connection_node_end=factories.ConnectionNodeFactory(
            the_geom="SRID=4326;POINT(-0.38222930900909202 -0.13872236685816669)"
        ),
    )

    check_length = ConnectionNodesLength(
        column=models.Weir.id,
        start_node=models.Weir.connection_node_start,
        end_node=models.Weir.connection_node_end,
        min_distance=0.05,
    )

    errors = check_length.get_invalid(session)
    assert len(errors) == 1
    assert errors[0].id == weir_too_short.id


def test_connection_nodes_length_missing_start_node(session):
    factories.GlobalSettingsFactory(epsg_code=28992)
    factories.WeirFactory(
        connection_node_start_id=9999,
        connection_node_end=factories.ConnectionNodeFactory(
            the_geom="SRID=4326;POINT(-0.38222930900909202 -0.13872236685816669)"
        ),
    )

    check_length = ConnectionNodesLength(
        column=models.Weir.id,
        start_node=models.Weir.connection_node_start,
        end_node=models.Weir.connection_node_end,
        min_distance=0.05,
    )

    errors = check_length.get_invalid(session)
    assert len(errors) == 0


def test_connection_nodes_length_missing_end_node(session):
    if session.bind.name == "postgresql":
        pytest.skip("Postgres only accepts coords in epsg 4326")
    factories.GlobalSettingsFactory(epsg_code=28992)
    factories.WeirFactory(
        connection_node_start=factories.ConnectionNodeFactory(
            the_geom="SRID=4326;POINT(-0.38222930900909202 -0.13872236685816669)"
        ),
        connection_node_end_id=9999,
    )

    check_length = ConnectionNodesLength(
        column=models.Weir.id,
        start_node=models.Weir.connection_node_start,
        end_node=models.Weir.connection_node_end,
        min_distance=0.05,
    )

    errors = check_length.get_invalid(session)
    assert len(errors) == 0


def test_open_channels_with_nested_newton(session):
    factories.NumericalSettingsFactory(use_of_nested_newton=0)
    channel = factories.ChannelFactory(
        connection_node_start=factories.ConnectionNodeFactory(
            the_geom="SRID=4326;POINT(-71.064544 42.28787)"
        ),
        connection_node_end=factories.ConnectionNodeFactory(
            the_geom="SRID=4326;POINT(-71.0645 42.287)"
        ),
        the_geom="SRID=4326;LINESTRING(-71.064544 42.28787, -71.0645 42.287)",
    )
    open_definition = factories.CrossSectionDefinitionFactory(
        shape=constants.CrossSectionShape.TABULATED_TRAPEZIUM, width="1 0"
    )
    factories.CrossSectionLocationFactory(
        channel=channel,
        definition=open_definition,
        the_geom="SRID=4326;POINT(-71.0645 42.287)",
    )

    channel2 = factories.ChannelFactory(
        connection_node_start=factories.ConnectionNodeFactory(
            the_geom="SRID=4326;POINT(-71.064544 42.28787)"
        ),
        connection_node_end=factories.ConnectionNodeFactory(
            the_geom="SRID=4326;POINT(-71.0645 42.287)"
        ),
        the_geom="SRID=4326;LINESTRING(-71.064544 42.28787, -71.0645 42.287)",
    )
    open_definition_egg = factories.CrossSectionDefinitionFactory(
        shape=constants.CrossSectionShape.EGG,
    )
    factories.CrossSectionLocationFactory(
        channel=channel2,
        definition=open_definition_egg,
        the_geom="SRID=4326;POINT(-71.0645 42.287)",
    )

    check = OpenChannelsWithNestedNewton()

    errors = check.get_invalid(session)
    assert len(errors) == 2


channel_manhole_level_testdata = [
    ("start", -1, -3, -2, 0),
    ("start", -3, -1, -2, 1),
    ("end", -3, -1, -2, 0),
    ("end", -1, -3, -2, 1),
]


@pytest.mark.parametrize(
    "manhole_location,starting_reference_level,ending_reference_level,manhole_level,errors_number",
    channel_manhole_level_testdata,
)
def test_channel_manhole_level_check(
    session,
    manhole_location,
    starting_reference_level,
    ending_reference_level,
    manhole_level,
    errors_number,
):
    # using factories, create one minimal test case which passes, and one which fails
    # once that works, parametrise.
    # use nested factories for channel and connectionNode
    starting_coordinates = "4.718300 52.696686"
    ending_coordinates = "4.718255 52.696709"
    start_node = factories.ConnectionNodeFactory(
        the_geom=f"SRID=4326;POINT({starting_coordinates})"
    )
    end_node = factories.ConnectionNodeFactory(
        the_geom=f"SRID=4326;POINT({ending_coordinates})"
    )
    channel = factories.ChannelFactory(
        the_geom=f"SRID=4326;LINESTRING({starting_coordinates}, {ending_coordinates})",
        connection_node_start=start_node,
        connection_node_end=end_node,
    )
    # starting cross-section location
    factories.CrossSectionLocationFactory(
        the_geom="SRID=4326;POINT(4.718278 52.696697)",
        reference_level=starting_reference_level,
        channel=channel,
    )
    # ending cross-section location
    factories.CrossSectionLocationFactory(
        the_geom="SRID=4326;POINT(4.718264 52.696704)",
        reference_level=ending_reference_level,
        channel=channel,
    )
    # manhole
    factories.ManholeFactory(
        connection_node=end_node if manhole_location == "end" else start_node,
        bottom_level=manhole_level,
    )
    check = ChannelManholeLevelCheck(nodes_to_check=manhole_location)
    errors = check.get_invalid(session)
    assert len(errors) == errors_number


def test_node_distance(session):
    con1_too_close = factories.ConnectionNodeFactory(
        the_geom="SRID=4326;POINT(4.728282 52.64579283592512)"
    )
    con2_too_close = factories.ConnectionNodeFactory(
        the_geom="SRID=4326;POINT(4.72828 52.64579283592512)"
    )
    # Good distance
    factories.ConnectionNodeFactory(
        the_geom="SRID=4326;POINT(4.726838755789598 52.64514133594995)"
    )

    # sanity check to see the distances between the nodes
    node_a = aliased(models.ConnectionNode)
    node_b = aliased(models.ConnectionNode)
    distances_query = Query(
        func.ST_Distance(node_a.the_geom, node_b.the_geom, 1)
    ).filter(node_a.id != node_b.id)
    # Shows the distances between all 3 nodes: node 1 and 2 are too close
    distances_query.with_session(session).all()

    check = ConnectionNodesDistance(minimum_distance=10)
    invalid = check.get_invalid(session)
    assert len(invalid) == 2
    invalid_ids = [i.id for i in invalid]
    assert con1_too_close.id in invalid_ids
    assert con2_too_close.id in invalid_ids


@pytest.mark.parametrize(
    "channel_geom",
    [
        "LINESTRING(5.387204 52.155172, 5.387204 52.155262)",
        "LINESTRING(5.387218 52.155172, 5.387218 52.155262)",  # within tolerance
        "LINESTRING(5.387204 52.155262, 5.387204 52.155172)",  # reversed
        "LINESTRING(5.387218 52.155262, 5.387218 52.155172)",  # reversed, within tolerance
    ],
)
def test_channels_location_check(session, channel_geom):
    factories.ChannelFactory(
        connection_node_start=factories.ConnectionNodeFactory(
            the_geom="SRID=4326;POINT(5.387204 52.155172)"
        ),
        connection_node_end=factories.ConnectionNodeFactory(
            the_geom="SRID=4326;POINT(5.387204 52.155262)"
        ),
        the_geom=f"SRID=4326;{channel_geom}",
    )

    errors = LinestringLocationCheck(
        column=models.Channel.the_geom, max_distance=1.01
    ).get_invalid(session)
    assert len(errors) == 0


@pytest.mark.parametrize(
    "channel_geom",
    [
        "LINESTRING(5.387204 52.164151, 5.387204 52.155262)",  # startpoint is wrong
        "LINESTRING(5.387204 52.155172, 5.387204 52.164151)",  # endpoint is wrong
    ],
)
def test_channels_location_check_invalid(session, channel_geom):
    factories.ChannelFactory(
        connection_node_start=factories.ConnectionNodeFactory(
            the_geom="SRID=4326;POINT(5.387204 52.155172)"
        ),
        connection_node_end=factories.ConnectionNodeFactory(
            the_geom="SRID=4326;POINT(5.387204 52.155262)"
        ),
        the_geom=f"SRID=4326;{channel_geom}",
    )

    errors = LinestringLocationCheck(
        column=models.Channel.the_geom, max_distance=1.01
    ).get_invalid(session)
    assert len(errors) == 1


def test_cross_section_location(session):
    channel = factories.ChannelFactory(
        the_geom="SRID=4326;LINESTRING(5.387204 52.155172, 5.387204 52.155262)",
    )
    factories.CrossSectionLocationFactory(
        channel=channel, the_geom="SRID=4326;POINT(5.387204 52.155200)"
    )
    factories.CrossSectionLocationFactory(
        channel=channel, the_geom="SRID=4326;POINT(5.387218 52.155244)"
    )
    errors = CrossSectionLocationCheck(0.1).get_invalid(session)
    assert len(errors) == 1


def test_spatial_index_ok(session):
    check = SpatialIndexCheck(models.ConnectionNode.the_geom)
    invalid = check.get_invalid(session)
    assert len(invalid) == 0


def test_spatial_index_disabled(empty_sqlite_v4):
    session = empty_sqlite_v4.get_session()
    session.execute(
        text("SELECT DisableSpatialIndex('v2_connection_nodes', 'the_geom')")
    )
    check = SpatialIndexCheck(models.ConnectionNode.the_geom)
    invalid = check.get_invalid(session)
    assert len(invalid) == 1


@pytest.mark.parametrize(
    "x,y,ok",
    [
        (-71.064544, 42.28787, True),  # at start
        (-71.0645, 42.287, True),  # at end
        (-71.06452, 42.2874, True),  # middle
        (-71.064544, 42.287869, False),  # close to start
        (-71.064499, 42.287001, False),  # close to end
    ],
)
def test_potential_breach_start_end(session, x, y, ok):
    # channel geom: LINESTRING (-71.064544 42.28787, -71.0645 42.287)
    factories.PotentialBreachFactory(
        the_geom=f"SRID=4326;LINESTRING({x} {y}, -71.064544 42.286)"
    )
    check = PotentialBreachStartEndCheck(
        models.PotentialBreach.the_geom, min_distance=1.0
    )
    invalid = check.get_invalid(session)
    if ok:
        assert len(invalid) == 0
    else:
        assert len(invalid) == 1


@pytest.mark.parametrize(
    "x,y,ok",
    [
        (-71.06452, 42.2874, True),  # exactly on other
        (-71.06452, 42.287401, False),  # too close to other
        (-71.0645, 42.287, True),  # far enough from other
    ],
)
def test_potential_breach_interdistance(session, x, y, ok):
    # channel geom: LINESTRING (-71.064544 42.28787, -71.0645 42.287)
    ref = factories.PotentialBreachFactory(
        the_geom="SRID=4326;LINESTRING(-71.06452 42.2874, -71.0646 42.286)"
    )
    factories.PotentialBreachFactory(
        the_geom=f"SRID=4326;LINESTRING({x} {y}, -71.064544 42.286)",
        channel=ref.channel,
    )
    check = PotentialBreachInterdistanceCheck(
        models.PotentialBreach.the_geom, min_distance=1.0
    )
    invalid = check.get_invalid(session)
    if ok:
        assert len(invalid) == 0
    else:
        assert len(invalid) == 1


def test_potential_breach_interdistance_other_channel(session):
    factories.PotentialBreachFactory(
        the_geom="SRID=4326;LINESTRING(-71.06452 42.2874, -71.0646 42.286)"
    )
    factories.PotentialBreachFactory(
        the_geom="SRID=4326;LINESTRING(-71.06452 42.287401, -71.064544 42.286)"
    )
    check = PotentialBreachInterdistanceCheck(
        models.PotentialBreach.the_geom, min_distance=1.0
    )
    invalid = check.get_invalid(session)
    assert len(invalid) == 0


@pytest.mark.parametrize(
    "storage_area,time_step,expected_result,capacity",
    [
        (0.64, 30, 1, 12.5),
        (600, 30, 0, 12.5),
        (None, 30, 0, 12.5),  # no storage --> open water --> no check
        (600, 30, 0, 0),
    ],
)
def test_pumpstation_storage_timestep(
    session, storage_area, time_step, expected_result, capacity
):
    connection_node = factories.ConnectionNodeFactory(storage_area=storage_area)
    factories.PumpstationFactory(
        connection_node_start=connection_node,
        start_level=-4,
        lower_stop_level=-4.78,
        capacity=capacity,
    )
    factories.GlobalSettingsFactory(sim_time_step=time_step)
    check = PumpStorageTimestepCheck(models.Pumpstation.capacity)
    invalid = check.get_invalid(session)
    assert len(invalid) == expected_result
