"""
pa_plugs.py
===========
Plug Bumping Pressure & Plug and Abandonment (P&A) Module — PyMudCement-Optima

Responsible for:
    - Plug bumping pressure calculations
    - Cement plug design for side-tracking, well suspension, P&A (Step 7)

Author(s):  <add your group member name(s) here>
Course:     PENG 258 - Drilling Engineering 1
"""


def calculate_plug_bumping_pressure(displacement_pressure_pa: float,
                                     friction_losses_pa: float,
                                     hydrostatic_differential_pa: float) -> float:
    """
    Calculate the plug bumping pressure to establish safe operational
    limits for the rig crew.

    Returns
    -------
    float
        Plug bumping pressure in Pascals (Pa).
    """
    # TODO (Step 7): implement and validate
    raise NotImplementedError("Implement in Step 7")


def design_pa_plug(hole_diameter_m: float,
                    plug_length_m: float,
                    purpose: str = "P&A") -> dict:
    """
    Design a cement plug for open-hole side-tracking, well suspension,
    or plug and abandonment (P&A) operations.

    Parameters
    ----------
    purpose : str
        One of "side_track", "suspension", "P&A".

    Returns
    -------
    dict
        {
            "plug_volume_m3": float,
            "recommended_length_m": float,
            "notes": str
        }
    """
    # TODO (Step 7): implement design rules per purpose
    raise NotImplementedError("Implement in Step 7")
