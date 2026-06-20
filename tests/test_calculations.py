"""
test_calculations.py
=====================
Unit tests for PyMudCement-Optima engineering calculations.

Run with:
    pytest tests/ -v

As each module function is implemented (Steps 2-7), add a corresponding
test here with a hand-calculated expected value. This file is also useful
evidence for the "Mathematical Validation" section of your technical report.
"""

import pytest
from modules import mud_engine, hydraulics, cement_engine, cement_db


# ---------------------------------------------------------------------------
# Step 2: calculate_hydrostatic_pressure()
# ---------------------------------------------------------------------------

def test_hydrostatic_pressure_hand_calculation():
    """
    Hand calculation reference (cite this in your technical report):

        rho_mud = 1200 kg/m^3
        g       = 9.81 m/s^2
        TVD     = 3000 m

        P_hyd = rho_mud * g * TVD
              = 1200 * 9.81 * 3000
              = 35,316,000 Pa
              = 35.316 MPa
    """
    result = mud_engine.calculate_hydrostatic_pressure(1200, 3000)
    expected = 35316000.0
    assert result == pytest.approx(expected, rel=1e-6)


def test_hydrostatic_pressure_zero_depth():
    """At surface (TVD = 0), hydrostatic pressure must be zero."""
    result = mud_engine.calculate_hydrostatic_pressure(1200, 0)
    assert result == pytest.approx(0.0)


def test_hydrostatic_pressure_rejects_negative_density():
    with pytest.raises(ValueError):
        mud_engine.calculate_hydrostatic_pressure(-100, 3000)


def test_hydrostatic_pressure_rejects_negative_depth():
    with pytest.raises(ValueError):
        mud_engine.calculate_hydrostatic_pressure(1200, -50)


def test_hydrostatic_pressure_rejects_zero_density():
    with pytest.raises(ValueError):
        mud_engine.calculate_hydrostatic_pressure(0, 3000)


# ---------------------------------------------------------------------------
# Step 2: check_safe_mud_window()
# ---------------------------------------------------------------------------

def test_safe_mud_window_flags_underbalanced():
    """
    Mud weight (1100) below pore pressure gradient (1150) -> dangerous
    underbalanced condition, risk of well-control kick.
    """
    result = mud_engine.check_safe_mud_window(1100, 1150, 1450)
    assert result["is_safe"] is False
    assert result["status"] == "UNDERBALANCED"


def test_safe_mud_window_flags_overbalanced():
    """
    Mud weight (1500) above fracture gradient (1450) -> dangerous
    overbalanced condition, risk of lost circulation / formation breakdown.
    """
    result = mud_engine.check_safe_mud_window(1500, 1150, 1450)
    assert result["is_safe"] is False
    assert result["status"] == "OVERBALANCED_RISK"


def test_safe_mud_window_accepts_safe_value():
    """
    Mud weight (1250) comfortably within [1150, 1450] window with
    adequate trip margin -> SAFE.
    """
    result = mud_engine.check_safe_mud_window(1250, 1150, 1450)
    assert result["is_safe"] is True
    assert result["status"] == "SAFE"


def test_safe_mud_window_warns_on_thin_trip_margin():
    """
    Mud weight (1160) is technically inside the window but the margin
    above pore pressure (10 kg/m^3) is below the default 30 kg/m^3
    safety margin -> flagged as is_safe=True but with a CAUTION status.
    """
    result = mud_engine.check_safe_mud_window(1160, 1150, 1450)
    assert result["is_safe"] is True
    assert result["status"] == "OVERBALANCED_RISK"
    assert result["margin_to_pore_kg_m3"] == pytest.approx(10.0)


def test_safe_mud_window_rejects_invalid_formation_window():
    """Pore pressure gradient must always be less than fracture gradient."""
    with pytest.raises(ValueError):
        mud_engine.check_safe_mud_window(1200, 1450, 1150)


def test_safe_mud_window_rejects_negative_inputs():
    with pytest.raises(ValueError):
        mud_engine.check_safe_mud_window(-1, 1150, 1450)


# ---------------------------------------------------------------------------
# Step 3: calculate_shear_stress()
# ---------------------------------------------------------------------------

