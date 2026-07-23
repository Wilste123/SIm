from __future__ import annotations

import streamlit as st


SCENARIO_OPTIONS = [
    "fjern innvendig bærevegg",
    "fjern stolpe",
    "fjern stolperekke",
    "lag større åpning i bærevegg",
    "erstatt med drager",
    "usikker / bare vurder konsekvens",
]

REPLACEMENT_OPTIONS = ["ingen", "limtredrager", "ståldrager", "trebjelke", "ny stolpe", "ukjent"]


def render_removal_scenario_inputs(support_options: list[dict]) -> dict:
    st.markdown("### Endringsscenario")
    scenario_name = st.selectbox("Velg scenario", SCENARIO_OPTIONS, index=0)

    support_names = [f"{item['navn']} ({item['id']})" for item in support_options]
    support_map = {f"{item['navn']} ({item['id']})": item["id"] for item in support_options}

    remove_support_ids: list[str] = []
    if support_names:
        selected_supports = st.multiselect("Velg bærende del(er) som fjernes", support_names)
        remove_support_ids = [support_map[label] for label in selected_supports]

    opening_length_m = 0.0
    if scenario_name in {"fjern innvendig bærevegg", "lag større åpning i bærevegg"}:
        opening_length_m = st.number_input("Åpningens lengde (m)", min_value=0.0, value=4.0, step=0.1)

    temporary_support_planned = st.checkbox("Midlertidig understøtting planlegges", value=True)
    proposed_replacement = st.selectbox("Foreslått erstatning", REPLACEMENT_OPTIONS, index=1)

    replacement_beam_span_m = 0.0
    dragerdimensjon = "48x198"
    materiale = "C24 tre"
    antall_understottelser = 2
    understottelse_plassering = "Begge ender"

    if scenario_name == "erstatt med drager" or proposed_replacement in {"limtredrager", "ståldrager", "trebjelke"}:
        r1, r2, r3 = st.columns(3)
        replacement_beam_span_m = r1.number_input("Spennvidde (m)", min_value=0.5, value=5.0, step=0.1)
        dragerdimensjon = r2.text_input("Dragerdimensjon", value="48x198")
        materiale = r3.selectbox("Materiale", ["C24 tre", "GL30 limtre", "S355 stål"], index=0)

        r4, r5 = st.columns(2)
        antall_understottelser = int(r4.number_input("Antall understøttelser", min_value=2, value=2, step=1))
        understottelse_plassering = r5.text_input("Plassering av understøttelser", value="Begge ender")

    notes = st.text_area("Notater", value="Forenklet konsekvensvurdering, bør kontrolleres faglig.", height=80)

    return {
        "scenario_name": scenario_name,
        "remove_support_ids": remove_support_ids,
        "proposed_replacement": proposed_replacement,
        "replacement_beam_span_m": replacement_beam_span_m,
        "temporary_support_needed": temporary_support_planned,
        "opening_length_m": opening_length_m,
        "dragerdimensjon": dragerdimensjon,
        "materiale": materiale,
        "antall_understottelser": antall_understottelser,
        "understottelse_plassering": understottelse_plassering,
        "notes": notes,
    }
