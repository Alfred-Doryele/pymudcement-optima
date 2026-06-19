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

# --- Oilfield -> SI unit conversion constants -------------------------------
# Plastic Viscosity is conventionally reported in centipoise (cP).
#   1 cP = 0.001 Pa.s
CP_TO_PA_S = 0.001

# Yield Point is conventionally reported in lb/100ft^2 (lbf per 100 sq ft).
#   1 lb/100ft^2 = 0.4788 Pa
LB_100FT2_TO_PA = 0.4788


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
        Yield Point (YP) in Pa. Must be >= 0.
    plastic_viscosity_pa_s : float
        Plastic Viscosity (PV) in Pa.s. Must be >= 0.
    shear_rate_s1 : float
        Shear rate in s^-1. Must be >= 0.

    Returns
    -------
    float
        Shear stress (tau) in Pa.

    Raises
    ------
    ValueError
        If any input is negative.

    Example
    -------
    >>> # YP = 5 Pa, PV = 0.02 Pa.s, shear rate = 100 s^-1
    >>> calculate_shear_stress(5, 0.02, 100)
    7.0
    """
    if yield_point_pa < 0:
        raise ValueError("Yield Point (YP) cannot be negative.")
    if plastic_viscosity_pa_s < 0:
        raise ValueError("Plastic Viscosity (PV) cannot be negative.")
    if shear_rate_s1 < 0:
        raise ValueError("Shear rate cannot be negative.")

    tau_pa = yield_point_pa + (plastic_viscosity_pa_s * shear_rate_s1)
    return tau_pa


def parse_mud_report(report_data: dict) -> dict:
    """
    Parse a digital mud report (dict from CSV/Excel/manual entry) and
    extract key rheological properties, converting from conventional
    oilfield units into SI units used by the rest of the engine.

    Expected keys in report_data:
        {
            "PV": float,           # Plastic Viscosity, in centipoise (cP)
            "YP": float,           # Yield Point, in lb/100ft^2
            "mud_weight": float,   # Mud weight, in kg/m^3 (already SI)
        }

    Unit conversions applied:
        PV (cP)         -> PV (Pa.s)   : multiply by 0.001
        YP (lb/100ft^2)  -> YP (Pa)     : multiply by 0.4788

    Parameters
    ----------
    report_data : dict
        Raw mud report values. Must contain "PV" and "YP" keys.
        "mud_weight" is optional but passed through if present.

    Returns
    -------
    dict
        {
            "PV_cP": float,                # original, unconverted
            "YP_lb_100ft2": float,         # original, unconverted
            "PV_pa_s": float,              # converted to Pa.s
            "YP_pa": float,                # converted to Pa
            "mud_weight_kg_m3": float | None,
            "fluid_type": str,             # classification, see below
        }

    Raises
    ------
    ValueError
        If "PV" or "YP" keys are missing, or if their values are negative.

    Notes
    -----
    Fluid classification (a simple sanity-check heuristic, not a rigorous
    rheological classification):
        - YP/PV ratio > 1.0  -> "Highly Shear-Thinning (good hole cleaning)"
        - 0.5 <= YP/PV <= 1.0 -> "Normal Drilling Fluid"
        - YP/PV < 0.5         -> "Low Gel Strength (review hole cleaning capacity)"
        - PV == 0             -> "Undefined (PV is zero)"

    Example
    -------
    >>> parse_mud_report({"PV": 20, "YP": 15, "mud_weight": 1250})["PV_pa_s"]
    0.02
    """
    if "PV" not in report_data or "YP" not in report_data:
        raise ValueError(
            "Mud report must contain both 'PV' (Plastic Viscosity, cP) "
            "and 'YP' (Yield Point, lb/100ft^2) keys."
        )

    pv_cp = report_data["PV"]
    yp_lb = report_data["YP"]

    if pv_cp < 0:
        raise ValueError("PV (Plastic Viscosity) cannot be negative.")
    if yp_lb < 0:
        raise ValueError("YP (Yield Point) cannot be negative.")

    pv_pa_s = pv_cp * CP_TO_PA_S
    yp_pa = yp_lb * LB_100FT2_TO_PA

    if pv_cp == 0:
        fluid_type = "Undefined (PV is zero)"
    else:
        ratio = yp_lb / pv_cp
        if ratio > 1.0:
            fluid_type = "Highly Shear-Thinning (good hole cleaning)"
        elif ratio >= 0.5:
            fluid_type = "Normal Drilling Fluid"
        else:
            fluid_type = "Low Gel Strength (review hole cleaning capacity)"

    return {
        "PV_cP": pv_cp,
        "YP_lb_100ft2": yp_lb,
        "PV_pa_s": pv_pa_s,
        "YP_pa": yp_pa,
        "mud_weight_kg_m3": report_data.get("mud_weight"),
        "fluid_type": fluid_type,
    }