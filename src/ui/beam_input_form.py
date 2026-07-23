from __future__ import annotations

import streamlit as st

from src.data.materials import MATERIAL_TYPES, WOOD_DIMENSIONS
from src.data.standard_dimensions import DEFLECTION_LIMITS


def render_beam_input_form() -> dict:
    col1, col2, col3 = st.columns(3)
    span_m = col1.number_input("Spennvidde (m)", min_value=0.5, value=3.6, step=0.1)
    beam_dimension = col2.selectbox("Bjelkedimensjon", list(WOOD_DIMENSIONS.keys()), index=4)
    material_type = col3.selectbox("Materialtype", list(MATERIAL_TYPES.keys()), index=0)

    col4, col5, col6 = st.columns(3)
    load_type = col4.selectbox("Lasttype", ["punktlast midt på", "jevnt fordelt last"], index=1)
    load_kg = col5.number_input("Last (kg)", min_value=0.0, value=250.0, step=10.0)
    load_kn_per_m = col6.number_input("Last (kN/m)", min_value=0.0, value=1.8, step=0.1)

    col7, col8, col9 = st.columns(3)
    beam_count = col7.number_input("Antall bjelker", min_value=1, value=1, step=1)
    center_spacing_mm = col8.number_input("Senteravstand (mm)", min_value=100, value=600, step=50)
    deflection_limit = col9.selectbox("Tillatt nedbøyningsgrense", DEFLECTION_LIMITS, index=1)

    return {
        "span_m": span_m,
        "beam_dimension": beam_dimension,
        "material_type": material_type,
        "load_type": load_type,
        "load_kg": load_kg,
        "load_kn_per_m": load_kn_per_m,
        "beam_count": int(beam_count),
        "center_spacing_mm": int(center_spacing_mm),
        "deflection_limit": deflection_limit,
    }