def test_shear_stress_hand_calculation():
    """
    Hand calculation reference (cite this in your technical report):

        YP    = 5 Pa
        PV    = 0.02 Pa.s
        gamma = 100 s^-1

        tau = YP + PV * gamma
            = 5 + (0.02 * 100)
            = 5 + 2
            = 7.0 Pa
    """
    result = mud_engine.calculate_shear_stress(5, 0.02, 100)
    assert result == pytest.approx(7.0, rel=1e-9)


def test_shear_stress_zero_shear_rate_equals_yield_point():
    """At zero shear rate, shear stress should equal the yield point exactly."""
    result = mud_engine.calculate_shear_stress(5, 0.02, 0)
    assert result == pytest.approx(5.0)


def test_shear_stress_rejects_negative_yield_point():
    with pytest.raises(ValueError):
        mud_engine.calculate_shear_stress(-5, 0.02, 100)


def test_shear_stress_rejects_negative_viscosity():
    with pytest.raises(ValueError):
        mud_engine.calculate_shear_stress(5, -0.02, 100)


def test_shear_stress_rejects_negative_shear_rate():
    with pytest.raises(ValueError):
        mud_engine.calculate_shear_stress(5, 0.02, -10)


# ---------------------------------------------------------------------------
# Step 3: parse_mud_report()
# ---------------------------------------------------------------------------

def test_parse_mud_report_unit_conversion():
    """
    Hand calculation reference:

        PV = 20 cP   -> 20 * 0.001  = 0.02 Pa.s
        YP = 15 lb/100ft^2 -> 15 * 0.4788 = 7.182 Pa
    """
    result = mud_engine.parse_mud_report({"PV": 20, "YP": 15, "mud_weight": 1250})
    assert result["PV_pa_s"] == pytest.approx(0.02, rel=1e-9)
    assert result["YP_pa"] == pytest.approx(7.182, rel=1e-6)
    assert result["mud_weight_kg_m3"] == 1250


def test_parse_mud_report_classifies_normal_fluid():
    """YP/PV ratio of 0.75 (15/20) falls in the 'Normal Drilling Fluid' band."""
    result = mud_engine.parse_mud_report({"PV": 20, "YP": 15})
    assert result["fluid_type"] == "Normal Drilling Fluid"


def test_parse_mud_report_classifies_highly_shear_thinning():
    """YP/PV ratio > 1.0 (25/20 = 1.25) -> highly shear-thinning."""
    result = mud_engine.parse_mud_report({"PV": 20, "YP": 25})
    assert result["fluid_type"] == "Highly Shear-Thinning (good hole cleaning)"


def test_parse_mud_report_classifies_low_gel_strength():
    """YP/PV ratio < 0.5 (5/20 = 0.25) -> low gel strength warning."""
    result = mud_engine.parse_mud_report({"PV": 20, "YP": 5})
    assert result["fluid_type"] == "Low Gel Strength (review hole cleaning capacity)"


def test_parse_mud_report_handles_zero_pv():
    """PV = 0 must not raise a ZeroDivisionError; should return 'Undefined'."""
    result = mud_engine.parse_mud_report({"PV": 0, "YP": 10})
    assert result["fluid_type"] == "Undefined (PV is zero)"


def test_parse_mud_report_mud_weight_optional():
    """mud_weight is optional; should be None if not provided."""
    result = mud_engine.parse_mud_report({"PV": 20, "YP": 15})
    assert result["mud_weight_kg_m3"] is None


def test_parse_mud_report_rejects_missing_pv():
    with pytest.raises(ValueError):
        mud_engine.parse_mud_report({"YP": 15})


def test_parse_mud_report_rejects_missing_yp():
    with pytest.raises(ValueError):
        mud_engine.parse_mud_report({"PV": 20})


def test_parse_mud_report_rejects_negative_pv():
    with pytest.raises(ValueError):
        mud_engine.parse_mud_report({"PV": -5, "YP": 15})


def test_parse_mud_report_rejects_negative_yp():
    with pytest.raises(ValueError):
        mud_engine.parse_mud_report({"PV": 10, "YP": -5})


# ---------------------------------------------------------------------------
# Step 4: calculate_annular_velocity()
# ---------------------------------------------------------------------------

