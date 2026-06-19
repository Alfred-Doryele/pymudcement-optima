"""
cement_engine.py
================
Cement Volumetrics Engine — PyMudCement-Optima

Responsible for:
    - Annular volume calculations for slurry, spacer, flush, displacement (Step 5)

Author(s):  <add your group member name(s) here>
Course:     PENG 258 - Drilling Engineering 1
"""

import math


def calculate_annular_volume(hole_diameter_m: float,
                              casing_od_m: float,
                              length_m: float,
                              excess_factor: float = 0.15) -> float:
    """
    Annular volume for cementing.

    Formula:
        V_ann = (pi/4) * (Dhole^2 - Dcasing_od^2) * L * (1 + We)

    Parameters
    ----------
    hole_diameter_m : float
        Open hole diameter (m).
    casing_od_m : float
        Casing outer diameter (m).
    length_m : float
        Length of cemented interval (m).
    excess_factor : float
        Open-hole excess/washout factor (default 0.15 = 15%).

    Returns
    -------
    float
        Annular volume in cubic metres (m^3).
    """
    # TODO (Step 5): implement and validate against hand calculation
    raise NotImplementedError("Implement in Step 5")


def calculate_slurry_volumes(annular_volume_m3: float,
                              lead_slurry_fraction: float,
                              tail_slurry_fraction: float) -> dict:
    """
    Split total annular volume into lead and tail slurry volumes.

    Returns
    -------
    dict
        {"lead_volume_m3": float, "tail_volume_m3": float}
    """
    # TODO (Step 5): implement
    raise NotImplementedError("Implement in Step 5")


def calculate_displacement_volume(casing_id_m: float, length_m: float) -> float:
    """
    Calculate displacement fluid volume (inside the casing string).

    Returns
    -------
    float
        Displacement volume in m^3.
    """
    # TODO (Step 5): implement
    raise NotImplementedError("Implement in Step 5")
