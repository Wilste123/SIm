from __future__ import annotations

import streamlit as st


def render_report_view(
    project_data: dict,
    wall_data: dict,
    beam_data: dict,
    scenario_name: str,
    risk: dict,
    material_df,
    disclaimer: str,
) -> None:
    st.markdown("### Rapportutkast")
    st.write(f"**Prosjekt:** {project_data['project_name']}")
    st.write(f"**Dato:** {project_data['project_date']}")
    st.write(f"**Utført av:** {project_data['performed_by']}")
    st.write(f"**Bygningstype:** {project_data['building_type']}")
    st.write(f"**Lastscenario:** {scenario_name}")
    st.write(f"**Risikovurdering:** {risk['title']} – {risk['message']}")
    st.markdown("#### Vegginput")
    st.json(wall_data)
    st.markdown("#### Bjelkeinput")
    st.json(beam_data)
    st.markdown("#### Materialliste")
    st.dataframe(material_df, use_container_width=True)
    st.warning(disclaimer, icon="⚠️")
    st.caption("PDF-eksport er TODO i første MVP.")