def test_annular_velocity_hand_calculation():
    """
    Hand calculation reference:

        Q  = 0.02 m^3/s
        Dh = 0.2159 m (8.5 in hole)
        Dp = 0.127 m  (5 in pipe OD)

        A = (pi/4) * (Dh^2 - Dp^2)
          = (pi/4) * (0.2159^2 - 0.127^2)
          = 0.023942 m^2

        v = Q / A = 0.02 / 0.023942 = 0.83535 m/s
    """
    v = hydraulics.calculate_annular_velocity(0.02, 0.2159, 0.127)
    assert v == pytest.approx(0.83535, rel=1e-3)


def test_annular_velocity_rejects_hole_smaller_than_pipe():
    with pytest.raises(ValueError):
        hydraulics.calculate_annular_velocity(0.01, 0.1, 0.2)


def test_annular_velocity_rejects_negative_flow_rate():
    with pytest.raises(ValueError):
        hydraulics.calculate_annular_velocity(-0.01, 0.2, 0.1)


def test_annular_velocity_rejects_zero_pipe_od():
    with pytest.raises(ValueError):
        hydraulics.calculate_annular_velocity(0.01, 0.2, 0)


# ---------------------------------------------------------------------------
# Step 4: calculate_annular_pressure_drop()
# ---------------------------------------------------------------------------

def test_annular_pressure_drop_hand_calculation():
    """
    Hand calculation reference (laminar Bingham-Plastic annular flow):

        PV = 0.02 Pa.s, YP = 7.182 Pa, Q = 0.005 m^3/s
        Dh = 0.2159 m, Dp = 0.127 m, L = 3000 m

        A = 0.023942 m^2  ->  v = Q/A = 0.20884 m/s
        gap = Dh - Dp = 0.0889 m

        dP_viscous = 12*PV*v*L / gap^2
                   = 12*0.02*0.20884*3000 / 0.0889^2
                   ~ 18,962 Pa  (varies with rounding)

        dP_yield = 2*YP*L / gap
                 = 2*7.182*3000 / 0.0889
                 ~ 484,724 Pa

        Total dP = dP_viscous + dP_yield  ~ 503,750 Pa
    """
    result = hydraulics.calculate_annular_pressure_drop(
        plastic_viscosity_pa_s=0.02,
        yield_point_pa=7.182,
        flow_rate_m3_s=0.005,
        hole_diameter_m=0.2159,
        pipe_od_m=0.127,
        length_m=3000,
    )
    assert result["pressure_drop_pa"] == pytest.approx(503750, rel=1e-3)


def test_annular_pressure_drop_flags_laminar_regime():
    """At low flow rate (0.005 m^3/s), Reynolds Number should fall below
    the critical threshold and be classified LAMINAR."""
    result = hydraulics.calculate_annular_pressure_drop(
        plastic_viscosity_pa_s=0.02,
        yield_point_pa=7.182,
        flow_rate_m3_s=0.005,
        hole_diameter_m=0.2159,
        pipe_od_m=0.127,
        length_m=3000,
        mud_density_kg_m3=1250,
    )
    assert result["flow_regime"] == "LAMINAR"
    assert result["warning"] is None


def test_annular_pressure_drop_flags_turbulent_regime():
    """At a higher flow rate (0.02 m^3/s), Reynolds Number should exceed
    the critical threshold and be classified TURBULENT, with a warning."""
    result = hydraulics.calculate_annular_pressure_drop(
        plastic_viscosity_pa_s=0.02,
        yield_point_pa=7.182,
        flow_rate_m3_s=0.02,
        hole_diameter_m=0.2159,
        pipe_od_m=0.127,
        length_m=3000,
        mud_density_kg_m3=1250,
    )
    assert result["flow_regime"] == "TURBULENT"
    assert result["warning"] is not None


def test_annular_pressure_drop_regime_unknown_without_density():
    """If mud_density_kg_m3 is not supplied, flow regime cannot be assessed."""
    result = hydraulics.calculate_annular_pressure_drop(
        plastic_viscosity_pa_s=0.02,
        yield_point_pa=7.182,
        flow_rate_m3_s=0.005,
        hole_diameter_m=0.2159,
        pipe_od_m=0.127,
        length_m=3000,
    )
    assert result["reynolds_number"] is None
    assert "UNKNOWN" in result["flow_regime"]


