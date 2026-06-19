"""
mud_engine.py
=============
Drilling Fluids & Rheology Engine — PyMudCement-Optima

Responsible for:
    1. Hydrostatic pressure & mud weight safety window calculations (Step 2)
    2. Mud report parsing & Bingham-Plastic rheology modelling (Step 3)

Author(s):  <add your group member name(s) here>
Course:     PENG 258 - Drilling Engineering 1
"""

# Standard gravity used throughout the suite (m/s^2)
GRAVITY = 9.81


def calculate_hydrostatic_pressure(mud_density_kg_m3: float, tvd_m: float) -> float:
    """
    Calculate hydrostatic pressure exerted by a column of drilling fluid.

    Formula:  P_hyd = rho_mud * g * TVD

    Parameters
    ----------
    mud_density_kg_m3 : float
        Mud density in kg/m^3.
    tvd_m : float
        True Vertical Depth in metres.

    Returns
    -------
    float
        Hydrostatic pressure in Pascals (Pa).
    """
    # TODO (Step 2): implement and validate against hand calculation
    raise NotImplementedError("Implement in Step 2")


def check_safe_mud_window(mud_density_kg_m3: float,
                           pore_pressure_gradient: float,
                           fracture_gradient: float) -> dict:
    """
    Check whether a proposed mud weight falls within the safe operating
    window (i.e. above pore pressure, below fracture gradient).

    Parameters
    ----------
    mud_density_kg_m3 : float
        Proposed mud density.
    pore_pressure_gradient : float
        Formation pore pressure gradient (same units as mud density equivalent).
    fracture_gradient : float
        Formation fracture gradient.

    Returns
    -------
    dict
        {
            "is_safe": bool,
            "message": str
        }
    """
    # TODO (Step 2): implement safety window logic + warning messages
    raise NotImplementedError("Implement in Step 2")


def calculate_shear_stress(yield_point_pa: float,
                            plastic_viscosity_pa_s: float,
                            shear_rate_s1: float) -> float:
    """
    Bingham-Plastic Model: tau = YP + PV * gamma

    Parameters
    ----------
    yield_point_pa : float
        Yield Point (YP) in Pa.
    plastic_viscosity_pa_s : float
        Plastic Viscosity (PV) in Pa.s.
    shear_rate_s1 : float
        Shear rate in s^-1.

    Returns
    -------
    float
        Shear stress (tau) in Pa.
    """
    # TODO (Step 3): implement and validate
    raise NotImplementedError("Implement in Step 3")


def parse_mud_report(report_data: dict) -> dict:
    """
    Parse a digital mud report (dict from CSV/Excel/manual entry) and
    extract key rheological properties.

    Expected keys in report_data (example):
        {
            "PV": float,   # Plastic Viscosity (cP)
            "YP": float,   # Yield Point (lb/100ft^2)
            "mud_weight": float,
            ...
        }

    Returns
    -------
    dict
        Cleaned/validated rheology properties.
    """
    # TODO (Step 3): implement parsing + unit conversions
    raise NotImplementedError("Implement in Step 3")
