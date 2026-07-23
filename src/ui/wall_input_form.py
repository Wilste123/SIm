from __future__ import annotations

import streamlit as st

from src.data.standard_dimensions import STUD_DIMENSIONS, STUD_SPACING_OPTIONS


def render_wall_input_form() -> dict:
    st.markdown("### Vegg- og stendergenerator")
    col1, col2 = st.columns(2)
    wall_width_m = col1.number_input("Veggbredde (m)", min_value=1.0, value=4.8, step=0.1)
    wall_height_m = col2.number_input("Vegghøyde (m)", min_value=1.8, value=2.4, step=0.1)

    col3, col4, col5 = st.columns(3)
    stud_spacing_mm = col3.selectbox("Stenderavstand (mm)", STUD_SPACING_OPTIONS, index=2)
    stud_dimension = col4.selectbox("Stenderdimensjon", STUD_DIMENSIONS, index=3)
    top_plates = col5.number_input("Antall toppsviller", min_value=1, value=2, step=1)
    bottom_plates = st.number_input("Antall bunnsviller", min_value=1, value=1, step=1)

    has_door = st.checkbox("Veggen har døråpning", value=False)
    door_width_m = door_height_m = door_left_m = 0.0
    if has_door:
        d1, d2, d3 = st.columns(3)
        door_width_m = d1.number_input("Dørbredde (m)", min_value=0.5, value=1.0, step=0.1)
        door_height_m = d2.number_input("Dørhøyde (m)", min_value=1.8, value=2.1, step=0.1)
        door_left_m = d3.number_input("Dørplassering fra venstre (m)", min_value=0.0, value=0.6, step=0.1)

    has_window = st.checkbox("Veggen har vindu", value=True)
    window_width_m = window_height_m = window_left_m = window_bottom_m = 0.0
    if has_window:
        w1, w2, w3, w4 = st.columns(4)
        window_width_m = w1.number_input("Vindusbredde (m)", min_value=0.4, value=1.2, step=0.1)
        window_height_m = w2.number_input("Vindushøyde (m)", min_value=0.4, value=1.0, step=0.1)
        window_left_m = w3.number_input("Vindusplassering fra venstre (m)", min_value=0.0, value=2.4, step=0.1)
        window_bottom_m = w4.number_input("Vindusplassering fra gulv (m)", min_value=0.0, value=0.9, step=0.1)

    return {
        "wall_width_m": wall_width_m,
        "wall_height_m": wall_height_m,
        "stud_spacing_mm": int(stud_spacing_mm),
        "stud_dimension": stud_dimension,
        "top_plates": int(top_plates),
        "bottom_plates": int(bottom_plates),
        "has_door": has_door,
        "door_width_m": door_width_m,
        "door_height_m": door_height_m,
        "door_left_m": door_left_m,
        "has_window": has_window,
        "window_width_m": window_width_m,
        "window_height_m": window_height_m,
        "window_left_m": window_left_m,
        "window_bottom_m": window_bottom_m,
    }
