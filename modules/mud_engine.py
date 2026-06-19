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
        Mud density in kg/m^3. Must be > 0.
    tvd_m : float
        True Vertical Depth in metres. Must be >= 0.

    Returns
    -------
    float
        Hydrostatic pressure in Pascals (Pa).

    Raises
    ------
    ValueError
        If mud_density_kg_m3 <= 0 or tvd_m < 0.

    Example
    -------
    >>> calculate_hydrostatic_pressure(1200, 3000)
    35316000.0
    """
    if mud_density_kg_m3 <= 0:
        raise ValueError("Mud density must be a positive number (kg/m^3).")
    if tvd_m < 0:
        raise ValueError("TVD cannot be negative.")

    p_hyd_pa = mud_density_kg_m3 * GRAVITY * tvd_m
    return p_hyd_pa


def check_safe_mud_window(mud_density_kg_m3: float,
                           pore_pressure_gradient_kg_m3: float,
                           fracture_gradient_kg_m3: float,
                           safety_margin_kg_m3: float = 30.0) -> dict:
    """
    Check whether a proposed mud weight falls within the safe operating
    window, i.e. heavy enough to balance pore pressure (avoid a kick/
    well-control event) but light enough to stay below the fracture
    gradient (avoid lost circulation / formation breakdown).

    All three density-like inputs are expressed as Equivalent Mud Weight
    (EMW) in kg/m^3, which is the standard way pore pressure and fracture
    gradients are compared against mud weight in drilling engineering.

    Parameters
    ----------
    mud_density_kg_m3 : float
        Proposed/actual mud density (kg/m^3).
    pore_pressure_gradient_kg_m3 : float
        Formation pore pressure expressed as Equivalent Mud Weight (kg/m^3).
    fracture_gradient_kg_m3 : float
        Formation fracture pressure expressed as Equivalent Mud Weight (kg/m^3).
    safety_margin_kg_m3 : float, optional
        Recommended trip/connection safety margin above pore pressure
        (industry rule of thumb, default 30 kg/m^3 ~ 0.25 ppg).

    Returns
    -------
    dict
        {
            "is_safe": bool,
            "status": str,          # "UNDERBALANCED" | "OVERBALANCED_RISK" | "SAFE"
            "message": str,
            "margin_to_pore_kg_m3": float,
            "margin_to_fracture_kg_m3": float
        }

    Raises
    ------
    ValueError
        If pore_pressure_gradient_kg_m3 >= fracture_gradient_kg_m3
        (a physically inconsistent/invalid formation window), or if any
        density value is <= 0.

    Example
    -------
    >>> check_safe_mud_window(1250, 1150, 1450)["is_safe"]
    True
    >>> check_safe_mud_window(1100, 1150, 1450)["is_safe"]
    False
    """
    for name, value in [
        ("mud_density_kg_m3", mud_density_kg_m3),
        ("pore_pressure_gradient_kg_m3", pore_pressure_gradient_kg_m3),
        ("fracture_gradient_kg_m3", fracture_gradient_kg_m3),
    ]:
        if value <= 0:
            raise ValueError(f"{name} must be a positive number.")

    if pore_pressure_gradient_kg_m3 >= fracture_gradient_kg_m3:
        raise ValueError(
            "Invalid formation window: pore pressure gradient must be "
            "less than fracture gradient."
        )

    margin_to_pore = mud_density_kg_m3 - pore_pressure_gradient_kg_m3
    margin_to_fracture = fracture_gradient_kg_m3 - mud_density_kg_m3

    if mud_density_kg_m3 < pore_pressure_gradient_kg_m3:
        return {
            "is_safe": False,
            "status": "UNDERBALANCED",
            "message": (
                f"DANGER: Mud weight ({mud_density_kg_m3:.1f} kg/m^3) is below "
                f"pore pressure ({pore_pressure_gradient_kg_m3:.1f} kg/m^3). "
                f"Risk of a well-control kick. Increase mud weight immediately."
            ),
            "margin_to_pore_kg_m3": margin_to_pore,
            "margin_to_fracture_kg_m3": margin_to_fracture,
        }

    if mud_density_kg_m3 > fracture_gradient_kg_m3:
        return {
            "is_safe": False,
            "status": "OVERBALANCED_RISK",
            "message": (
                f"DANGER: Mud weight ({mud_density_kg_m3:.1f} kg/m^3) exceeds "
                f"fracture gradient ({fracture_gradient_kg_m3:.1f} kg/m^3). "
                f"Risk of formation breakdown and lost circulation. "
                f"Reduce mud weight immediately."
            ),
            "margin_to_pore_kg_m3": margin_to_pore,
            "margin_to_fracture_kg_m3": margin_to_fracture,
        }

    if margin_to_pore < safety_margin_kg_m3:
        return {
            "is_safe": True,
            "status": "OVERBALANCED_RISK",
            "message": (
                f"CAUTION: Mud weight is within the safe window but the trip "
                f"margin above pore pressure ({margin_to_pore:.1f} kg/m^3) is "
                f"below the recommended {safety_margin_kg_m3:.1f} kg/m^3 safety "
                f"margin. Consider increasing mud weight slightly."
            ),
            "margin_to_pore_kg_m3": margin_to_pore,
            "margin_to_fracture_kg_m3": margin_to_fracture,
        }

    return {
        "is_safe": True,
        "status": "SAFE",
        "message": (
            f"SAFE: Mud weight ({mud_density_kg_m3:.1f} kg/m^3) is within the "
            f"operating window [{pore_pressure_gradient_kg_m3:.1f}, "
            f"{fracture_gradient_kg_m3:.1f}] kg/m^3 with adequate margin."
        ),
        "margin_to_pore_kg_m3": margin_to_pore,
        "margin_to_fracture_kg_m3": margin_to_fracture,
    }


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