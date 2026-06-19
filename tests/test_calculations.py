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


def test_hydrostatic_pressure_placeholder():
    """
    Example test structure for Step 2.
    Once calculate_hydrostatic_pressure() is implemented, replace this
    with a real assertion, e.g.:

        result = mud_engine.calculate_hydrostatic_pressure(1200, 3000)
        expected = 1200 * 9.81 * 3000
        assert result == pytest.approx(expected, rel=1e-3)
    """
    with pytest.raises(NotImplementedError):
        mud_engine.calculate_hydrostatic_pressure(1200, 3000)


# TODO (Step 2): test_safe_mud_window_flags_underbalanced()
# TODO (Step 2): test_safe_mud_window_flags_overbalanced()
# TODO (Step 3): test_bingham_plastic_shear_stress()
# TODO (Step 4): test_annular_pressure_drop()
# TODO (Step 4): test_ecd_calculation()
# TODO (Step 5): test_annular_volume_matches_hand_calc()
# TODO (Step 6): test_additive_recommendation_by_temperature()
# TODO (Step 7): test_plug_bumping_pressure()
