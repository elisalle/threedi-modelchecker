VIEWS_TO_DELETE = ["v2_crosssection_view", "v2_pipe_map_view", "v2_imp_surface_view"]
ALL_VIEWS = {
    "v2_1d_lateral_view": {
        "definition": "SELECT a.rowid AS rowid, a.id AS id, a.connection_node_id AS connection_node_id, a.timeseries AS timeseries, b.the_geom FROM v2_1d_lateral a JOIN v2_connection_nodes b ON a.connection_node_id = b.id",
        "view_geometry": "the_geom",
        "view_rowid": "connection_node_id",
        "f_table_name": "v2_connection_nodes",
        "f_geometry_column": "the_geom",
    },
    "v2_1d_boundary_conditions_view": {
        "definition": "SELECT a.rowid AS rowid, a.id AS id, a.connection_node_id AS connection_node_id, a.boundary_type AS boundary_type, a.timeseries AS timeseries, b.the_geom FROM v2_1d_boundary_conditions a JOIN v2_connection_nodes b ON a.connection_node_id = b.id",
        "view_geometry": "the_geom",
        "view_rowid": "connection_node_id",
        "f_table_name": "v2_connection_nodes",
        "f_geometry_column": "the_geom",
    },
    "v2_cross_section_location_view": {
        "definition": "SELECT loc.rowid as rowid, loc.id as loc_id, loc.code as loc_code, loc.reference_level as loc_reference_level, loc.bank_level as loc_bank_level, loc.friction_type as loc_friction_type, loc.friction_value as loc_friction_value, loc.definition_id as loc_definition_id, loc.channel_id as loc_channel_id, loc.the_geom as the_geom, def.id as def_id, def.shape as def_shape, def.width as def_width, def.code as def_code, def.height as def_height FROM v2_cross_section_location loc, v2_cross_section_definition def WHERE loc.definition_id = def.id",
        "view_geometry": "the_geom",
        "view_rowid": "rowid",
        "f_table_name": "v2_cross_section_location",
        "f_geometry_column": "the_geom",
    },
    "v2_cross_section_view": {
        "definition": "SELECT def.rowid AS rowid, def.id AS def_id, def.shape AS def_shape, def.width AS def_width, def.height AS def_height, def.code AS def_code, l.id AS l_id, l.channel_id AS l_channel_id, l.definition_id AS l_definition_id, l.reference_level AS l_reference_level, l.friction_type AS l_friction_type, l.friction_value AS l_friction_value, l.bank_level AS l_bank_level, l.code AS l_code, l.the_geom AS the_geom, ch.id AS ch_id, ch.display_name AS ch_display_name, ch.code AS ch_code, ch.calculation_type AS ch_calculation_type, ch.dist_calc_points AS ch_dist_calc_points, ch.zoom_category AS ch_zoom_category, ch.connection_node_start_id AS ch_connection_node_start_id, ch.connection_node_end_id AS ch_connection_node_end_id FROM v2_cross_section_definition AS def , v2_cross_section_location AS l , v2_channel AS ch WHERE l.definition_id = def.id AND l.channel_id = ch.id",
        "view_geometry": "the_geom",
        "view_rowid": "rowid",
        "f_table_name": "v2_cross_section_location",
        "f_geometry_column": "the_geom",
    },
    "v2_culvert_view": {
        "definition": "SELECT cul.rowid AS rowid, cul.id AS cul_id, cul.display_name AS cul_display_name, cul.code AS cul_code, cul.calculation_type AS cul_calculation_type, cul.friction_value AS cul_friction_value, cul.friction_type AS cul_friction_type, cul.dist_calc_points AS cul_dist_calc_points, cul.zoom_category AS cul_zoom_category, cul.cross_section_definition_id AS cul_cross_section_definition_id, cul.discharge_coefficient_positive AS cul_discharge_coefficient_positive, cul.discharge_coefficient_negative AS cul_discharge_coefficient_negative, cul.invert_level_start_point AS cul_invert_level_start_point, cul.invert_level_end_point AS cul_invert_level_end_point, cul.the_geom AS the_geom, cul.connection_node_start_id AS cul_connection_node_start_id, cul.connection_node_end_id AS cul_connection_node_end_id, def.id AS def_id, def.shape AS def_shape, def.width AS def_width, def.height AS def_height, def.code AS def_code FROM v2_culvert AS cul , v2_cross_section_definition AS def WHERE cul.cross_section_definition_id = def.id",
        "view_geometry": "the_geom",
        "view_rowid": "rowid",
        "f_table_name": "v2_culvert",
        "f_geometry_column": "the_geom",
    },
    "v2_manhole_view": {
        "definition": "SELECT manh.rowid AS rowid, manh.id AS manh_id, manh.display_name AS manh_display_name, manh.code AS manh_code, manh.connection_node_id AS manh_connection_node_id, manh.shape AS manh_shape, manh.width AS manh_width, manh.length AS manh_length, manh.manhole_indicator AS manh_manhole_indicator, manh.calculation_type AS manh_calculation_type, manh.bottom_level AS manh_bottom_level, manh.surface_level AS manh_surface_level, manh.drain_level AS manh_drain_level, manh.sediment_level AS manh_sediment_level, manh.zoom_category AS manh_zoom_category, node.id AS node_id, node.storage_area AS node_storage_area, node.initial_waterlevel AS node_initial_waterlevel, node.code AS node_code, node.the_geom AS the_geom, node.the_geom_linestring AS node_the_geom_linestring FROM v2_manhole AS manh , v2_connection_nodes AS node WHERE manh.connection_node_id = node.id",
        "view_geometry": "the_geom",
        "view_rowid": "rowid",
        "f_table_name": "v2_connection_nodes",
        "f_geometry_column": "the_geom",
    },
    "v2_orifice_view": {
        "definition": "SELECT orf.rowid AS rowid, orf.id AS orf_id, orf.display_name AS orf_display_name, orf.code AS orf_code, orf.crest_level AS orf_crest_level, orf.sewerage AS orf_sewerage, orf.cross_section_definition_id AS orf_cross_section_definition_id, orf.friction_value AS orf_friction_value, orf.friction_type AS orf_friction_type, orf.discharge_coefficient_positive AS orf_discharge_coefficient_positive, orf.discharge_coefficient_negative AS orf_discharge_coefficient_negative, orf.zoom_category AS orf_zoom_category, orf.crest_type AS orf_crest_type, orf.connection_node_start_id AS orf_connection_node_start_id, orf.connection_node_end_id AS orf_connection_node_end_id, def.id AS def_id, def.shape AS def_shape, def.width AS def_width, def.height AS def_height, def.code AS def_code, MakeLine( start_node.the_geom, end_node.the_geom) AS the_geom FROM v2_orifice AS orf, v2_cross_section_definition AS def, v2_connection_nodes AS start_node, v2_connection_nodes AS end_node where orf.connection_node_start_id = start_node.id AND orf.connection_node_end_id = end_node.id AND orf.cross_section_definition_id = def.id",
        "view_geometry": "the_geom",
        "view_rowid": "rowid",
        "f_table_name": "v2_connection_nodes",
        "f_geometry_column": "the_geom_linestring",
    },
    "v2_pipe_view": {
        "definition": "SELECT pipe.rowid AS rowid, pipe.id AS pipe_id, pipe.display_name AS pipe_display_name, pipe.code AS pipe_code, pipe.profile_num AS pipe_profile_num, pipe.sewerage_type AS pipe_sewerage_type, pipe.calculation_type AS pipe_calculation_type, pipe.invert_level_start_point AS pipe_invert_level_start_point, pipe.invert_level_end_point AS pipe_invert_level_end_point, pipe.cross_section_definition_id AS pipe_cross_section_definition_id, pipe.friction_value AS pipe_friction_value, pipe.friction_type AS pipe_friction_type, pipe.dist_calc_points AS pipe_dist_calc_points, pipe.material AS pipe_material, pipe.original_length AS pipe_original_length, pipe.zoom_category AS pipe_zoom_category, pipe.connection_node_start_id AS pipe_connection_node_start_id, pipe.connection_node_end_id AS pipe_connection_node_end_id, def.id AS def_id, def.shape AS def_shape, def.width AS def_width, def.height AS def_height, def.code AS def_code, MakeLine( start_node.the_geom, end_node.the_geom) AS the_geom FROM v2_pipe AS pipe , v2_cross_section_definition AS def , v2_connection_nodes AS start_node , v2_connection_nodes AS end_node WHERE pipe.connection_node_start_id = start_node.id AND pipe.connection_node_end_id = end_node.id AND pipe.cross_section_definition_id = def.id",
        "view_geometry": "the_geom",
        "view_rowid": "rowid",
        "f_table_name": "v2_connection_nodes",
        "f_geometry_column": "the_geom_linestring",
    },
    "v2_pumpstation_point_view": {
        "definition": "SELECT a.rowid AS rowid, a.id AS pump_id, a.display_name, a.code, a.classification, a.sewerage, a.start_level, a.lower_stop_level, a.upper_stop_level, a.capacity, a.zoom_category, a.connection_node_start_id, a.connection_node_end_id, a.type, b.id AS connection_node_id, b.storage_area, b.the_geom FROM v2_pumpstation a JOIN v2_connection_nodes b ON a.connection_node_start_id = b.id",
        "view_geometry": "the_geom",
        "view_rowid": "connection_node_start_id",
        "f_table_name": "v2_connection_nodes",
        "f_geometry_column": "the_geom",
    },
    "v2_pumpstation_view": {
        "definition": "SELECT pump.rowid AS rowid, pump.id AS pump_id, pump.display_name AS pump_display_name, pump.code AS pump_code, pump.classification AS pump_classification, pump.type AS pump_type, pump.sewerage AS pump_sewerage, pump.start_level AS pump_start_level, pump.lower_stop_level AS pump_lower_stop_level, pump.upper_stop_level AS pump_upper_stop_level, pump.capacity AS pump_capacity, pump.zoom_category AS pump_zoom_category, pump.connection_node_start_id AS pump_connection_node_start_id, pump.connection_node_end_id AS pump_connection_node_end_id, MakeLine( start_node.the_geom, end_node.the_geom ) AS the_geom FROM v2_pumpstation AS pump , v2_connection_nodes AS start_node , v2_connection_nodes AS end_node WHERE pump.connection_node_start_id = start_node.id AND pump.connection_node_end_id = end_node.id",
        "view_geometry": "the_geom",
        "view_rowid": "rowid",
        "f_table_name": "v2_connection_nodes",
        "f_geometry_column": "the_geom_linestring",
    },
    "v2_weir_view": {
        "definition": "SELECT weir.rowid AS rowid, weir.id AS weir_id, weir.display_name AS weir_display_name, weir.code AS weir_code, weir.crest_level AS weir_crest_level, weir.crest_type AS weir_crest_type, weir.cross_section_definition_id AS weir_cross_section_definition_id, weir.sewerage AS weir_sewerage, weir.discharge_coefficient_positive AS weir_discharge_coefficient_positive, weir.discharge_coefficient_negative AS weir_discharge_coefficient_negative, weir.external AS weir_external, weir.zoom_category AS weir_zoom_category, weir.friction_value AS weir_friction_value, weir.friction_type AS weir_friction_type, weir.connection_node_start_id AS weir_connection_node_start_id, weir.connection_node_end_id AS weir_connection_node_end_id, def.id AS def_id, def.shape AS def_shape, def.width AS def_width, def.height AS def_height, def.code AS def_code, MakeLine( start_node.the_geom, end_node.the_geom) AS the_geom FROM v2_weir AS weir , v2_cross_section_definition AS def , v2_connection_nodes AS start_node , v2_connection_nodes AS end_node WHERE weir.connection_node_start_id = start_node.id AND weir.connection_node_end_id = end_node.id AND weir.cross_section_definition_id = def.id",
        "view_geometry": "the_geom",
        "view_rowid": "rowid",
        "f_table_name": "v2_connection_nodes",
        "f_geometry_column": "the_geom_linestring",
    },
}
