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
from modules import mud_engine, hydraulics


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


# TODO (Step 5): test_annular_volume_matches_hand_calc()
# TODO (Step 6): test_additive_recommendation_by_temperature()
# TODO (Step 7): test_plug_bumping_pressure()