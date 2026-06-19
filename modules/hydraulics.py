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


def calculate_annular_pressure_drop(plastic_viscosity_pa_s: float,
                                     yield_point_pa: float,
                                     flow_rate_m3_s: float,
                                     hole_diameter_m: float,
                                     pipe_od_m: float,
                                     length_m: float) -> float:
    """
    Calculate annular pressure drop for a Bingham-Plastic fluid in
    laminar/turbulent annular flow.

    Returns
    -------
    float
        Pressure drop in Pascals (Pa).
    """
    # TODO (Step 4): implement Bingham-Plastic annular flow equations
    raise NotImplementedError("Implement in Step 4")


def calculate_ecd(mud_weight_kg_m3: float,
                   annular_pressure_drop_pa: float,
                   tvd_m: float) -> float:
    """
    Calculate Equivalent Circulating Density (ECD).

    ECD = mud_weight + (annular_pressure_drop / (g * TVD))   [consistent SI units]

    Returns
    -------
    float
        ECD expressed in kg/m^3 (convertible to ppg/sg in the GUI layer).
    """
    # TODO (Step 4): implement + add fracture gradient warning check
    raise NotImplementedError("Implement in Step 4")
