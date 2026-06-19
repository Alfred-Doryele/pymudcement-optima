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
from modules import mud_engine


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
# Step 3 placeholders (not yet implemented)
# ---------------------------------------------------------------------------

def test_shear_stress_not_yet_implemented():
    with pytest.raises(NotImplementedError):
        mud_engine.calculate_shear_stress(5, 0.02, 100)


def test_parse_mud_report_not_yet_implemented():
    with pytest.raises(NotImplementedError):
        mud_engine.parse_mud_report({"PV": 20, "YP": 15})


# TODO (Step 4): test_annular_pressure_drop()
# TODO (Step 4): test_ecd_calculation()
# TODO (Step 5): test_annular_volume_matches_hand_calc()
# TODO (Step 6): test_additive_recommendation_by_temperature()
# TODO (Step 7): test_plug_bumping_pressure()