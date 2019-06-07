import pytest

from threedi_modelchecker.checks.other import BankLevelCheck
from threedi_modelchecker.checks.other import CrossSectionShapeCheck
from threedi_modelchecker.checks.other import TimeseriesCheck
from threedi_modelchecker.checks.other import valid_tabulated_shape
from threedi_modelchecker.threedi_model import models, constants
from . import factories
from .factories import BoundaryConditions2DFactory


def test_check_cross_section_location_bank_levels(session):
    """Check 'CrossSectionLocation.bank_level' is not null if
        calculation_type is CONNECTED or DOUBLE_CONNECTED.
    """
    if session.bind.name == "postgresql":
        pytest.skip(
            "Postgis db has set constraints which make the "
            "channelfactory fail. Furthermore, it expects an SRID "
            "28992 while spatialite expects 4326."
        )
    channel = factories.ChannelFactory(
        calculation_type=constants.CalculationType.CONNECTED
    )
    wrong = factories.CrossSectionLocationFactory(
        channel=channel, bank_level=None
    )
    factories.CrossSectionLocationFactory(
        channel=channel, bank_level=1.0
    )
    factories.CrossSectionLocationFactory(
        channel=factories.ChannelFactory(
            calculation_type=constants.CalculationType.EMBEDDED
        ),
        bank_level=None,
    )

    bank_level_check = BankLevelCheck()
    invalid_bank_levels = bank_level_check.get_invalid(session)
    assert len(invalid_bank_levels) == 1
    assert invalid_bank_levels[0].id == wrong.id


def test_get_invalid_cross_section_shapes(session):
    factories.CrossSectionDefinitionFactory(
        width="1", height="1", shape=constants.CrossSectionShape.RECTANGLE
    )
    factories.CrossSectionDefinitionFactory(
        width="1", height=None, shape=constants.CrossSectionShape.CIRCLE
    )
    factories.CrossSectionDefinitionFactory(
        width="1 2", height="0 2",
        shape=constants.CrossSectionShape.TABULATED_TRAPEZIUM
    )

    coss_section_check = CrossSectionShapeCheck()
    invalid_rows = coss_section_check.get_invalid(session)
    assert len(invalid_rows) == 0


def test_valid_tabulated_shape():
    width = "0 1 2 3"
    height = "0 1 2 3"
    assert valid_tabulated_shape(width, height)


def test_valid_tabulated_shape_empty():
    assert not valid_tabulated_shape("", "")


def test_valid_tabulated_shape_unequal_length():
    width = "1 2"
    height = "1 2 3"
    assert not valid_tabulated_shape(width, height)


def test_valid_tabulated_shape_invalid_char():
    width = "1 2"
    height = "1 a"
    assert not valid_tabulated_shape(width, height)


def test_tabulated_shape_valid123():
    width = "7 7 0"
    height = "0 2.25 2.25"
    assert valid_tabulated_shape(width, height)


def test_tabulated_shape_invalid123():
    width = "0.5106338 0.8793753 1.109911 1.279277 1.409697 1.511286 1.589584 " \
            "1.647911 1.688341 1.71214 1.72 1.72"
    height = "0.831 0.749 0.667 0.585 0.503 0.421 0.338 0.256 0.174 0.092 0 0.01"
    assert not valid_tabulated_shape(width, height)


def test_timeseries_check(session):
    BoundaryConditions2DFactory()

    check = TimeseriesCheck(models.BoundaryConditions2D.timeseries)
    invalid = check.get_invalid(session)
    assert len(invalid) == 0


def test_timeseries_check_multiple(session):
    BoundaryConditions2DFactory.create_batch(3)

    check = TimeseriesCheck(models.BoundaryConditions2D.timeseries)
    invalid = check.get_invalid(session)
    assert len(invalid) == 0


def test_timeseries_check_different_timesteps(session):
    BoundaryConditions2DFactory(
        timeseries="0,-0.5\n1,1.4\n2,4.0"
    )
    boundary_condition2 = BoundaryConditions2DFactory(
        timeseries="0,-0.5\n1,1.4\n3,4.0"  # Note the last timestep is 3 instead of 2
    )

    check = TimeseriesCheck(models.BoundaryConditions2D.timeseries)
    invalid = check.get_invalid(session)
    assert len(invalid) == 1
    assert invalid[0].id == boundary_condition2.id
