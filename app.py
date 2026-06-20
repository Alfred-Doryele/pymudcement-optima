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

from modules import mud_engine, hydraulics, cement_engine, cement_db, pa_plugs

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

        **Status:** ✅ All backend engineering modules complete (Steps 1-7):
        mud design, hydraulics & ECD, cementing volumetrics, additive
        recommendations, and plug/P&A design. Final GUI polish, validation,
        and reporting in progress (Steps 8-10).
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
    st.caption("Recommends a cement additive and estimated pump time based on Bottom Hole Temperature.")

    bht = st.number_input("Bottom Hole Temperature, BHT (°C)", min_value=0.0, value=110.0, step=5.0)

    if st.button("Get Additive Recommendation", type="primary"):
        try:
            rec = cement_db.recommend_additives(bht)

            st.subheader("Recommendation")
            st.metric("Recommended Additive", rec["recommended_additive"])

            a1, a2 = st.columns(2)
            a1.metric("Estimated Pump Time", f"{rec['estimated_pump_time_min']:.0f} min")
            a2.metric("Typical Dosage", rec["typical_dosage_percent"])

            st.info(f"**Function:** {rec['function']}")
            st.caption(f"Matched temperature range: {rec['matched_temp_range_c']} °C")

            if "WARNING" in rec["notes"]:
                st.error(rec["notes"])
            else:
                st.success(rec["notes"])

            with st.expander("View full additive database"):
                db = cement_db.load_additive_database()
                st.table(db)

        except ValueError as e:
            st.error(f"Input error: {e}")

elif page == "Plug & P&A Design":
    st.header("Plug Bumping Pressure & P&A Design")

    st.subheader("Plug Bumping Pressure")
    st.caption("Surface pressure expected when the top wiper plug lands on the float collar/shoe.")

    col1, col2 = st.columns(2)
    with col1:
        disp_pressure = st.number_input("Displacement Pressure (Pa)", min_value=0.0, value=2_000_000.0, step=100_000.0)
        friction_losses = st.number_input("Friction Losses (Pa)", min_value=0.0, value=500_000.0, step=50_000.0)
        tvd_plug = st.number_input("TVD to Plug Landing Point (m)", min_value=0.0, value=3000.0, step=50.0)
    with col2:
        mud_density_inside = st.number_input("Mud/Cement Density Inside Casing (kg/m³)", min_value=0.1, value=1900.0, step=10.0)
        displaced_density = st.number_input("Displaced Fluid Density in Annulus (kg/m³)", min_value=0.1, value=1250.0, step=10.0)

    if st.button("Calculate Plug Bumping Pressure", type="primary"):
        try:
            bump_result = pa_plugs.calculate_plug_bumping_pressure(
                displacement_pressure_pa=disp_pressure,
                friction_losses_pa=friction_losses,
                mud_density_kg_m3=mud_density_inside,
                displaced_fluid_density_kg_m3=displaced_density,
                tvd_m=tvd_plug,
            )

            b1, b2 = st.columns(2)
            b1.metric("Plug Bumping Pressure", f"{bump_result['plug_bumping_pressure_pa']/1e6:.3f} MPa")
            b2.metric("Hydrostatic Differential", f"{bump_result['hydrostatic_differential_pa']/1e6:.3f} MPa")

            if bump_result["warning"]:
                st.warning(bump_result["warning"])
            else:
                st.success("Plug bumping pressure is within a typical operational range.")

        except ValueError as e:
            st.error(f"Input error: {e}")

    st.divider()
    st.subheader("Cement Plug Design (Side-Track / Suspension / P&A)")

    col3, col4 = st.columns(2)
    with col3:
        hole_d_plug = st.number_input("Open Hole Diameter (m)", min_value=0.01, value=0.2159, step=0.001, format="%.4f")
        plug_length = st.number_input("Designed Plug Length (m)", min_value=0.1, value=120.0, step=5.0)
    with col4:
        purpose = st.selectbox("Plug Purpose", ["P&A", "suspension", "side_track"])
        excess_factor_plug = st.number_input("Excess Factor", min_value=0.0, value=0.0, step=0.05, format="%.2f")

    if st.button("Design Plug"):
        try:
            plug_result = pa_plugs.design_pa_plug(
                hole_diameter_m=hole_d_plug,
                plug_length_m=plug_length,
                purpose=purpose,
                excess_factor=excess_factor_plug,
            )

            p1, p2 = st.columns(2)
            p1.metric("Plug Volume", f"{plug_result['plug_volume_m3']:.3f} m³")
            p2.metric("Minimum Recommended Length", f"{plug_result['recommended_length_m']:.0f} m")

            if plug_result["meets_minimum_length"]:
                st.success(plug_result["notes"])
            else:
                st.error(plug_result["notes"])

        except ValueError as e:
            st.error(f"Input error: {e}")
