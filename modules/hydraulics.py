"""
hydraulics.py
=============
Annular Hydraulics & ECD Engine — PyMudCement-Optima

Responsible for:
    - Annular pressure drop calculations for non-Newtonian (Bingham-Plastic) fluids
    - Live Equivalent Circulating Density (ECD) tracking (Step 4)

Author(s):  <add your group member name(s) here>
Course:     PENG 258 - Drilling Engineering 1
"""

import math

GRAVITY = 9.81

# Critical Reynolds Number threshold separating laminar from turbulent
# annular flow for Bingham-Plastic fluids (standard drilling engineering
# value used across SPE literature, e.g. Bourgoyne et al.).
CRITICAL_REYNOLDS_NUMBER = 2100


def calculate_annular_velocity(flow_rate_m3_s: float,
                                hole_diameter_m: float,
                                pipe_od_m: float) -> float:
    """
    Calculate average fluid velocity in the annulus.

    Formula:  v = Q / A_annulus
              A_annulus = (pi/4) * (Dhole^2 - Dpipe_od^2)

    Parameters
    ----------
    flow_rate_m3_s : float
        Volumetric flow rate (m^3/s). Must be > 0.
    hole_diameter_m : float
        Open hole (or casing ID) diameter (m). Must be > pipe_od_m.
    pipe_od_m : float
        Drill pipe/casing outer diameter (m). Must be > 0.

    Returns
    -------
    float
        Average annular velocity (m/s).

    Raises
    ------
    ValueError
        If flow rate <= 0, pipe_od_m <= 0, or hole_diameter_m <= pipe_od_m.
    """
    if flow_rate_m3_s <= 0:
        raise ValueError("Flow rate must be a positive number (m^3/s).")
    if pipe_od_m <= 0:
        raise ValueError("Pipe OD must be a positive number (m).")
    if hole_diameter_m <= pipe_od_m:
        raise ValueError("Hole diameter must be greater than pipe OD (annulus must exist).")

    annular_area = (math.pi / 4) * (hole_diameter_m**2 - pipe_od_m**2)
    velocity = flow_rate_m3_s / annular_area
    return velocity


def calculate_annular_pressure_drop(plastic_viscosity_pa_s: float,
                                     yield_point_pa: float,
                                     flow_rate_m3_s: float,
                                     hole_diameter_m: float,
                                     pipe_od_m: float,
                                     length_m: float,
                                     mud_density_kg_m3: float = None) -> dict:
    """
    Calculate annular pressure drop for a Bingham-Plastic fluid, assuming
    laminar annular flow (the standard regime used for routine ECD and
    hole-cleaning checks at this engineering level).

    Laminar annular pressure drop (Bingham-Plastic model, SI-consistent form):

        dP/dL = [12 * PV * v / (Dh - Dp)^2] + [YP / (Dh - Dp)] * (1/200) ... (field-unit form)

    Implemented here in fully consistent SI units as:

        dP = [ (12 * PV * v * L) / (Dh - Dp)^2 ] + [ (2 * YP * L) / (Dh - Dp) ]

    where:
        PV = Plastic Viscosity (Pa.s)
        YP = Yield Point (Pa)
        v  = average annular velocity (m/s)
        L  = length of annular interval (m)
        Dh = hole diameter (m)
        Dp = pipe OD (m)

    If mud_density_kg_m3 is supplied, a Reynolds Number is also estimated
    to flag whether the flow regime is actually laminar (the formula above
    is only valid for laminar flow; turbulent flow needs a different
    correlation and is flagged rather than silently miscalculated).

    Parameters
    ----------
    plastic_viscosity_pa_s : float
        Plastic Viscosity (Pa.s). Must be >= 0.
    yield_point_pa : float
        Yield Point (Pa). Must be >= 0.
    flow_rate_m3_s : float
        Volumetric flow rate (m^3/s). Must be > 0.
    hole_diameter_m : float
        Open hole diameter (m). Must be > pipe_od_m.
    pipe_od_m : float
        Drill pipe outer diameter (m). Must be > 0.
    length_m : float
        Length of the annular interval (m). Must be >= 0.
    mud_density_kg_m3 : float, optional
        Mud density (kg/m^3), used only to estimate the flow regime.

    Returns
    -------
    dict
        {
            "pressure_drop_pa": float,
            "annular_velocity_m_s": float,
            "reynolds_number": float | None,
            "flow_regime": str,   # "LAMINAR" | "TURBULENT" | "UNKNOWN (density not provided)"
            "warning": str | None
        }

    Raises
    ------
    ValueError
        If any required input is invalid (see calculate_annular_velocity
        and individual parameter checks).

    Example
    -------
    >>> result = calculate_annular_pressure_drop(
    ...     plastic_viscosity_pa_s=0.02, yield_point_pa=7.182,
    ...     flow_rate_m3_s=0.02, hole_diameter_m=0.2159,
    ...     pipe_od_m=0.127, length_m=3000
    ... )
    >>> round(result["pressure_drop_pa"], 1)
    """
    if plastic_viscosity_pa_s < 0:
        raise ValueError("Plastic Viscosity (PV) cannot be negative.")
    if yield_point_pa < 0:
        raise ValueError("Yield Point (YP) cannot be negative.")
    if length_m < 0:
        raise ValueError("Length cannot be negative.")

    # Annular velocity (also validates flow_rate, hole_diameter, pipe_od)
    v = calculate_annular_velocity(flow_rate_m3_s, hole_diameter_m, pipe_od_m)

    gap = hole_diameter_m - pipe_od_m  # hydraulic gap of the annulus (m)

    # Bingham-Plastic laminar annular pressure drop (SI-consistent form)
    dp_viscous = (12 * plastic_viscosity_pa_s * v * length_m) / (gap**2)
    dp_yield = (2 * yield_point_pa * length_m) / gap
    pressure_drop_pa = dp_viscous + dp_yield

    reynolds_number = None
    flow_regime = "UNKNOWN (density not provided)"
    warning = None

    if mud_density_kg_m3 is not None:
        if mud_density_kg_m3 <= 0:
            raise ValueError("Mud density must be a positive number (kg/m^3).")

        # Reynolds Number for Bingham-Plastic annular flow (simplified,
        # generalized form sufficient for regime screening at this level).
        if plastic_viscosity_pa_s > 0:
            reynolds_number = (mud_density_kg_m3 * v * gap) / plastic_viscosity_pa_s
        else:
            reynolds_number = float("inf")

        if reynolds_number <= CRITICAL_REYNOLDS_NUMBER:
            flow_regime = "LAMINAR"
        else:
            flow_regime = "TURBULENT"
            warning = (
                f"Estimated Reynolds Number ({reynolds_number:.0f}) exceeds the "
                f"laminar threshold ({CRITICAL_REYNOLDS_NUMBER}). Flow is likely "
                f"turbulent — the laminar pressure-drop formula used here may "
                f"underestimate the true pressure drop. Treat this result as "
                f"indicative only."
            )

    return {
        "pressure_drop_pa": pressure_drop_pa,
        "annular_velocity_m_s": v,
        "reynolds_number": reynolds_number,
        "flow_regime": flow_regime,
        "warning": warning,
    }


