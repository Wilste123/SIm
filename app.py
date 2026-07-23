from __future__ import annotations

import pandas as pd
import streamlit as st

from src.data.default_prices import DEFAULT_PRICES_PER_METER
from src.engine.beam_calculations import analyze_beam
from src.engine.material_calculations import build_materials_dataframe, summarize_materials
from src.engine.risk_assessment import assess_risk
from src.engine.wall_generator import generate_wall_layout
from src.engine.weather_simulation import WEATHER_SCENARIOS
from src.export.json_export import build_project_payload, export_project_json
from src.ui.beam_input_form import render_beam_input_form
from src.ui.project_summary import render_project_form, render_project_summary
from src.ui.report_view import render_report_view
from src.ui.sidebar_inputs import render_sidebar_inputs
from src.ui.wall_input_form import render_wall_input_form
from src.visuals.beam_plot import create_beam_figure
from src.visuals.color_theme import COLORS
from src.visuals.load_plot import create_load_scenario_figure
from src.visuals.wall_plot import create_wall_figure

DISCLAIMER = (
    "Dette verktøyet gir kun forenklede beregninger og visuelle estimater. "
    "Resultatene skal ikke brukes som endelig dokumentasjon for bærende konstruksjoner. "
    "Ved tiltak som påvirker bæreevne, stabilitet eller personsikkerhet må løsningen kontrolleres "
    "av kvalifisert fagperson/byggingeniør."
)

st.set_page_config(page_title="LåveSim", layout="wide")


def main() -> None:
    st.title("LåveSim")
    st.subheader("Forenklet konstruksjons- og materialverktøy for små bygg")
    st.warning(DISCLAIMER, icon="⚠️")

    sidebar = render_sidebar_inputs(DEFAULT_PRICES_PER_METER)
    prices = sidebar["prices"]
    waste_factor = sidebar["waste_factor"]

    tabs = st.tabs([
        "Prosjekt",
        "Vegg/stendere",
        "Bjelke/bæring",
        "Last og uvær",
        "Materialliste",
        "Rapport",
    ])

    with tabs[0]:
        project_data = render_project_form()
        render_project_summary(project_data)

    with tabs[1]:
        wall_data = render_wall_input_form()
        wall_result = generate_wall_layout(wall_data)
        material_df = build_materials_dataframe(wall_data, wall_result, prices)
        wall_result["estimated_cost"] = float(material_df["estimert kostnad"].sum())
        wall_fig = create_wall_figure(wall_data, wall_result)
        st.plotly_chart(wall_fig, use_container_width=True)

        st.markdown("### Veggoppsummering")
        metric_columns = st.columns(4)
        metric_columns[0].metric("Ordinære stendere", wall_result["regular_stud_count"])
        metric_columns[1].metric("Ekstra stendere", wall_result["extra_stud_count"])
        metric_columns[2].metric("Totalt trevirke", f"{wall_result['total_timber_m']:.1f} lm")
        metric_columns[3].metric("Estimert kostnad", f"{wall_result['estimated_cost']:.0f} kr")

    with tabs[2]:
        beam_data = render_beam_input_form()
        beam_result = analyze_beam(beam_data)
        st.markdown("### Enkel bjelkevurdering")
        beam_metrics = st.columns(4)
        beam_metrics[0].metric("Maks moment", f"{beam_result['moment_kNm']:.2f} kNm")
        beam_metrics[1].metric("Skjærkraft", f"{beam_result['shear_kN']:.2f} kN")
        beam_metrics[2].metric("Nedbøyning", f"{beam_result['deflection_mm']:.1f} mm")
        beam_metrics[3].metric("Utnyttelsesgrad", f"{beam_result['utilization_ratio']:.2f}")
        st.info(beam_result["summary"])
        st.plotly_chart(create_beam_figure(beam_data["span_m"], beam_result["utilization_ratio"]), use_container_width=True)

    with tabs[3]:
        st.markdown("### Last og uvær")
        selected_scenario = st.selectbox(
            "Velg scenario",
            list(WEATHER_SCENARIOS.keys()),
            index=0,
        )
        scenario = WEATHER_SCENARIOS[selected_scenario]
        st.write(scenario["description"])
        st.write(f"Antatt lastøkning: **{scenario['load_factor']:.0%}**")
        st.plotly_chart(create_load_scenario_figure(selected_scenario, scenario), use_container_width=True)
        st.markdown("#### Anbefalte tiltak")
        for recommendation in scenario["recommendations"]:
            st.write(f"- {recommendation}")

    material_summary = summarize_materials(material_df, waste_factor)
    risk = assess_risk(
        wall_data=wall_data,
        wall_result=wall_result,
        beam_data=beam_data,
        beam_result=beam_result,
        scenario_name=selected_scenario,
    )

    with tabs[4]:
        st.markdown("### Materialliste")
        st.dataframe(material_df, use_container_width=True)
        total_cols = st.columns(4)
        total_cols[0].metric("Total løpemeter", f"{material_summary['total_length_m']:.1f} lm")
        total_cols[1].metric("Estimert kostnad", f"{material_summary['total_cost']:.0f} kr")
        total_cols[2].metric("Svinn", f"{waste_factor:.0f} %")
        total_cols[3].metric("Kostnad inkl. svinn", f"{material_summary['cost_with_waste']:.0f} kr")

    report_payload = build_project_payload(
        project_data=project_data,
        wall_data=wall_data,
        wall_result=wall_result,
        beam_data=beam_data,
        beam_result=beam_result,
        scenario_name=selected_scenario,
        scenario=scenario,
        risk=risk,
        material_df=material_df,
        material_summary=material_summary,
    )

    with tabs[5]:
        render_report_view(
            project_data=project_data,
            wall_data=wall_data,
            beam_data=beam_data,
            scenario_name=selected_scenario,
            risk=risk,
            material_df=material_df,
            disclaimer=DISCLAIMER,
        )
        st.download_button(
            "Eksporter prosjekt som JSON",
            data=export_project_json(report_payload),
            file_name=f"{project_data['project_name'].replace(' ', '_').lower() or 'lavesim_prosjekt'}.json",
            mime="application/json",
        )
        st.dataframe(pd.DataFrame([risk]), use_container_width=True)

    risk_color = COLORS.get(
        "success" if risk["level"] == "green" else "warning" if risk["level"] == "yellow" else "danger"
    )
    st.markdown(
        f"<div style='padding:0.75rem 1rem;border-radius:0.5rem;background:{risk_color};color:white;'>"
        f"<strong>{risk['title']}</strong><br>{risk['message']}</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
