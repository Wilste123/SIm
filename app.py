from __future__ import annotations

import pandas as pd
import streamlit as st

from src.data.default_prices import DEFAULT_PRICES_PER_METER
from src.engine.beam_calculations import analyze_beam
from src.engine.global_stability import assess_lateral_stability
from src.engine.load_paths import build_load_distribution
from src.engine.material_calculations import build_materials_dataframe, summarize_materials
from src.engine.removal_scenarios import apply_removal_scenario, assess_removal_risk
from src.engine.replacement_beam import evaluate_replacement_beam
from src.engine.risk_assessment import assess_risk
from src.engine.structural_system import build_structural_model
from src.engine.wall_generator import generate_wall_layout
from src.engine.weather_simulation import WEATHER_SCENARIOS
from src.export.json_export import build_project_payload, export_project_json
from src.ui.barn_system_inputs import render_barn_system_inputs
from src.ui.beam_input_form import render_beam_input_form
from src.ui.project_summary import render_project_form, render_project_summary
from src.ui.removal_scenario_inputs import render_removal_scenario_inputs
from src.ui.report_view import render_report_view
from src.ui.sidebar_inputs import render_sidebar_inputs
from src.ui.wall_input_form import render_wall_input_form
from src.visuals.barn_plan_plot import create_barn_plan_figure
from src.visuals.beam_plot import create_beam_figure
from src.visuals.color_theme import COLORS
from src.visuals.load_path_plot import create_load_path_figure
from src.visuals.load_plot import create_load_scenario_figure
from src.visuals.system_risk_plot import create_system_risk_figure
from src.visuals.wall_plot import create_wall_figure

DISCLAIMER = (
    "Dette verktøyet gir kun forenklede beregninger og visuelle estimater. "
    "Resultatene skal ikke brukes som endelig dokumentasjon for bærende konstruksjoner. "
    "Ved tiltak som påvirker bæreevne, stabilitet eller personsikkerhet må løsningen kontrolleres "
    "av kvalifisert fagperson/byggingeniør."
)

STRUCTURAL_DISCLAIMER = (
    "Denne modulen gir kun en forenklet og pedagogisk vurdering av lastveier og mulige konsekvenser "
    "ved endring av bærekonstruksjon. Den skal ikke brukes som prosjekteringsgrunnlag eller som "
    "dokumentasjon for fjerning av bærevegg, søyle eller drager. Ved inngrep i bærende konstruksjoner "
    "må løsningen vurderes av kvalifisert fagperson/byggingeniør, og søknadsplikt må avklares med kommunen."
)

st.set_page_config(page_title="LåveSim", layout="wide")