elif page == "Job Procedure Report":
    st.header("Digital Cementing Job Procedure Sheet")
    st.caption("Consolidates mud design, hydraulics, cementing volumes, additives, and plug bumping pressure into one printable job sheet.")

    st.subheader("1. Well & Job Header")
    h1, h2, h3 = st.columns(3)
    with h1:
        well_name = st.text_input("Well Name", value="Well-A1")
        job_date = st.date_input("Job Date")
    with h2:
        tvd_report = st.number_input("TVD (m)", min_value=0.1, value=3000.0, step=50.0, key="rpt_tvd")
        bht_report = st.number_input("Bottom Hole Temperature, BHT (°C)", min_value=0.0, value=110.0, step=5.0, key="rpt_bht")
    with h3:
        prepared_by = st.text_input("Prepared By", value="")
        approved_by = st.text_input("Approved By (Supervisor)", value="")

    st.divider()
    st.subheader("2. Mud Design Parameters")
    m1, m2 = st.columns(2)
    with m1:
        rpt_mud_density = st.number_input("Mud Density (kg/m³)", min_value=0.1, value=1250.0, step=10.0, key="rpt_mud")
        rpt_pore_pressure = st.number_input("Pore Pressure Gradient (kg/m³ EMW)", min_value=0.1, value=1150.0, step=10.0, key="rpt_pp")
        rpt_fracture_gradient = st.number_input("Fracture Gradient (kg/m³ EMW)", min_value=0.1, value=1450.0, step=10.0, key="rpt_fg")
    with m2:
        rpt_pv_cp = st.number_input("Plastic Viscosity, PV (cP)", min_value=0.0, value=20.0, step=1.0, key="rpt_pv")
        rpt_yp_lb = st.number_input("Yield Point, YP (lb/100ft²)", min_value=0.0, value=15.0, step=1.0, key="rpt_yp")
        rpt_shear_rate = st.number_input("Shear Rate (s⁻¹)", min_value=0.0, value=100.0, step=10.0, key="rpt_sr")

    st.divider()
    st.subheader("3. Hydraulics & Cementing Geometry")
    st.caption("Note: hydraulics uses the open hole / drill pipe annulus; cementing uses the open hole / casing annulus for the casing string being run.")
    g1, g2 = st.columns(2)
    with g1:
        rpt_hole_d = st.number_input("Open Hole Diameter (m)", min_value=0.01, value=0.31115, step=0.001, format="%.5f", key="rpt_hole")
        rpt_pipe_od = st.number_input("Drill Pipe OD (m)", min_value=0.01, value=0.127, step=0.001, format="%.4f", key="rpt_pipe")
        rpt_flow_rate = st.number_input("Flow Rate (L/min)", min_value=1.0, value=300.0, step=10.0, key="rpt_flow")
    with g2:
        rpt_casing_od = st.number_input("Casing OD (m)", min_value=0.01, value=0.24448, step=0.001, format="%.5f", key="rpt_cod")
        rpt_casing_id = st.number_input("Casing ID (m)", min_value=0.01, value=0.22049, step=0.001, format="%.5f", key="rpt_cid")
        rpt_cement_length = st.number_input("Cemented Interval Length (m)", min_value=0.0, value=500.0, step=10.0, key="rpt_clen")

    if st.button("Generate Job Procedure Sheet", type="primary"):
        try:
            # --- Run all calculations ---
            p_hyd = mud_engine.calculate_hydrostatic_pressure(rpt_mud_density, tvd_report)
            window_result = mud_engine.check_safe_mud_window(rpt_mud_density, rpt_pore_pressure, rpt_fracture_gradient)
            rheology = mud_engine.parse_mud_report({"PV": rpt_pv_cp, "YP": rpt_yp_lb})
            tau = mud_engine.calculate_shear_stress(rheology["YP_pa"], rheology["PV_pa_s"], rpt_shear_rate)

            flow_rate_m3_s = rpt_flow_rate / 60000
            dp_result = hydraulics.calculate_annular_pressure_drop(
                plastic_viscosity_pa_s=rheology["PV_pa_s"],
                yield_point_pa=rheology["YP_pa"],
                flow_rate_m3_s=flow_rate_m3_s,
                hole_diameter_m=rpt_hole_d,
                pipe_od_m=rpt_pipe_od,
                length_m=tvd_report,
                mud_density_kg_m3=rpt_mud_density,
            )
            ecd_result = hydraulics.calculate_ecd(
                rpt_mud_density, dp_result["pressure_drop_pa"], tvd_report, rpt_fracture_gradient
            )

            v_ann = cement_engine.calculate_annular_volume(rpt_hole_d, rpt_casing_od, rpt_cement_length)
            slurry = cement_engine.calculate_slurry_volumes(v_ann, 0.6, 0.4)
            v_disp = cement_engine.calculate_displacement_volume(rpt_casing_id, tvd_report)

            additive_rec = cement_db.recommend_additives(bht_report)

            bump_result = pa_plugs.calculate_plug_bumping_pressure(
                displacement_pressure_pa=2_000_000,
                friction_losses_pa=dp_result["pressure_drop_pa"],
                mud_density_kg_m3=rpt_mud_density,
                displaced_fluid_density_kg_m3=rpt_mud_density,
                tvd_m=tvd_report,
            )

            # --- Display on-screen summary ---
            st.success("Job procedure sheet generated successfully.")

            st.subheader("📋 Summary")
            d1, d2, d3 = st.columns(3)
            d1.metric("Hydrostatic Pressure", f"{p_hyd/1e6:.2f} MPa")
            d2.metric("ECD", f"{ecd_result['ecd_kg_m3']:.1f} kg/m³")
            d3.metric("Plug Bumping Pressure", f"{bump_result['plug_bumping_pressure_pa']/1e6:.2f} MPa")

            d4, d5, d6 = st.columns(3)
            d4.metric("Annular Cement Volume", f"{v_ann:.2f} m³")
            d5.metric("Displacement Volume", f"{v_disp:.2f} m³")
            d6.metric("Recommended Additive", additive_rec["recommended_additive"])

            if not window_result["is_safe"]:
                st.error(f"⚠️ Mud Weight Check: {window_result['message']}")
            else:
                st.info(f"Mud Weight Check: {window_result['message']}")

            # --- Generate PDF ---
            from fpdf import FPDF

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, "Cementing Job Procedure Sheet", ln=True, align="C")
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 6, "PyMudCement-Optima | PENG 258 Capstone Project", ln=True, align="C")
            pdf.ln(4)

            def section(title):
                pdf.set_font("Helvetica", "B", 12)
                pdf.set_fill_color(220, 230, 240)
                pdf.cell(0, 8, title, ln=True, fill=True)
                pdf.set_font("Helvetica", "", 10)

            def row(label, value):
                pdf.cell(95, 6, str(label), border=0)
                pdf.cell(95, 6, str(value), border=0, ln=True)

            section("Well & Job Header")
            row("Well Name:", well_name)
            row("Job Date:", str(job_date))
            row("TVD:", f"{tvd_report:.1f} m")
            row("Bottom Hole Temperature:", f"{bht_report:.1f} C")
            row("Prepared By:", prepared_by or "-")
            row("Approved By:", approved_by or "-")
            pdf.ln(2)

            section("Mud Design")
            row("Mud Density:", f"{rpt_mud_density:.1f} kg/m3")
            row("Hydrostatic Pressure:", f"{p_hyd/1e6:.3f} MPa")
            row("Safe Window Status:", window_result["status"])
            row("PV (converted):", f"{rheology['PV_pa_s']:.4f} Pa.s")
            row("YP (converted):", f"{rheology['YP_pa']:.3f} Pa")
            row("Shear Stress:", f"{tau:.3f} Pa")
            row("Fluid Classification:", rheology["fluid_type"])
            pdf.ln(2)

            section("Hydraulics & ECD")
            row("Annular Velocity:", f"{dp_result['annular_velocity_m_s']:.3f} m/s")
            row("Annular Pressure Drop:", f"{dp_result['pressure_drop_pa']/1e3:.1f} kPa")
            row("Flow Regime:", dp_result["flow_regime"])
            row("ECD:", f"{ecd_result['ecd_kg_m3']:.1f} kg/m3")
            pdf.ln(2)

            section("Cementing Volumes")
            row("Annular Cement Volume:", f"{v_ann:.3f} m3")
            row("Lead Slurry Volume:", f"{slurry['lead_volume_m3']:.3f} m3")
            row("Tail Slurry Volume:", f"{slurry['tail_volume_m3']:.3f} m3")
            row("Displacement Volume:", f"{v_disp:.3f} m3")
            pdf.ln(2)

            section("Additive Recommendation")
            row("Recommended Additive:", additive_rec["recommended_additive"])
            row("Estimated Pump Time:", f"{additive_rec['estimated_pump_time_min']:.0f} min")
            row("Typical Dosage:", additive_rec["typical_dosage_percent"])
            pdf.ln(2)

            section("Plug Bumping Pressure")
            row("Plug Bumping Pressure:", f"{bump_result['plug_bumping_pressure_pa']/1e6:.3f} MPa")
            if bump_result["warning"]:
                pdf.set_text_color(200, 0, 0)
                pdf.multi_cell(0, 6, f"WARNING: {bump_result['warning']}")
                pdf.set_text_color(0, 0, 0)
            pdf.ln(4)

            pdf.set_font("Helvetica", "I", 9)
            pdf.cell(0, 6, "Signature (Prepared By): _______________________     Signature (Approved By): _______________________", ln=True)

            pdf_bytes = bytes(pdf.output())

            st.download_button(
                label="📄 Download Job Procedure Sheet (PDF)",
                data=pdf_bytes,
                file_name=f"job_procedure_sheet_{well_name.replace(' ', '_')}.pdf",
                mime="application/pdf",
            )

        except ValueError as e:
            st.error(f"Input error: {e}")