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

# NOTE: more imports will be added as Steps 3-7 are implemented.
from modules import mud_engine

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
    st.header("Mud Weight & Pressure Balance Design")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Wellbore Inputs")
        tvd = st.number_input("True Vertical Depth, TVD (m)", min_value=0.0, value=3000.0, step=50.0)
        mud_density = st.number_input("Proposed Mud Density (kg/m³)", min_value=0.1, value=1250.0, step=10.0)

    with col2:
        st.subheader("Formation Gradients (Equivalent Mud Weight)")
        pore_pressure = st.number_input("Pore Pressure Gradient (kg/m³ EMW)", min_value=0.1, value=1150.0, step=10.0)
        fracture_gradient = st.number_input("Fracture Gradient (kg/m³ EMW)", min_value=0.1, value=1450.0, step=10.0)

    if st.button("Calculate", type="primary"):
        try:
            # Hydrostatic pressure
            p_hyd = mud_engine.calculate_hydrostatic_pressure(mud_density, tvd)

            st.metric("Hydrostatic Pressure", f"{p_hyd/1e6:.3f} MPa", f"{p_hyd:,.0f} Pa")

            # Safe window check
            window_result = mud_engine.check_safe_mud_window(
                mud_density, pore_pressure, fracture_gradient
            )

            st.subheader("Safe Mud Weight Window Check")
            if window_result["status"] == "SAFE":
                st.success(window_result["message"])
            elif window_result["is_safe"]:
                st.warning(window_result["message"])
            else:
                st.error(window_result["message"])

            m1, m2 = st.columns(2)
            m1.metric("Margin above Pore Pressure", f"{window_result['margin_to_pore_kg_m3']:.1f} kg/m³")
            m2.metric("Margin below Fracture Gradient", f"{window_result['margin_to_fracture_kg_m3']:.1f} kg/m³")

        except ValueError as e:
            st.error(f"Input error: {e}")

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