from enum import Enum


LATEST_SOUTH_MIGRATION_ID = 173
#  Migration 174 deletes some fields, which were already not present in the
#  models of the threedi-modelchecker. Therefore we can both accept migration
#  173 and 174.
MIN_SCHEMA_VERSION = 201
VERSION_TABLE_NAME = "schema_version"


class BoundaryType(Enum):
    WATERLEVEL = 1
    VELOCITY = 2
    DISCHARGE = 3
    RIEMANN = 4
    SOMMERFELD = 5


class Later2dType(Enum):
    SURFACE = 1


class FlowVariable(Enum):
    DISCHARGE = "discharge"
    FLOW_VELOCITY = "flow_velocity"
    PUMP_DISCHARGE = "pump_discharge"
    RAIN = "rain"
    WATERLEVEL = "waterlevel"
    WET_CROSS_SECTION = "wet_cross-section"
    WET_SURFACE = "wet_surface"
    LATERAL_DISCHARGE = "lateral_discharge"
    VOLUM = "volume"
    SIMPLE_INFILTRATION = "simple_infiltration"
    LEAKAGE = "leakage"
    INTERCEPTION = "interception"
    SURFACE_SOURCE_SINK_DISCHARGE = "surface_source_sink_discharge"


class AggregationMethod(Enum):
    AVERAGE = "avg"
    MINIMUM = "min"
    MAXIMUM = "max"
    CUMULATIVE = "cum"
    CUMULATIVE_NEGATIVE = "cum_negative"
    CUMULATIVE_POSITIVE = "cum_positive"
    CURRENT = "current"
    SUMMATION = "sum"


class CalculationType(Enum):
    EMBEDDED = 100
    STANDALONE = 101
    CONNECTED = 102
    DOUBLE_CONNECTED = 105


class CalculationTypeCulvert(Enum):
    EMBEDDED_NODE = 0
    ISOLATED_NODE = 1
    CONNECTED_NODE = 2
    EMBEDDED = 100
    STANDALONE = 101
    CONNECTED = 102
    DOUBLE_CONNECTED = 105


class CalculationTypeNode(Enum):
    EMBEDDED = 0
    ISOLATED = 1
    CONNECTED = 2


class CrossSectionShape(Enum):
    CLOSED_RECTANGLE = 0
    RECTANGLE = 1
    CIRCLE = 2
    EGG = 3
    TABULATED_RECTANGLE = 5
    TABULATED_TRAPEZIUM = 6


class FrictionType(Enum):
    CHEZY = 1
    MANNING = 2


class InitializationType(Enum):
    MAX = 0
    MIN = 1
    AVERAGE = 2


class SurfaceInclinationType(Enum):
    VLAK = "vlak"
    HELLEND = "hellend"
    UITGESTREKT = "uitgestrekt"


class SurfaceClass(Enum):
    GESLOTEN_VERHARDING = "gesloten verharding"
    OPEN_VERHARDING = "open verharding"
    HALF_VERHARD = "half verhard"
    ONVERHARD = "onverhard"
    PAND = "pand"


class SurfaceType(Enum):
    SURFACE = "v2_surface"
    IMPERVIOUS_SURFACE = "v2_impervious_surface"


class InterflowType(Enum):
    NO_INTERLFOW = 0
    LOCAL_DEEPEST_POINT_SCALED_POROSITY = 1
    GLOBAL_DEEPEST_POINT_SCALED_POROSITY = 2
    LOCAL_DEEPEST_POINT_CONSTANT_POROSITY = 3
    GLOBAL_DEEPEST_POINT_CONSTANT_POROSITY = 4


class Material(Enum):
    SAND = 1
    CLAY = 2


class CrestType(Enum):
    BROAD_CRESTED = 3
    SHORT_CRESTED = 4


class PipeCalculationType(Enum):
    EMBEDDED = 0
    ISOLATED = 1
    CONNECTED = 2
    BROAD_CRESTED = 3
    SHORT_CRESTED = 4


class SewerageType(Enum):
    MIXED = 0
    RAIN_WATER = 1
    DRY_WEATHER_FLOW = 2
    TRANSPORT = 3
    SPILLWAY = 4
    ZINKER = 5
    STORAGE = 6
    STORAGE_TANK = 7


class PumpType(Enum):
    SUCTION_SIDE = 1
    DELIVERY_SIDE = 2


class InfiltrationSurfaceOption(Enum):
    RAIN = 0
    WHOLE_SURFACE = 1
    WET_SURFACE = 2


class ZoomCategories(Enum):
    # Visibility in live-site: 0 is lowest for smallest level (i.e. ditch)
    # and 5 for highest (rivers).
    LOWEST_VISIBILITY = 0
    LOW_VISIBILITY = 1
    MEDIUM_LOW_VISIBILITY = 2
    MEDIUM_VISIBILITY = 3
    HIGH_VISIBILITY = 4
    HIGHEST_VISIBILITY = 5


class InflowType(Enum):
    NO_INFLOW = 0
    IMPERVIOUS_SURFACE = 1
    SURFACE = 2


class OffOrStandard(Enum):
    OFF = 0
    STANDARD = 1


class FrictionShallowWaterDepthCorrection(Enum):
    OFF = 0
    MAX_AVERAGE_CHANNEL_BASED = 1
    LINEARIZED = 2
    LINEARIZED_WEIGHTED_AVERAGED = 3


class LimiterSlopeXArea(Enum):
    OFF = 0
    HIGHER_ORDER_SCHEME = 1
    UPWIND = 2
    DEPTH_DEPENDED = 3


class IntegrationMethod(Enum):
    EULER_IMPLICIT = 0


class ControlType(Enum):
    memory = "memory"
    table = "table"


class StructureControlTypes(Enum):
    pumpstation = "v2_pumpstation"
    pipe = "v2_pipe"
    orifice = "v2_orifice"
    culvert = "v2_culvert"
    weir = "v2_weir"
    channel = "v2_channel"


class ControlTableActionTypes(Enum):
    set_discharge_coefficients = "set_discharge_coefficients"  # not pump
    set_crest_level = "set_crest_level"  # orifice, weir only
    set_pump_capacity = "set_pump_capacity"  # only pump, in API: set_pump_capacity
    set_capacity = "set_capacity"  # old form, mapped to set_pump_capacity


class MeasureLocationContentTypes(Enum):
    v2_connection_nodes = "v2_connection_nodes"  # in API: v2_connection_node (singular)
    # pipe = "v2_pipe"  # --> line cnode a-b
    # orifice = "v2_orifice"  # --> line cnode a-b
    # culvert = "v2_culvert"  # --> line cnode a-b
    # channel = "v2_channel"  # --> line cnode a-b
    # weir = "v2_weir"  # --> line cnode a-b


class MeasureVariables(Enum):
    waterlevel = "waterlevel"  # in API: "s1"
    volume = "volume"  # in API: "vol1"
    discharge = "discharge"  # in API: "q"
    velocity = "velocity"  # in API: "u1"


class MeasureOperators(Enum):
    greater_than = ">"
    greater_than_equal = ">="
    less_than = "<"
    less_than_equal = "<="
