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

# NOTE: more imports will be added as Steps 6-7 are implemented.
from modules import mud_engine, hydraulics, cement_engine

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

        Use the sidebar to navigate between modules.

        **Status:** ✅ Mud Design, Hydraulics & ECD, and Cementing Volumetrics
        modules complete (Steps 1-5). Additive database and P&A modules in progress.
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

    st.divider()
    st.subheader("Rheology Analysis (Mud Report)")

    col3, col4, col5 = st.columns(3)
    with col3:
        pv_cp = st.number_input("Plastic Viscosity, PV (cP)", min_value=0.0, value=20.0, step=1.0)
    with col4:
        yp_lb = st.number_input("Yield Point, YP (lb/100ft²)", min_value=0.0, value=15.0, step=1.0)
    with col5:
        shear_rate = st.number_input("Shear Rate, γ (s⁻¹)", min_value=0.0, value=100.0, step=10.0)

    if st.button("Analyze Rheology"):
        try:
            report = mud_engine.parse_mud_report({"PV": pv_cp, "YP": yp_lb})

            r1, r2, r3 = st.columns(3)
            r1.metric("PV (converted)", f"{report['PV_pa_s']:.4f} Pa·s")
            r2.metric("YP (converted)", f"{report['YP_pa']:.3f} Pa")

            tau = mud_engine.calculate_shear_stress(
                report["YP_pa"], report["PV_pa_s"], shear_rate
            )
            r3.metric("Shear Stress, τ", f"{tau:.3f} Pa")

            st.info(f"**Fluid Classification:** {report['fluid_type']}")

        except ValueError as e:
            st.error(f"Input error: {e}")

elif page == "Hydraulics & ECD":
    st.header("Annular Hydraulics & ECD")
    st.caption("Bingham-Plastic laminar annular pressure drop and live ECD tracking.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Fluid Properties")
        pv_pa_s = st.number_input("Plastic Viscosity, PV (Pa·s)", min_value=0.0, value=0.02, step=0.001, format="%.4f")
        yp_pa = st.number_input("Yield Point, YP (Pa)", min_value=0.0, value=7.182, step=0.1)
        mud_weight = st.number_input("Mud Density (kg/m³)", min_value=0.1, value=1250.0, step=10.0)

    with col2:
        st.subheader("Wellbore & Flow Inputs")
        flow_rate_lpm = st.number_input("Flow Rate, Q (L/min)", min_value=1.0, value=300.0, step=10.0)
        hole_d = st.number_input("Hole Diameter, Dh (m)", min_value=0.01, value=0.2159, step=0.001, format="%.4f")
        pipe_od = st.number_input("Pipe OD, Dp (m)", min_value=0.01, value=0.127, step=0.001, format="%.4f")
        length = st.number_input("Annular Interval Length, L (m)", min_value=0.0, value=3000.0, step=50.0)
        tvd_hyd = st.number_input("TVD (m)", min_value=0.1, value=3000.0, step=50.0)
        fracture_gradient_hyd = st.number_input("Fracture Gradient (kg/m³ EMW)", min_value=0.1, value=1450.0, step=10.0)

    if st.button("Calculate Hydraulics", type="primary"):
        try:
            flow_rate_m3_s = flow_rate_lpm / 60000  # L/min -> m^3/s

            dp_result = hydraulics.calculate_annular_pressure_drop(
                plastic_viscosity_pa_s=pv_pa_s,
                yield_point_pa=yp_pa,
                flow_rate_m3_s=flow_rate_m3_s,
                hole_diameter_m=hole_d,
                pipe_od_m=pipe_od,
                length_m=length,
                mud_density_kg_m3=mud_weight,
            )

            c1, c2, c3 = st.columns(3)
            c1.metric("Annular Velocity", f"{dp_result['annular_velocity_m_s']:.3f} m/s")
            c2.metric("Pressure Drop", f"{dp_result['pressure_drop_pa']/1e3:.1f} kPa")
            c3.metric("Reynolds Number", f"{dp_result['reynolds_number']:.0f}")

            if dp_result["flow_regime"] == "LAMINAR":
                st.success(f"Flow Regime: {dp_result['flow_regime']} ✅ (laminar formula valid)")
            else:
                st.warning(f"Flow Regime: {dp_result['flow_regime']} — {dp_result['warning']}")

            st.divider()

            ecd_result = hydraulics.calculate_ecd(
                mud_weight_kg_m3=mud_weight,
                annular_pressure_drop_pa=dp_result["pressure_drop_pa"],
                tvd_m=tvd_hyd,
                fracture_gradient_kg_m3=fracture_gradient_hyd,
            )

            st.subheader("Equivalent Circulating Density (ECD)")
            st.metric("ECD", f"{ecd_result['ecd_kg_m3']:.1f} kg/m³")

            if ecd_result["exceeds_fracture_gradient"]:
                st.error(ecd_result["message"])
            else:
                st.success(ecd_result["message"])

        except ValueError as e:
            st.error(f"Input error: {e}")

elif page == "Cementing Volumetrics":
    st.header("Cement Slurry & Spacer Volumes")
    st.caption("Annular cement volume, lead/tail slurry split, and displacement fluid volume.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Hole & Casing Geometry")
        hole_d_cem = st.number_input("Open Hole Diameter, Dh (m)", min_value=0.01, value=0.31115, step=0.001, format="%.5f")
        casing_od = st.number_input("Casing Outer Diameter (m)", min_value=0.01, value=0.24448, step=0.001, format="%.5f")
        casing_id = st.number_input("Casing Inner Diameter (m)", min_value=0.01, value=0.22049, step=0.001, format="%.5f")
        cement_length = st.number_input("Cemented Interval Length, L (m)", min_value=0.0, value=500.0, step=10.0)

    with col2:
        st.subheader("Job Design Parameters")
        excess_factor = st.number_input("Open-Hole Excess Factor, We", min_value=0.0, value=0.15, step=0.01, format="%.2f")
        lead_fraction = st.slider("Lead Slurry Fraction", min_value=0.0, max_value=1.0, value=0.6, step=0.05)
        tail_fraction = st.slider("Tail Slurry Fraction", min_value=0.0, max_value=1.0, value=0.4, step=0.05)
        casing_length = st.number_input("Casing String Length (for displacement), m", min_value=0.0, value=3000.0, step=50.0)

    if st.button("Calculate Cementing Volumes", type="primary"):
        try:
            v_ann = cement_engine.calculate_annular_volume(
                hole_d_cem, casing_od, cement_length, excess_factor
            )

            st.subheader("Annular Cement Volume")
            st.metric("Total Annular Volume", f"{v_ann:.3f} m³")

            st.divider()
            st.subheader("Lead / Tail Slurry Split")

            slurry = cement_engine.calculate_slurry_volumes(v_ann, lead_fraction, tail_fraction)

            s1, s2, s3 = st.columns(3)
            s1.metric("Lead Slurry Volume", f"{slurry['lead_volume_m3']:.3f} m³")
            s2.metric("Tail Slurry Volume", f"{slurry['tail_volume_m3']:.3f} m³")
            s3.metric("Unallocated Fraction", f"{slurry['unallocated_fraction']*100:.0f}%")

            if slurry["warning"]:
                st.error(slurry["warning"])
            else:
                st.success("Slurry volumes allocated within total annular volume.")

            st.divider()
            st.subheader("Displacement Fluid Volume")

            v_disp = cement_engine.calculate_displacement_volume(casing_id, casing_length)
            st.metric("Displacement Volume (inside casing)", f"{v_disp:.3f} m³")

        except ValueError as e:
            st.error(f"Input error: {e}")

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