def test_annular_pressure_drop_handles_zero_pv_without_crashing():
    """PV = 0 must not raise a ZeroDivisionError in the Reynolds calculation."""
    result = hydraulics.calculate_annular_pressure_drop(
        plastic_viscosity_pa_s=0,
        yield_point_pa=7,
        flow_rate_m3_s=0.01,
        hole_diameter_m=0.2,
        pipe_od_m=0.1,
        length_m=100,
        mud_density_kg_m3=1250,
    )
    assert result["reynolds_number"] == float("inf")
    assert result["flow_regime"] == "TURBULENT"


def test_annular_pressure_drop_rejects_negative_pv():
    with pytest.raises(ValueError):
        hydraulics.calculate_annular_pressure_drop(-0.02, 7, 0.01, 0.2, 0.1, 100)


def test_annular_pressure_drop_rejects_negative_yp():
    with pytest.raises(ValueError):
        hydraulics.calculate_annular_pressure_drop(0.02, -7, 0.01, 0.2, 0.1, 100)


def test_annular_pressure_drop_rejects_negative_length():
    with pytest.raises(ValueError):
        hydraulics.calculate_annular_pressure_drop(0.02, 7, 0.01, 0.2, 0.1, -100)


# ---------------------------------------------------------------------------
# Step 4: calculate_ecd()
# ---------------------------------------------------------------------------

def test_ecd_hand_calculation():
    """
    Hand calculation reference:

        mud_weight = 1250 kg/m^3
        dP         = 503750 Pa  (from laminar pressure drop test above)
        TVD        = 3000 m
        g          = 9.81 m/s^2

        ECD = mud_weight + dP/(g*TVD)
            = 1250 + 503750/(9.81*3000)
            = 1250 + 17.12
            = 1267.12 kg/m^3
    """
    result = hydraulics.calculate_ecd(1250, 503750, 3000)
    assert result["ecd_kg_m3"] == pytest.approx(1267.12, rel=1e-3)


def test_ecd_flags_exceeding_fracture_gradient():
    """A very high pressure drop should push ECD above the fracture gradient."""
    result = hydraulics.calculate_ecd(1250, 50_000_000, 3000, fracture_gradient_kg_m3=1450)
    assert result["exceeds_fracture_gradient"] is True
    assert "WARNING" in result["message"]


def test_ecd_within_fracture_gradient():
    result = hydraulics.calculate_ecd(1250, 503750, 3000, fracture_gradient_kg_m3=1450)
    assert result["exceeds_fracture_gradient"] is False
    assert "OK" in result["message"]


def test_ecd_fracture_gradient_optional():
    """Without a fracture gradient supplied, exceeds_fracture_gradient is None."""
    result = hydraulics.calculate_ecd(1250, 503750, 3000)
    assert result["exceeds_fracture_gradient"] is None


def test_ecd_rejects_zero_mud_weight():
    with pytest.raises(ValueError):
        hydraulics.calculate_ecd(0, 500000, 3000)


def test_ecd_rejects_negative_pressure_drop():
    with pytest.raises(ValueError):
        hydraulics.calculate_ecd(1250, -500000, 3000)


def test_ecd_rejects_zero_tvd():
    with pytest.raises(ValueError):
        hydraulics.calculate_ecd(1250, 500000, 0)


# ---------------------------------------------------------------------------
# Step 5: calculate_annular_volume()
# ---------------------------------------------------------------------------

def test_annular_volume_hand_calculation():
    """
    Hand calculation reference (cite this in your technical report):

        Dhole      = 0.31115 m  (12.25 in open hole)
        Dcasing_OD = 0.24448 m  (9.625 in casing)
        L          = 500 m
        We         = 0.15 (15% excess)

        V_ann = (pi/4) * (Dhole^2 - Dcasing_OD^2) * L * (1 + We)
              = (pi/4) * (0.31115^2 - 0.24448^2) * 500 * 1.15
              ~ 16.729 m^3
    """
    result = cement_engine.calculate_annular_volume(0.31115, 0.24448, 500, 0.15)
    assert result == pytest.approx(16.729, rel=1e-3)


def test_annular_volume_default_excess_factor():
    """Default excess_factor of 0.15 should match an explicit 0.15 call."""
    explicit = cement_engine.calculate_annular_volume(0.31115, 0.24448, 500, 0.15)
    default = cement_engine.calculate_annular_volume(0.31115, 0.24448, 500)
    assert default == pytest.approx(explicit, rel=1e-9)