def _max_risk_level(*levels: str) -> str:
    score = {"green": 1, "yellow": 2, "red": 3}
    highest = "green"
    for level in levels:
        if score.get(level, 2) > score[highest]:
            highest = level
    return highest


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
        "Bæresystem / Låveanalyse",
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

    with tabs[5]:
        st.markdown("### Bæresystem / Låveanalyse")
        st.warning(STRUCTURAL_DISCLAIMER, icon="⚠️")

        barn_inputs = render_barn_system_inputs()

        st.markdown("### Lastmodell")
        l1, l2, l3 = st.columns(3)
        egenlast_tak_kn_m2 = l1.number_input("Egenlast tak (kN/m²)", min_value=0.1, value=0.8, step=0.1)
        snolast_kn_m2 = l2.number_input("Snølast (kN/m²)", min_value=0.0, value=1.5, step=0.1)
        nyttelast_gulv_kn_m2 = l3.number_input("Nyttelast gulv (kN/m²)", min_value=0.0, value=2.0, step=0.1)

        l4, l5, l6 = st.columns(3)
        lagerlast_kn_m2 = l4.number_input("Lagerlast (kN/m²)", min_value=0.0, value=1.0, step=0.1)
        vindscenario = l5.selectbox("Vindscenario", ["lav", "normal", "høy", "storm"], index=1)
        usikkerhetsfaktor = l6.slider("Sikkerhets-/usikkerhetsfaktor", min_value=1.0, max_value=2.0, value=1.2, step=0.05)

        load_input = {
            "egenlast_tak_kn_m2": egenlast_tak_kn_m2,
            "snolast_kn_m2": snolast_kn_m2,
            "nyttelast_gulv_kn_m2": nyttelast_gulv_kn_m2,
            "lagerlast_kn_m2": lagerlast_kn_m2,
            "vindscenario": vindscenario,
            "usikkerhetsfaktor": usikkerhetsfaktor,
        }

        base_model = build_structural_model(barn_inputs["building"], barn_inputs["system"], load_input)
        support_options = [
            {"id": line["id"], "navn": line["navn"]} for line in base_model.get("support_lines", [])
        ] + [{"id": point["id"], "navn": point["navn"]} for point in base_model.get("point_supports", [])]

        scenario_input = render_removal_scenario_inputs(support_options)

        before_distribution = build_load_distribution(base_model, usikkerhetsfaktor)
        before_model = {**base_model, "load_distribution": before_distribution}

        after_model = apply_removal_scenario(base_model, scenario_input)
        after_distribution = build_load_distribution(after_model, usikkerhetsfaktor)
        after_model["load_distribution"] = after_distribution

        removal_risk = assess_removal_risk(before_model, after_model, scenario_input)
        lateral_risk = assess_lateral_stability(after_model, scenario_input)
        overall_level = _max_risk_level(removal_risk["risk_level"], lateral_risk["risk_level"])

        st.markdown("### Konsekvensanalyse")
        k1, k2, k3 = st.columns(3)
        k1.metric("Samlet last før", f"{before_distribution['total_load_kn']:.1f} kN")
        k2.metric("Samlet last etter", f"{after_distribution['total_load_kn']:.1f} kN")
        k3.metric("Risikonivå (forenklet)", overall_level.upper())

        st.plotly_chart(create_barn_plan_figure(before_model, after_model, scenario_input, overall_level), use_container_width=True)
        st.plotly_chart(create_load_path_figure(before_distribution, after_distribution), use_container_width=True)
        st.plotly_chart(create_system_risk_figure(removal_risk, lateral_risk), use_container_width=True)

        st.markdown("### Lastvei og reaksjonsøkning")
        if removal_risk["reaction_increase"]:
            reaction_df = pd.DataFrame.from_dict(removal_risk["reaction_increase"], orient="index").reset_index()
            reaction_df = reaction_df.rename(columns={"index": "støtte"})
            st.dataframe(reaction_df, use_container_width=True)

        if removal_risk["unresolved_load_paths"]:
            st.error("Uavklarte lastveier funnet. Resultatet er kun en grov indikasjon.")
            st.markdown("**Uavklarte lastveier:**")
            for finding in removal_risk["unresolved_load_paths"]:
                st.write(f"- {finding}")

        st.markdown("### Horisontal stabilitet")
        for finding in lateral_risk["findings"]:
            st.write(f"- {finding}")

        st.markdown("### Anbefalt tiltak")
        combined_recommendations = list(dict.fromkeys(removal_risk["recommendations"] + lateral_risk["recommendations"]))
        for recommendation in combined_recommendations:
            st.write(f"- {recommendation}")

        st.markdown("### Midlertidig understøtting")
        if removal_risk["requires_temporary_support"]:
            st.warning(
                "Anbefalt ved valgt scenario fordi bærende element påvirkes og risiko er gul/rød. "
                "Appen dimensjonerer ikke midlertidig understøtting; løsning må avklares faglig."
            )
        else:
            st.info("Ingen tydelig indikasjon på behov i denne forenklede vurderingen, men dette bør kontrolleres.")

        st.markdown("### Rapportgrunnlag")
        st.caption("Alle resultater i denne fanen er forenklede estimater og pedagogiske indikasjoner.")

        replacement_result = None
        if scenario_input.get("proposed_replacement") in {"limtredrager", "ståldrager", "trebjelke"}:
            max_line_load = max(after_distribution.get("line_loads_kn_per_m", {}).values(), default=0.0)
            material_map = {
                "limtredrager": "GL30 limtre",
                "ståldrager": "S355 stål",
                "trebjelke": "C24 tre",
            }
            replacement_result = evaluate_replacement_beam(
                span_m=scenario_input.get("replacement_beam_span_m", 0.0),
                dragerdimensjon=scenario_input.get("dragerdimensjon", "48x198"),
                materiale=material_map.get(scenario_input.get("proposed_replacement"), "C24 tre"),
                line_load_kn_per_m=max_line_load,
                antall_understottelser=scenario_input.get("antall_understottelser", 2),
            )
            st.markdown("### Forenklet dragerindikasjon")
            st.write(
                f"Utnyttelsesgrad (estimert): **{replacement_result['utilization_ratio']:.2f}** "
                f"(risiko: {replacement_result['risk_level']})"
            )

        barn_analysis = {
            "disclaimer": STRUCTURAL_DISCLAIMER,
            "building_input": barn_inputs["building"],
            "system_input": barn_inputs["system"],
            "load_input": load_input,
            "scenario": scenario_input,
            "before_model": before_model,
            "after_model": after_model,
            "before_distribution": before_distribution,
            "after_distribution": after_distribution,
            "removal_risk": removal_risk,
            "lateral_risk": lateral_risk,
            "overall_risk_level": overall_level,
            "replacement_beam": replacement_result,
        }

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
        barn_analysis=barn_analysis,
    )

    with tabs[6]:
        render_report_view(
            project_data=project_data,
            wall_data=wall_data,
            beam_data=beam_data,
            scenario_name=selected_scenario,
            risk=risk,
            material_df=material_df,
            disclaimer=DISCLAIMER,
            barn_analysis=barn_analysis,
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
