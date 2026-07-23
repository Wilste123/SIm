from __future__ import annotations

import streamlit as st

from src.engine.element_selection import build_element_label, list_selectable_elements
from src.engine.structural_elements import BarnModel3D

ACTIONS = [
    "behold",
    "fjern",
    "forsterk",
    "erstatt med drager",
    "legg til søyle under",
    "marker som bærende",
    "marker som ikke-bærende",
]

DRAGER_MATERIALER = ["limtre", "stål", "konstruksjonsvirke", "ukjent"]


def render_element_selector_and_editor(model: BarnModel3D) -> dict:
    """Viser elementvelger og endringseditor.

    Returnerer dict med selected_element_id, action og replacement.
    """
    st.markdown("#### Velg element i modellen")

    selectable = list_selectable_elements(model)
    if not selectable:
        st.info("Ingen valgbare elementer i modellen.")
        return {"selected_element_id": None, "action": "behold", "replacement": {}}

    labels = [item["label"] for item in selectable]
    ids = [item["id"] for item in selectable]

    selected_idx = st.selectbox(
        "Velg element",
        range(len(labels)),
        format_func=lambda i: labels[i],
        key="3d_element_select",
    )

    selected_item = selectable[selected_idx]
    selected_id = ids[selected_idx]
    elem = selected_item["element"]

    # Vis detaljer
    with st.expander("Elementdetaljer", expanded=True):
        d1, d2, d3 = st.columns(3)
        d1.markdown(f"**Navn:** {elem.name}")
        d2.markdown(f"**Type:** {elem.element_type}")
        d3.markdown(f"**Materiale:** {elem.material}")

        d4, d5, d6 = st.columns(3)
        d4.markdown(f"**Bærende:** {'Ja' if elem.is_bearing else 'Nei'}")
        d5.markdown(f"**Bærer tak:** {'Ja' if elem.carries_roof else 'Nei'}")
        d6.markdown(f"**Bærer gulv:** {'Ja' if elem.carries_floor else 'Nei'}")

        d7, d8, d9 = st.columns(3)
        d7.markdown(f"**Horisontal avstivning:** {'Ja' if elem.provides_lateral_stability else 'Nei'}")
        d8.markdown(f"**Estimert last:** {elem.load_kn:.1f} kN")
        d9.markdown(f"**Status:** {elem.status}")

        if elem.connected_to:
            st.markdown(f"**Tilkoblede elementer:** {', '.join(elem.connected_to)}")

    action = st.selectbox(
        "Velg handling",
        ACTIONS,
        key="3d_action_select",
    )

    replacement: dict = {}

    if action == "erstatt med drager":
        st.markdown("##### Erstatningsdrager")
        r1, r2 = st.columns(2)
        drager_mat = r1.selectbox(
            "Drager-materiale", DRAGER_MATERIALER, key="3d_drager_mat"
        )
        spennvidde = r2.number_input(
            "Spennvidde (m)",
            min_value=0.5,
            value=max(elem.length, 1.0),
            step=0.1,
            key="3d_spenn",
        )
        r3, r4 = st.columns(2)
        drager_h = r3.number_input(
            "Dragerhøyde (mm)", min_value=50, value=300, step=10, key="3d_drager_h"
        )
        drager_b = r4.number_input(
            "Dragerbredde (mm)", min_value=45, value=90, step=5, key="3d_drager_b"
        )
        r5, r6 = st.columns(2)
        antall_underst = r5.number_input(
            "Antall understøttelser", min_value=0, value=2, step=1,
            key="3d_understottelser",
        )
        legg_til_soyle = r6.checkbox(
            "Legg til søyle under", value=False, key="3d_soyle_under"
        )
        replacement = {
            "drager_materiale": drager_mat,
            "spennvidde_m": spennvidde,
            "drager_hoyde_mm": drager_h,
            "drager_bredde_mm": drager_b,
            "antall_understottelser": antall_underst,
            "legg_til_soyle_under": legg_til_soyle,
        }

    return {
        "selected_element_id": selected_id,
        "action": action,
        "replacement": replacement,
    }
