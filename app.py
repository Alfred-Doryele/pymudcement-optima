"""
app.py
======
PyMudCement-Optima — Streamlit GUI Entry Point

This is the single entry point that ties together all backend engines:
    - modules.mud_engine       (mud weight, PV/YP)
    - modules.hydraulics       (annular pressure drop, ECD)
    - modules.cement_engine    (slurry/spacer/displacement volumes)
    - modules.cement_db        (additive recommendations)
    - modules.pa_plugs         (plug bumping pressure, P&A design)

Run locally with:
    streamlit run app.py

Author(s):  <add your group member name(s) here>
Course:     PENG 258 - Drilling Engineering 1
"""

import streamlit as st

# NOTE: these imports will start working once Steps 2-7 are implemented.
# from modules import mud_engine, hydraulics, cement_engine, cement_db, pa_plugs

st.set_page_config(
    page_title="PyMudCement-Optima",
    page_icon="🛢️",
    layout="wide"
)

st.title("🛢️ PyMudCement-Optima")
st.caption("Intelligent Mud & Cement Design Suite — PENG 258 Capstone Project")

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select Module",
    [
        "Home",
        "Mud Design",
        "Hydraulics & ECD",
        "Cementing Volumetrics",
        "Additive Recommendation",
        "Plug & P&A Design",
        "Job Procedure Report",
    ]
)

if page == "Home":
    st.markdown(
        """
        ### Welcome
        This application automates drilling fluid design and primary cementing
        engineering calculations, in line with SPE industry competencies.

        Use the sidebar to navigate between modules. Each module will be built
        out progressively in Steps 2-7 of the project plan.

        **Status:** 🚧 Scaffold only — backend logic not yet implemented (Step 1 complete).
        """
    )

elif page == "Mud Design":
    st.header("Mud Weight & Rheology Design")
    st.info("This section will be wired up in Step 2 & 3 (mud_engine.py).")
    # TODO: build input form -> call mud_engine functions -> display results

elif page == "Hydraulics & ECD":
    st.header("Annular Hydraulics & ECD")
    st.info("This section will be wired up in Step 4 (hydraulics.py).")
    # TODO: build input form -> call hydraulics functions -> display results

elif page == "Cementing Volumetrics":
    st.header("Cement Slurry & Spacer Volumes")
    st.info("This section will be wired up in Step 5 (cement_engine.py).")
    # TODO: build input form -> call cement_engine functions -> display results

elif page == "Additive Recommendation":
    st.header("Cement Additive Lookup")
    st.info("This section will be wired up in Step 6 (cement_db.py).")
    # TODO: build input form -> call cement_db functions -> display results

elif page == "Plug & P&A Design":
    st.header("Plug Bumping Pressure & P&A Design")
    st.info("This section will be wired up in Step 7 (pa_plugs.py).")
    # TODO: build input form -> call pa_plugs functions -> display results

elif page == "Job Procedure Report":
    st.header("Digital Cementing Job Procedure Sheet")
    st.info("This section generates the downloadable report (Milestone 2 / Step 8).")
    # TODO: aggregate results from all modules -> generate PDF/printable report
