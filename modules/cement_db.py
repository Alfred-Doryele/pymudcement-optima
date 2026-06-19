"""
cement_db.py
============
Cement Additive Lookup & Slurry Design — PyMudCement-Optima

Responsible for:
    - Loading the additive database (data/cement_additives.json)
    - Suggesting additives and pump time based on wellbore temperature (Step 6)

Author(s):  <add your group member name(s) here>
Course:     PENG 258 - Drilling Engineering 1
"""

import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "cement_additives.json")


def load_additive_database(path: str = DB_PATH) -> list:
    """
    Load the cement additive lookup table from JSON.

    Returns
    -------
    list of dict
        Each entry describes an additive's applicable temperature range,
        function, and typical dosage.
    """
    # TODO (Step 6): implement file loading + error handling
    raise NotImplementedError("Implement in Step 6")


def recommend_additives(bottom_hole_temp_c: float) -> dict:
    """
    Recommend cement additives and estimate pump time for a given BHT.

    Returns
    -------
    dict
        {
            "recommended_additives": list[str],
            "estimated_pump_time_min": float,
            "notes": str
        }
    """
    # TODO (Step 6): implement lookup logic
    raise NotImplementedError("Implement in Step 6")