def calculate_ecd(mud_weight_kg_m3: float,
                   annular_pressure_drop_pa: float,
                   tvd_m: float,
                   fracture_gradient_kg_m3: float = None) -> dict:
    """
    Calculate Equivalent Circulating Density (ECD): the effective mud
    density seen by the formation while circulating, accounting for the
    additional friction pressure in the annulus.

    Formula:
        ECD = mud_weight + (annular_pressure_drop / (g * TVD))

    Parameters
    ----------
    mud_weight_kg_m3 : float
        Static mud weight (kg/m^3). Must be > 0.
    annular_pressure_drop_pa : float
        Annular friction pressure drop (Pa), e.g. from
        calculate_annular_pressure_drop(). Must be >= 0.
    tvd_m : float
        True Vertical Depth (m). Must be > 0 (ECD undefined at surface).
    fracture_gradient_kg_m3 : float, optional
        Formation fracture gradient as Equivalent Mud Weight (kg/m^3).
        If supplied, the result flags whether ECD exceeds it (risk of
        induced lost circulation / formation breakdown while circulating).

    Returns
    -------
    dict
        {
            "ecd_kg_m3": float,
            "exceeds_fracture_gradient": bool | None,
            "message": str
        }

    Raises
    ------
    ValueError
        If mud_weight_kg_m3 <= 0, annular_pressure_drop_pa < 0, or tvd_m <= 0.

    Example
    -------
    >>> calculate_ecd(1250, 500000, 3000)["ecd_kg_m3"]
    1267.0...
    """
    if mud_weight_kg_m3 <= 0:
        raise ValueError("Mud weight must be a positive number (kg/m^3).")
    if annular_pressure_drop_pa < 0:
        raise ValueError("Annular pressure drop cannot be negative.")
    if tvd_m <= 0:
        raise ValueError("TVD must be greater than zero for ECD to be defined.")

    ecd_kg_m3 = mud_weight_kg_m3 + (annular_pressure_drop_pa / (GRAVITY * tvd_m))

    exceeds_fracture_gradient = None
    message = f"ECD = {ecd_kg_m3:.1f} kg/m^3 (static mud weight {mud_weight_kg_m3:.1f} kg/m^3 + circulating friction effect)."

    if fracture_gradient_kg_m3 is not None:
        if fracture_gradient_kg_m3 <= 0:
            raise ValueError("Fracture gradient must be a positive number (kg/m^3).")

        exceeds_fracture_gradient = ecd_kg_m3 > fracture_gradient_kg_m3
        if exceeds_fracture_gradient:
            message = (
                f"WARNING: ECD ({ecd_kg_m3:.1f} kg/m^3) exceeds the fracture "
                f"gradient ({fracture_gradient_kg_m3:.1f} kg/m^3). Risk of induced "
                f"lost circulation while circulating. Consider reducing flow rate "
                f"or mud rheology (PV/YP)."
            )
        else:
            message = (
                f"OK: ECD ({ecd_kg_m3:.1f} kg/m^3) is below the fracture gradient "
                f"({fracture_gradient_kg_m3:.1f} kg/m^3)."
            )

    return {
        "ecd_kg_m3": ecd_kg_m3,
        "exceeds_fracture_gradient": exceeds_fracture_gradient,
        "message": message,
    }