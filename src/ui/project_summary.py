from __future__ import annotations

from datetime import date

import streamlit as st

from src.data.standard_dimensions import BUILDING_TYPES


def render_project_form() -> dict:
    col1, col2 = st.columns(2)
    project_name = col1.text_input("Prosjektnavn", value="LåveSim-prosjekt")
    building_type = col2.selectbox("Bygningstype", BUILDING_TYPES, index=0)

    col3, col4 = st.columns(2)
    location = col3.text_input("Sted", value="")
    performed_by = col4.text_input("Utført av", value="William Berg Steffenak - copyright")

    col5, col6 = st.columns(2)
    project_date = col5.date_input("Dato", value=date.today())
    note = col6.text_area("Notat", value="", height=100)

    return {
        "project_name": project_name,
        "building_type": building_type,
        "location": location,
        "performed_by": performed_by,
        "project_date": project_date.isoformat(),
        "note": note,
    }


def render_project_summary(project_data: dict) -> None:
    st.markdown("### Prosjektoversikt")
    cols = st.columns(4)
    cols[0].metric("Prosjekt", project_data["project_name"] or "-")
    cols[1].metric("Type", project_data["building_type"])
    cols[2].metric("Sted", project_data["location"] or "-")
    cols[3].metric("Utført av", project_data["performed_by"])
    if project_data["note"]:
        st.info(project_data["note"])