def test_annular_volume_zero_length_returns_zero():
    result = cement_engine.calculate_annular_volume(0.3, 0.2, 0)
    assert result == pytest.approx(0.0)


def test_annular_volume_rejects_hole_smaller_than_casing():
    with pytest.raises(ValueError):
        cement_engine.calculate_annular_volume(0.2, 0.25, 500)


def test_annular_volume_rejects_zero_casing_od():
    with pytest.raises(ValueError):
        cement_engine.calculate_annular_volume(0.3, 0, 500)


def test_annular_volume_rejects_negative_length():
    with pytest.raises(ValueError):
        cement_engine.calculate_annular_volume(0.3, 0.2, -500)


def test_annular_volume_rejects_negative_excess_factor():
    with pytest.raises(ValueError):
        cement_engine.calculate_annular_volume(0.3, 0.2, 500, -0.1)


# ---------------------------------------------------------------------------
# Step 5: calculate_slurry_volumes()
# ---------------------------------------------------------------------------

def test_slurry_volumes_split_sums_to_total():
    """A 60/40 lead/tail split of a known annular volume should sum back
    to the original total (when fractions sum to 1.0)."""
    v_ann = 16.729
    result = cement_engine.calculate_slurry_volumes(v_ann, 0.6, 0.4)
    assert result["lead_volume_m3"] + result["tail_volume_m3"] == pytest.approx(v_ann, rel=1e-6)
    assert result["unallocated_fraction"] == pytest.approx(0.0, abs=1e-9)
    assert result["warning"] is None


def test_slurry_volumes_hand_calculation():
    """
    Hand calculation reference:

        V_ann = 16.729 m^3, lead = 60%, tail = 40%

        lead_volume = 16.729 * 0.6 = 10.0374 m^3
        tail_volume = 16.729 * 0.4 = 6.6916 m^3
    """
    result = cement_engine.calculate_slurry_volumes(16.729, 0.6, 0.4)
    assert result["lead_volume_m3"] == pytest.approx(10.0374, rel=1e-3)
    assert result["tail_volume_m3"] == pytest.approx(6.6916, rel=1e-3)


def test_slurry_volumes_warns_on_over_allocation():
    """Fractions summing above 1.0 should trigger a warning."""
    result = cement_engine.calculate_slurry_volumes(16.729, 0.7, 0.5)
    assert result["warning"] is not None
    assert "WARNING" in result["warning"]


def test_slurry_volumes_unallocated_fraction_for_partial_split():
    """If lead+tail < 1.0 (e.g. spacer takes the rest), unallocated_fraction
    should reflect the remainder."""
    result = cement_engine.calculate_slurry_volumes(16.729, 0.5, 0.3)
    assert result["unallocated_fraction"] == pytest.approx(0.2, rel=1e-6)
    assert result["warning"] is None


def test_slurry_volumes_rejects_negative_annular_volume():
    with pytest.raises(ValueError):
        cement_engine.calculate_slurry_volumes(-5, 0.5, 0.5)


def test_slurry_volumes_rejects_lead_fraction_above_one():
    with pytest.raises(ValueError):
        cement_engine.calculate_slurry_volumes(10, 1.5, 0.5)


def test_slurry_volumes_rejects_negative_tail_fraction():
    with pytest.raises(ValueError):
        cement_engine.calculate_slurry_volumes(10, 0.5, -0.1)


# ---------------------------------------------------------------------------
# Step 5: calculate_displacement_volume()
# ---------------------------------------------------------------------------

def test_displacement_volume_hand_calculation():
    """
    Hand calculation reference:

        Dcasing_ID = 0.22049 m (8.681 in)
        L          = 3000 m

        V_disp = (pi/4) * Dcasing_ID^2 * L
               = (pi/4) * 0.22049^2 * 3000
               ~ 114.548 m^3
    """
    result = cement_engine.calculate_displacement_volume(0.22049, 3000)
    assert result == pytest.approx(114.548, rel=1e-3)


def test_displacement_volume_zero_length_returns_zero():
    result = cement_engine.calculate_displacement_volume(0.2, 0)
    assert result == pytest.approx(0.0)


