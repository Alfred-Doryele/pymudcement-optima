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
        Open hole diameter (m). Must be > casing_od_m.
    casing_od_m : float
        Casing outer diameter (m). Must be > 0.
    length_m : float
        Length of cemented interval (m). Must be >= 0.
    excess_factor : float
        Open-hole excess/washout factor (default 0.15 = 15%). Must be >= 0.

    Returns
    -------
    float
        Annular volume in cubic metres (m^3).

    Raises
    ------
    ValueError
        If casing_od_m <= 0, hole_diameter_m <= casing_od_m,
        length_m < 0, or excess_factor < 0.

    Example
    -------
    >>> # 12.25 in hole (0.31115 m), 9.625 in casing OD (0.24448 m), 500 m, 15% excess
    >>> calculate_annular_volume(0.31115, 0.24448, 500, 0.15)
    """
    if casing_od_m <= 0:
        raise ValueError("Casing OD must be a positive number (m).")
    if hole_diameter_m <= casing_od_m:
        raise ValueError("Hole diameter must be greater than casing OD (annulus must exist).")
    if length_m < 0:
        raise ValueError("Length cannot be negative.")
    if excess_factor < 0:
        raise ValueError("Excess factor cannot be negative.")

    v_ann_m3 = (math.pi / 4) * (hole_diameter_m**2 - casing_od_m**2) * length_m * (1 + excess_factor)
    return v_ann_m3


def calculate_slurry_volumes(annular_volume_m3: float,
                              lead_slurry_fraction: float,
                              tail_slurry_fraction: float) -> dict:
    """
    Split total annular cement volume into lead and tail slurry volumes
    by fraction.

    In a typical primary cement job, the lower portion of the annulus
    (near the casing shoe) is cemented with a higher-strength, denser
    "tail" slurry, while the upper portion uses a lighter, cheaper "lead"
    slurry. This function performs a simple proportional split of a
    known total annular volume.

    Note: lead_slurry_fraction + tail_slurry_fraction need not sum to
    exactly 1.0 (e.g. if a portion is left for spacer fluid), but a
    warning-style check is applied if the sum exceeds 1.0, since that
    would over-allocate the annular volume.

    Parameters
    ----------
    annular_volume_m3 : float
        Total annular volume to be cemented (m^3), e.g. from
        calculate_annular_volume(). Must be >= 0.
    lead_slurry_fraction : float
        Fraction (0-1) of annular_volume_m3 allocated to lead slurry.
    tail_slurry_fraction : float
        Fraction (0-1) of annular_volume_m3 allocated to tail slurry.

    Returns
    -------
    dict
        {
            "lead_volume_m3": float,
            "tail_volume_m3": float,
            "unallocated_fraction": float,
            "warning": str | None
        }

    Raises
    ------
    ValueError
        If annular_volume_m3 < 0, or either fraction is outside [0, 1].

    Example
    -------
    >>> calculate_slurry_volumes(16.729, 0.6, 0.4)
    {'lead_volume_m3': 10.0374, 'tail_volume_m3': 6.6916, ...}
    """
    if annular_volume_m3 < 0:
        raise ValueError("Annular volume cannot be negative.")
    if not (0 <= lead_slurry_fraction <= 1):
        raise ValueError("lead_slurry_fraction must be between 0 and 1.")
    if not (0 <= tail_slurry_fraction <= 1):
        raise ValueError("tail_slurry_fraction must be between 0 and 1.")

    lead_volume_m3 = annular_volume_m3 * lead_slurry_fraction
    tail_volume_m3 = annular_volume_m3 * tail_slurry_fraction

    total_fraction = lead_slurry_fraction + tail_slurry_fraction
    unallocated_fraction = 1.0 - total_fraction

    warning = None
    if total_fraction > 1.0:
        warning = (
            f"WARNING: lead_slurry_fraction + tail_slurry_fraction = "
            f"{total_fraction:.2f}, which exceeds 1.0 (100% of annular volume). "
            f"Check your fractions — total cement volume is over-allocated."
        )

    return {
        "lead_volume_m3": lead_volume_m3,
        "tail_volume_m3": tail_volume_m3,
        "unallocated_fraction": unallocated_fraction,
        "warning": warning,
    }


def calculate_displacement_volume(casing_id_m: float, length_m: float) -> float:
    """
    Calculate displacement fluid volume: the internal capacity of the
    casing string, which must be displaced with fluid (typically drilling
    mud or water) to push the cement slurry out through the shoe and up
    into the annulus.

    Formula:
        V_disp = (pi/4) * Dcasing_id^2 * L

    Parameters
    ----------
    casing_id_m : float
        Casing inner diameter (m). Must be > 0.
    length_m : float
        Length of casing string to be displaced (m). Must be >= 0.

    Returns
    -------
    float
        Displacement volume in m^3.

    Raises
    ------
    ValueError
        If casing_id_m <= 0 or length_m < 0.

    Example
    -------
    >>> # 8.681 in casing ID (0.22049 m), 3000 m casing string
    >>> calculate_displacement_volume(0.22049, 3000)
    """
    if casing_id_m <= 0:
        raise ValueError("Casing ID must be a positive number (m).")
    if length_m < 0:
        raise ValueError("Length cannot be negative.")

    v_disp_m3 = (math.pi / 4) * (casing_id_m**2) * length_m
    return v_disp_m3