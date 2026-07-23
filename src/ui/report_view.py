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
    barn_analysis: dict | None = None,
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

    if barn_analysis:
        st.markdown("#### Bæresystemanalyse")
        st.write("**Forenklet vurdering av total bæring, lastvei og konsekvens ved endring av bæresystem.**")
        st.write(f"**Bygningsmål:** {barn_analysis['building_input']}")
        st.write(f"**Antatte laster:** {barn_analysis['load_input']}")
        st.write(f"**Valgt endringsscenario:** {barn_analysis['scenario']['scenario_name']}")
        st.write(f"**Hva som fjernes:** {barn_analysis['scenario']['remove_support_ids']}")
        st.write(f"**Foreslått erstatning:** {barn_analysis['scenario']['proposed_replacement']}")
        st.write(f"**Før/etter-vurdering:** {barn_analysis['removal_risk']['summary']}")
        st.write("**Kritiske funn:**")
        for finding in barn_analysis["removal_risk"]["critical_findings"]:
            st.write(f"- {finding}")
        st.write("**Anbefalte tiltak:**")
        for recommendation in barn_analysis["removal_risk"]["recommendations"]:
            st.write(f"- {recommendation}")
        st.write(
            "**Midlertidig understøtting:** "
            + ("Bør brukes" if barn_analysis["removal_risk"]["requires_temporary_support"] else "Ikke tydelig indikert")
        )
        st.warning(barn_analysis["disclaimer"], icon="⚠️")

    st.markdown("#### Materialliste")
    st.dataframe(material_df, use_container_width=True)
    st.warning(disclaimer, icon="⚠️")
    st.caption("PDF-eksport er TODO i første MVP.")