def test_displacement_volume_rejects_zero_casing_id():
    with pytest.raises(ValueError):
        cement_engine.calculate_displacement_volume(0, 3000)


def test_displacement_volume_rejects_negative_length():
    with pytest.raises(ValueError):
        cement_engine.calculate_displacement_volume(0.2, -100)


# ---------------------------------------------------------------------------
# Step 6: load_additive_database()
# ---------------------------------------------------------------------------

def test_load_additive_database_returns_list():
    db = cement_db.load_additive_database()
    assert isinstance(db, list)
    assert len(db) > 0


def test_load_additive_database_entries_have_required_keys():
    db = cement_db.load_additive_database()
    required_keys = {"temp_range_c", "additive", "function",
                      "typical_dosage_percent", "estimated_pump_time_min"}
    for entry in db:
        assert required_keys.issubset(entry.keys())


def test_load_additive_database_rejects_missing_file():
    with pytest.raises(FileNotFoundError):
        cement_db.load_additive_database("/nonexistent/path/to/file.json")


def test_load_additive_database_rejects_invalid_json(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{not valid json")
    with pytest.raises(ValueError):
        cement_db.load_additive_database(str(bad_file))


def test_load_additive_database_rejects_missing_additives_key(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text('{"foo": "bar"}')
    with pytest.raises(ValueError):
        cement_db.load_additive_database(str(bad_file))


# ---------------------------------------------------------------------------
# Step 6: recommend_additives()
# ---------------------------------------------------------------------------

def test_recommend_additives_low_temperature_band():
    """BHT = 25C should fall in the [0, 50) band -> Calcium Chloride accelerator."""
    result = cement_db.recommend_additives(25)
    assert result["recommended_additive"] == "Calcium Chloride (Accelerator)"
    assert result["matched_temp_range_c"] == [0, 50]


def test_recommend_additives_mid_temperature_band():
    """BHT = 110C should fall in the [90, 150) band -> Lignosulfonate Retarder."""
    result = cement_db.recommend_additives(110)
    assert result["recommended_additive"] == "Lignosulfonate Retarder"


def test_recommend_additives_high_temperature_band():
    """BHT = 200C should fall in the [150, 250] band -> HTHP Retarder."""
    result = cement_db.recommend_additives(200)
    assert result["recommended_additive"] == "HTHP Retarder (e.g., synthetic copolymer)"


def test_recommend_additives_lower_boundary_goes_to_upper_band():
    """BHT exactly at a boundary (50C) should go to the band starting at
    50, not the band ending at 50 (i.e. bands are [low, high))."""
    result = cement_db.recommend_additives(50)
    assert result["matched_temp_range_c"] == [50, 90]


def test_recommend_additives_at_absolute_upper_limit():
    """BHT exactly at the database's highest value (250C) should still
    match the last band (inclusive at the very top)."""
    result = cement_db.recommend_additives(250)
    assert result["recommended_additive"] == "HTHP Retarder (e.g., synthetic copolymer)"
    assert "WARNING" not in result["notes"]


def test_recommend_additives_flags_extreme_temperature_beyond_database():
    """
    Stress-test scenario (matches syllabus requirement: 'inputting ...
    extreme bottom-hole temperatures to verify the software's warning
    logic'). BHT = 300C exceeds the highest band (250C) and must return
    a clear warning rather than silently returning a value or crashing.
    """
    result = cement_db.recommend_additives(300)
    assert result["recommended_additive"] == "HTHP Retarder (e.g., synthetic copolymer)"
    assert "WARNING" in result["notes"]


def test_recommend_additives_rejects_negative_temperature():
    with pytest.raises(ValueError):
        cement_db.recommend_additives(-10)


def test_recommend_additives_rejects_empty_database():
    with pytest.raises(ValueError):
        cement_db.recommend_additives(50, database=[])


def test_recommend_additives_accepts_preloaded_database():
    """Passing a pre-loaded database should avoid re-reading the file
    and produce the same result as the default auto-load."""
    db = cement_db.load_additive_database()
    result = cement_db.recommend_additives(100, database=db)
    assert result["recommended_additive"] == "Lignosulfonate Retarder"


# TODO (Step 7): test_plug_bumping_pressure()