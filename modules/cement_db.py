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

    Parameters
    ----------
    path : str, optional
        Path to the additive database JSON file. Defaults to
        data/cement_additives.json relative to this module.

    Returns
    -------
    list of dict
        Each entry describes an additive's applicable temperature range,
        function, and typical dosage. Format:
        {
            "temp_range_c": [low, high],
            "additive": str,
            "function": str,
            "typical_dosage_percent": str,
            "estimated_pump_time_min": float
        }

    Raises
    ------
    FileNotFoundError
        If the database file does not exist at the given path.
    ValueError
        If the file exists but is not valid JSON, or does not contain
        an "additives" key.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Cement additive database not found at: {path}. "
            f"Ensure data/cement_additives.json exists in the project."
        )

    try:
        with open(path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Cement additive database is not valid JSON: {e}")

    if "additives" not in data:
        raise ValueError("Cement additive database JSON must contain an 'additives' key.")

    return data["additives"]


def recommend_additives(bottom_hole_temp_c: float, database: list = None) -> dict:
    """
    Recommend a cement additive and estimate pump time for a given
    Bottom Hole Temperature (BHT) by matching against the additive
    lookup database.

    Temperature bands in the database are treated as [low, high), i.e.
    inclusive of the lower bound and exclusive of the upper bound,
    except for the highest band which is treated as fully inclusive
    at its upper limit.

    Parameters
    ----------
    bottom_hole_temp_c : float
        Bottom Hole Temperature (°C). Must be >= 0.
    database : list, optional
        Pre-loaded additive database (as returned by
        load_additive_database()). If not supplied, it is loaded
        automatically from the default path.

    Returns
    -------
    dict
        {
            "recommended_additive": str,
            "function": str,
            "typical_dosage_percent": str,
            "estimated_pump_time_min": float,
            "matched_temp_range_c": [float, float],
            "notes": str
        }

    Raises
    ------
    ValueError
        If bottom_hole_temp_c < 0.

    Notes
    -----
    If bottom_hole_temp_c exceeds the highest band in the database
    (i.e. an extreme HTHP well, the kind of stress-test scenario your
    examiner panel may use), the highest-temperature additive is still
    returned, but flagged with a notes warning that the well is outside
    the database's validated range and specialist HTHP cement design
    should be consulted.

    Example
    -------
    >>> recommend_additives(110)["recommended_additive"]
    'Lignosulfonate Retarder'
    """
    if bottom_hole_temp_c < 0:
        raise ValueError("Bottom Hole Temperature cannot be negative.")

    if database is None:
        database = load_additive_database()

    if not database:
        raise ValueError("Additive database is empty.")

    # Sort by lower bound to make boundary logic and "exceeds max" check reliable
    sorted_db = sorted(database, key=lambda entry: entry["temp_range_c"][0])

    for entry in sorted_db:
        low, high = entry["temp_range_c"]
        is_last_band = entry is sorted_db[-1]
        in_band = (low <= bottom_hole_temp_c < high) or (
            is_last_band and bottom_hole_temp_c == high
        )
        if in_band:
            return {
                "recommended_additive": entry["additive"],
                "function": entry["function"],
                "typical_dosage_percent": entry["typical_dosage_percent"],
                "estimated_pump_time_min": entry["estimated_pump_time_min"],
                "matched_temp_range_c": entry["temp_range_c"],
                "notes": (
                    f"BHT {bottom_hole_temp_c:.1f}\u00b0C falls within the "
                    f"validated range [{low}, {high}]\u00b0C for this additive."
                ),
            }

    # BHT exceeds the highest band -> return the highest-temperature
    # additive with a clear warning, rather than failing silently.
    highest = sorted_db[-1]
    low, high = highest["temp_range_c"]
    return {
        "recommended_additive": highest["additive"],
        "function": highest["function"],
        "typical_dosage_percent": highest["typical_dosage_percent"],
        "estimated_pump_time_min": highest["estimated_pump_time_min"],
        "matched_temp_range_c": [low, high],
        "notes": (
            f"WARNING: BHT {bottom_hole_temp_c:.1f}\u00b0C exceeds the highest "
            f"validated range in the database ([{low}, {high}]\u00b0C). The "
            f"'{highest['additive']}' recommendation is provided as a starting "
            f"point only \u2014 specialist HTHP cement slurry design and "
            f"laboratory thickening-time testing should be consulted before "
            f"field application."
        ),
    }